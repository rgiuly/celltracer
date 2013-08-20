#This software is Copyright 2012 The Regents of the University of California. All Rights Reserved.
#Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes for non-profit institutions, without fee, and without a written agreement is hereby granted, provided that the above copyright notice, this paragraph and the following three paragraphs appear in all copies.
#Permission to make commercial use of this software may be obtained by contacting:
#Technology Transfer Office
#9500 Gilman Drive, Mail Code 0910
#University of California
#La Jolla, CA 92093-0910
#(858) 534-5815
#invent@ucsd.edu
#This software program and documentation are copyrighted by The Regents of the University of California. The software program and documentation are supplied "as is", without any accompanying services from The Regents. The Regents does not warrant that the operation of the program will be uninterrupted or error-free. The end-user understands that the program was developed for research purposes and is advised not to rely exclusively on the program for any reason.
#IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO
#ANY PARTY FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR
#CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING
#OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION,
#EVEN IF THE UNIVERSITY OF CALIFORNIA HAS BEEN ADVISED OF
#THE POSSIBILITY OF SUCH DAMAGE. THE UNIVERSITY OF
#CALIFORNIA SPECIFICALLY DISCLAIMS ANY WARRANTIES,
#INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#THE SOFTWARE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO OBLIGATIONS TO
#PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR
#MODIFICATIONS.

# This module contains functions to support segmentation and the ComponentDetector class.
# The ComponentDetector class contains parameters for segmentation of biological objects
# and methods for running steps of the segmentation process.




import warnings
import numpy
from time import localtime, strftime
import pickle

import logging
from cytoseg_classify import *
from contour_list_classification import *

# Note: this is code run on a variety of systems. Checks for import errors are in place
# to make it easy to find issues with python module not being installed.

try:
    from contour_processing import ContourDetector
except ImportError:
    print "could not load: from contour_processing import ContourDetector"

try:
    import cv
except ImportError:
    print "could not load: import cv"

from fill import *

import globals
import default_path

# nolonger using mayavi2
if 0:
    print "loading enthought"
    try:
        from enthought.mayavi.scripts import mayavi2
    except ImportError:
        warnings.warn("enthought.mayavi.scripts module is not installed")

print "loading default path"
from default_path import *
print "loading accuracy"
from accuracy import *
print "loading contour_comparison"
from contour_comparison import *
print "loading label_identifier"
from label_identifier import *

from xml.dom.minidom import Document
#from pygraph import *
try:
    from pygraph.classes.graph import *
    import pygraph.algorithms.accessibility
    from graph import *
except ImportError:
    warnings.warn("pygraph module is not installed")
import os
import colorsys
import copy as copy_module

    
enablePathProbabilityFilter = True # use True for mitochondria



def deleteFiles(path):

    for file in os.listdir(path):
        fullFile = os.path.join(path, file)
        print "deleting", fullFile
        if os.path.isfile(fullFile):
            os.unlink(fullFile)


def mitochondriaProbability_old(features):
    """Simple naive bayes approach for finding mitochondria contours. Nolonger using this method"""

    amplitude = 1
    overlapValue = gaussian(1.0 - features['ellipseOverlap'], amplitude, 0.2)
    perimeterValue = gaussian(abs(250.0 - features['perimeter']), amplitude, 150)
    grayValueMatch = gaussian(abs(1 - features['averageGrayValue']), amplitude, 0.25)
    areaMatch = gaussian(abs(700 - math.sqrt(features['contourArea'])), amplitude, 500)
    return overlapValue * perimeterValue * grayValueMatch * areaMatch


def mitochondriaProbability(features):
    """Simple naive bayes approach for finding mitochondria contours. Nolonger using this method"""

    amplitude = 1
    overlapValue = gaussian(1.0 - features['ellipseOverlap'], amplitude, 0.2)
    perimeterValue = gaussian(abs(131.0 - features['perimeter']), amplitude, 75)
    grayValueMatch = gaussian(abs(1 - features['averageGrayValue']), amplitude, 0.25)
    areaMatch = gaussian(abs(635 - math.sqrt(features['contourArea'])), amplitude, 300)
    return overlapValue * perimeterValue * grayValueMatch * areaMatch * areaMatch


def mitochondria_newProbability(features):
    """Simple naive bayes approach for finding mitochondria contours. Nolonger using this method"""

    amplitude = 1
    overlapValue = gaussian(1.0 - features['ellipseOverlap'], amplitude, 0.2)
    perimeterValue = gaussian(abs(131.0 - features['perimeter']), amplitude, 75)
    #grayValueMatch = gaussian(abs(1 - features['averageGrayValue']), amplitude, 0.25)
    grayValueMatch = features['averageGrayValue']
    area = math.sqrt(features['contourArea']) / 635.0
    #return overlapValue * perimeterValue * grayValueMatch * area * area
    return grayValueMatch * area * area * area


def blankInnerCellProbability(features):
    """Simple naive bayes approach for finding inner cell contours. Nolonger using this method"""

    amplitude = 1
    overlapValue = gaussian(1.0 - features['ellipseOverlap'], amplitude, 0.2)
    perimeterValue = gaussian(abs(250.0 - features['perimeter']), amplitude, 150)
    grayValueMatch = gaussian(features['averageGrayValue'], amplitude, 0.25)
    areaMatch = gaussian(abs(700 - math.sqrt(features['contourArea'])), amplitude, 500)
    return overlapValue * perimeterValue * grayValueMatch * areaMatch


def vesicleProbability(features):
    """Simple naive bayes approach for finding vesicle contours. Nolonger using this method"""

    amplitude = 1
    overlapValue = gaussian(1.0 - features['ellipseOverlap'], amplitude, 0.2)
    perimeterValue = gaussian(abs(15 - features['perimeter']), amplitude, 5)
    grayValueMatch = gaussian(abs(0.5 - features['averageGrayValue']), amplitude, 0.5)
    areaMatch = gaussian(abs(70 - math.sqrt(features['contourArea'])), amplitude, 20)
    grayValueAtContourPointsMatch = gaussian(abs(160 - features['averageOriginalVolumeValueAtContourPoints']), amplitude, 160)
    return overlapValue * perimeterValue * grayValueMatch * areaMatch * grayValueAtContourPointsMatch


def updateContourProbabilities(contoursGroupedByImage, probabilityFunction):
    """Set probability that contour is salient based on a probability function."""

    contourList = nonnullObjects(contoursGroupedByImage)
    print "updateContourProbabilities"

    for contour in contourList:

        p = probabilityFunction(contour.features)
        contour.setProbability(p)
        print p

        if p < 0:
            limitedProbability = 0
        elif p > 1:
            limitedProbability = 1
        else:
            limitedProbability = p

        color = 255.0 * array(((1.0 - limitedProbability) * 10.0,
                               (limitedProbability * 10.0),
                               0))
        if 1:
            contour.setColor(color)





#@mayavi2.standalone
def display3DContours(dataViewer, inputVolumeName, highProbabilityContoursNodeName, displayParameters):
    """Deprecated. Shows contours in mayavi2."""

    numberOfContoursToDisplay = displayParameters.numberOfContoursToDisplay

    from enthought.mayavi.sources.array_source import ArraySource
    from enthought.mayavi.modules.outline import Outline
    from enthought.mayavi.modules.image_plane_widget import ImagePlaneWidget
    from enthought.mayavi.modules.iso_surface import IsoSurface
    
    # 'mayavi' is always defined on the interpreter.
    #mayavi.new_scene()
    from enthought.mayavi.api import Engine
    e = Engine()
    e.start()
    s = e.new_scene()

    # Make the data and add it to the pipeline.
    # todo: load this from the data tree of cytoseg
    #originalVolume = loadImageStack(driveName + "/images/HPFcere_vol/HPF_rotated_tif/median_then_gaussian_8bit", None)
    originalVolume = dataViewer.getPersistentVolume_old(inputVolumeName)
    #originalVolume = loadImageStack("O:/images/3D-blob-data/small_crop", None)
    #originalVolume = originalVolume[:,:,3:]

    data1 = array(originalVolume, dtype=float)
    data = numpy.transpose(data1).copy()
    data.shape = data.shape[::-1]

    src = ArraySource(transpose_input_array=False)
    src.scalar_data = data
    e.add_source(src)
    # Visualize the data.
    #o = Outline()
    #mayavi.add_module(o)
    ipw = ImagePlaneWidget()
    e.add_module(ipw)
    ipw.module_manager.scalar_lut_manager.show_scalar_bar = True

    ipw_y = ImagePlaneWidget()
    e.add_module(ipw_y)
    ipw_y.ipw.plane_orientation = 'y_axes'

    ipw_z = ImagePlaneWidget()
    e.add_module(ipw_z)
    ipw_z.ipw.plane_orientation = 'z_axes'

    # Enthought library imports
    
    #import enthought
    from enthought.mayavi import mlab as enthought_mlab
        
    from enthought.mayavi.scripts import mayavi2
    
    from enthought.mayavi import mlab as enthought_mlab

    import enthought.mayavi
    
    #mayavi.new_scene()
    #ball = enthought_mlab.points3d(1, 1, 1, scale_factor=16, scale_mode='none', resolution=20, color=(1,0,0), name='ball')

    
    node = dataViewer.mainDoc.dataTree.getSubtree((highProbabilityContoursNodeName,))
    #frm.refreshTreeControls()
    #contours = node.makeChildrenObjectList()

    #highProbabilityContourList = highProbabilityContours(contours)
    contourList = node.makeChildrenObjectList()
    #for contour in contours[0:2000:10]:

    #if numberOfContoursToDisplay != None:
    #    highProbabilityContourList = highProbabilityContourList[0:numberOfContoursToDisplay]

    for contour in contourList[:numberOfContoursToDisplay]:
        print "process contour"
        x = []
        y = []
        z = []
        for point in contour.points():
            x.append(point.loc[0])
            y.append(point.loc[1])
            z.append(point.loc[2])

        mitochondriaLikeness = contour.probability()
        #enthought_mlab.plot3d(x, y, z, tube_radius=1, color=(.1, mitochondriaLikeness*2.0, 0))
        enthought_mlab.plot3d(x, y, z, tube_radius=displayParameters.contourSegmentTubeRadius, color=(.1, mitochondriaLikeness, 0))
        #draw a sphere at contour.bestFitEllipse.center
        center = contour.bestFitEllipse.center
        # points3d requires lists of length 2 or more with distinct numbers in them for the first 4 arguments, that's why zeros are used, this may be a bug in the points3d function that i'm working around with the zeros
        enthought_mlab.points3d((0, center[0]), (0, center[1]), (0, center[2]), (0, 1), colormap="copper", scale_factor=displayParameters.contourCenterMarkerSize)
        
    print "finished sending contours to mayavi"

    #enthought_mlab.contour3d(data, contours=3)
    #enthought_mlab.contour3d(originalVolume, contours=3)


class ContourAndBlobDisplayParameters:

    def __init__(self):
        self.numberOfContoursToDisplay = None
        self.contourSegmentTubeRadius = 1
        self.contourCenterMarkerSize = 5
        self.enable3DPlot = True
        self.contourProbabilityThreshold = 0


def saveBlobsToJinxFile(node, filename):
    """Saves blobs to Jinx format. Nolonger using this.
    filename: filename (without a path or an extension)"""

    doc = Document()
    #blobsNode = gui.mainDoc.dataTree.getSubtree(('Blobs',))
    main = doc.createElement("main")
    doc.appendChild(main)

    saveBlobsToJinxFileRecursiveHelper(node, doc, main)

    file = open(os.path.join(defaultOutputPath, filename + ".xml"), "w")
    file.write(doc.toprettyxml(indent="   "))


def saveBlobsToJinxFileRecursiveHelper(node, document, documentElement):

    if node.isGroupNode:
        for childNode in node.children:
            saveBlobsToJinxFileRecursiveHelper(childNode, document, documentElement)
    else:
        documentElement.appendChild(
            node.object.getXMLObject(document, node.name))



class ComponentDetector:
    """Class contains methods for running various steps of the segmentation process."""

    def __init__(self,
                 dataViewer,
                 dataIdentifier,
                 target,
                 originalImageFilePath,
                 contourListClassificationMethod,
                 contourListExamplesIdentifier, # file to write to
                 contourListTrainingExamplesIdentifier, # file to read from
                 voxelTrainingImageFilePath=None,
                 voxelTrainingLabelFilePath=None,
                 labelFilePaths=None,
                 voxelClassificationIteration=0):
        """
        parameters for __init___:
        dataViewer: contains image and contour data associated with the segmentation process
        dataIdentifier: string to identify the data
        target: name of target biological component to be segmented
        originalImageFilePath: path to the original image that is to be processed
        contourListClassificationMethod: method for contour classification
        contourListExamplesIdentifier: features from detected contours go in file named by this identifier
        contourListTrainingExamplesIdentifier: the classifier is generated based items in the file named by this identifier
        voxelTrainingImageFilePath: path to training data images
        voxelTrainingLabelFilePath: path to training data segmentation
        labelFilePaths: deprecated
        voxelClassificationIteration: used only for series runs will multiple iterations
        """

        #self.app = wx.PySimpleApp()
        #self.dataViewer = ClassificationControlsFrame(makeClassifyGUITree())
        #self.dataViewer.Show()

        self.dataViewer = dataViewer

        self.dataIdentifier = dataIdentifier
        self.target = target
        self.highProbabilityContoursBaseFilename =\
            self.dataIdentifier + "_" + self.target

        self.originalImageFilePath = originalImageFilePath

        self.originalVolumeName = dataIdentifier + 'OriginalVolume'
        self.contourProcessingTrainingVolumeNodePath = ('Volumes',
                        dataIdentifier + 'ContourProcessingTrainingVolume')
        self.contourProcessingInputVolumeNodePath = ('Volumes',
                        dataIdentifier + 'ContourProcessingInputVolume')
        self.voxelClassificationInputVolumeName = self.originalVolumeName
        self.blurredVolumeName = dataIdentifier + 'BlurredVolume'
        self._voxelClassificationIteration = voxelClassificationIteration



        # this is for old accuracy check
        self.fullManualSegNodePath =\
            ('Volumes', dataIdentifier + 'FullManualSeg')

        self.trainingProbabilityMapNodePath =\
            ('Volumes', dataIdentifier + 'TrainingProbabilityMap')

        self.inputProbabilityMapNodePath =\
            ('Volumes', dataIdentifier + 'InputProbabilityMap')

        self.voxelTrainingImageFilePath = voxelTrainingImageFilePath
        self.voxelTrainingLabelFilePath = voxelTrainingLabelFilePath

        self.contourListClassificationMethod = contourListClassificationMethod

        trainingContoursNodeName = dataIdentifier + '_' + self.target + 'TrainingContours'
        inputContoursNodeName = dataIdentifier + '_' + self.target + 'InputContours'

        # currently, these nodes havee to be at the top level of the tree
        self.trainingContoursNodePath = (trainingContoursNodeName,)
        self.inputContoursNodePath = (inputContoursNodeName,)

        self.trainingContourListsNodePath = (dataIdentifier + '_' + self.target + 'TrainingContourLists',)
        self.inputContourListsNodePath = (dataIdentifier + '_' + self.target + 'InputContourLists',)

        if contourListExamplesIdentifier != None:
            self.contourListExamplesIdentifier = contourListExamplesIdentifier +\
                                                '_' + self.target
        self.contourListTrainingExamplesIdentifier =\
            contourListTrainingExamplesIdentifier +\
            '_' + self.target
        self.contourListInputDataExamplesIdentifier = 'InputDataExamples' +\
                                                '_' + self.target
        self.labelFilePaths = labelFilePaths

        self.fullManualSegFilePath = None

        self.numberOfTrainingLayersToProcess = None

        self.numberOfLayersToProcess = None
        self.trainingRegion = None
        self.regionToClassify = None
        self.numberOfThresholds = 1
        self.firstThreshold = 0.5
        self.thresholdStep = 0.1

        self.contourProcessingTrainingRegion = None
        self.contourProcessingRegionToClassify = None

        self.accuracyCalcRegion = None

        #self.minVoxelLabelValue = 1
        #self.maxVoxelLabelValue = None

        self.displayParametersDict = {}
        self.displayParametersDict['primaryObject'] = ContourAndBlobDisplayParameters()
        self.displayParametersDict['primaryObject'].numberOfContoursToDisplay = None #20
        self.displayParametersDict['primaryObject'].contourProbabilityThreshold = 0.08
        self.displayParametersDict['mitochondria_new'] = ContourAndBlobDisplayParameters()
        self.displayParametersDict['mitochondria_new'].numberOfContoursToDisplay = None #20
        self.displayParametersDict['mitochondria_new'].contourProbabilityThreshold = 0.0
        self.displayParametersDict['blankInnerCell'] = ContourAndBlobDisplayParameters()
        self.displayParametersDict['blankInnerCell'].numberOfContoursToDisplay = 20
        self.displayParametersDict['blankInnerCell'].contourProbabilityThreshold = 0 #0.1
        self.displayParametersDict['vesicles'] = ContourAndBlobDisplayParameters()
        self.displayParametersDict['vesicles'].numberOfContoursToDisplay = 5 #500 #5 #20
        self.displayParametersDict['vesicles'].contourSegmentTubeRadius = 0.1
        self.displayParametersDict['vesicles'].contourCenterMarkerSize = 0.5
        self.displayParametersDict['vesicles'].contourProbabilityThreshold = 0.15

        self.probabilityFunctionDict = {}
        self.probabilityFunctionDict['primaryObject'] = mitochondriaProbability
        self.probabilityFunctionDict['mitochondria_new'] =\
            mitochondria_newProbability
        self.probabilityFunctionDict['vesicles'] = vesicleProbability
        self.probabilityFunctionDict['blankInnerCell'] = blankInnerCellProbability
        self.probabilityFunctionDict['membranes'] = blankInnerCellProbability
        self.probabilityFunctionDict['membranes_test'] = blankInnerCellProbability
        self.pathLength = {}
        self.pathLength['primaryObject'] = 3
        self.pathLength['mitochondria_new'] = 2
        #self.pathLength['mitochondria_new'] = 3
        self.pathLength['vesicles'] = 1
        self.pathLength['blankInnerCell'] = 1
        print "path length", self.pathLength
        self.enable3DPlot = False
        #numberOfLayersToProcess = 7


        self.labelIdentifierDict = LabelIdentifierDict()





    def voxelTrainingClassificationResultPath(self, iteration):
        """
        Create node path that identifies the volume generated by classification of training data.
        This is a node path that identifies a node in the tree that stores data for cytoseg.
        """

        return ('Volumes', self.dataIdentifier + 'VoxelTrainingClassificationResult'
                + '_' + str(iteration))


    def voxelClassificationResultPath(self, iteration):
        """
        Create node path that identifies the volume generated by classification of input data.
        This is a node path that identifies a node in the tree that stores data for cytoseg.
        """

        return ('Volumes', self.dataIdentifier + 'VoxelClassificationResult'
                + '_' + str(iteration))


    def currentVoxelTrainingClassificationResultPath(self):
        """When process is run with series architecture, this identifies the current output for classification of training data."""

        return self.voxelTrainingClassificationResultPath(
                                    self._voxelClassificationIteration)


    def currentVoxelClassificationResultPath(self):
        """When process is run with series architecture, this identifies the current output for classification of input data."""

        return self.voxelClassificationResultPath(self._voxelClassificationIteration)


    def previousVoxelTrainingClassificationResultPath(self):
        """When process is run with series architecture, this ideentifies the previous output for classification of training data."""

        return self.voxelTrainingClassificationResultPath(
                                    self._voxelClassificationIteration - 1)


    def previousVoxelClassificationResultPath(self):
        """When process is run with series architecture, this identifies the previous output for classification of input data."""

        return self.voxelClassificationResultPath(self._voxelClassificationIteration - 1)




    def unfilteredContourOutputPath(self):
        """This node path identifies the node with all contours in it.
        For this, contours are not filtered by classification probability."""

        numContours = self.pathLength[self.target]
        return os.path.join(default_path.defaultOutputPath, "unfilteredContourOutput_numContours=%02d" % numContours)


    def highProbabilityContourOutputPath(self):
        """This node path identifies the node with only high probability contours in it.
        For this, contours are filtered by classification probability."""

        numContours = self.pathLength[self.target]
        return os.path.join(default_path.defaultOutputPath, "contourOutput_numContours=%02d" % numContours)


    def writeContoursToImageStack(self, pathToContoursNode):
        """
        Renders contours into an image stack for viewing.
        Parameters:
        pathToContoursNode: identifies a group of contours are stored in a tree to be viewed
        """

        print "writing contours to image stack", defaultOutputPath

        #contoursNode = frm.mainDoc.dataTree.getSubtree((highProbabilityContoursNodeName,))
        #contoursNode = frm.mainDoc.dataTree.getSubtree((contoursNodeName,))
        contoursNode = self.dataViewer.mainDoc.dataTree.getSubtree(pathToContoursNode)
        originalVolume = self.dataViewer.getPersistentObject(self.contourProcessingInputVolumeNodePath)
        contourRenderingVolume = zeros(originalVolume.shape)
        contourProbabilityVolume = zeros(originalVolume.shape)
        tempVolume = array(originalVolume)

        print "rendering filled contours"
        #self.dataViewer.renderPointSetsInVolumeRecursive(contourRenderingVolume,
        #                                                 contoursNode,
        #                                                 probabilityThreshold=0)
        self.dataViewer.renderPointSetsInVolumeRecursive(contourProbabilityVolume,
                                                         contoursNode,
                                                         valueMode='probability',
                                                         probabilityThreshold=0.09)
        #self.dataViewer.renderPointSetsInVolumeRecursive(tempVolume, contoursNode,
        #                                                 probabilityThreshold=0)
        self.dataViewer.addVolume(contourRenderingVolume, 'ContourVolume')
        self.dataViewer.refreshTreeControls()
        writeStackRGB(defaultOutputPath,
                          redVolume=contourRenderingVolume,
                          greenVolume=contourProbabilityVolume*0.4,
                          blueVolume=tempVolume)


    def writeContoursToBinaryImageStack_old(self, pathToContoursNode):
        """Deprecated"""

        print "writing contours to image stack", defaultOutputPath

        #contoursNode = frm.mainDoc.dataTree.getSubtree((highProbabilityContoursNodeName,))
        #contoursNode = frm.mainDoc.dataTree.getSubtree((contoursNodeName,))
        contoursNode = self.dataViewer.mainDoc.dataTree.getSubtree(pathToContoursNode)
        originalVolume = self.dataViewer.getPersistentObject(self.contourProcessingInputVolumeNodePath)
        #contourRenderingVolume = zeros(originalVolume.shape)
        contourProbabilityVolume = zeros(originalVolume.shape)
        #tempVolume = array(originalVolume)

        print "rendering filled contours"
        #self.dataViewer.renderPointSetsInVolumeRecursive(contourRenderingVolume,
        #                                                 contoursNode,
        #                                                 probabilityThreshold=0)
        self.dataViewer.renderPointSetsInVolumeRecursive(contourProbabilityVolume,
                                                         contoursNode,
                                                         valueMode='probability',
                                                         probabilityThreshold=0.09)
        #self.dataViewer.renderPointSetsInVolumeRecursive(tempVolume, contoursNode,
        #                                                 probabilityThreshold=0)
        #self.dataViewer.addVolume(contourRenderingVolume, 'ContourVolume')
        self.dataViewer.refreshTreeControls()
        writeStackRGB(defaultOutputPath,
                          redVolume=contourProbabilityVolume*0.4,
                          greenVolume=contourProbabilityVolume*0.4,
                          blueVolume=contourProbabilityVolume*0.4)


    # writes composite and single channel images
    def writeContoursToBinaryImageStack(self, pathToContoursNode, filePath,
                                        probabilityThreshold):
        """Write filled contours to black and while image stack."""

        print "writing contours to image stack", filePath

        contoursNode = self.dataViewer.mainDoc.dataTree.getSubtree(pathToContoursNode)
        originalVolume = self.dataViewer.getPersistentObject(self.contourProcessingInputVolumeNodePath)
        contourProbabilityVolume = zeros(originalVolume.shape)

        print "rendering filled contours"
        self.dataViewer.renderPointSetsInVolumeRecursive(contourProbabilityVolume,
                                contoursNode,
                                valueMode='probability',
                                probabilityThreshold=probabilityThreshold)
        self.dataViewer.refreshTreeControls()
        volume = contourProbabilityVolume * 0.4

        b = copy_module.deepcopy(borderWidthForFeatures)
        b[2] = 0

        self.writeVolumeResult(filePath, originalVolume, volume,
                               self.contourProcessingRegionToClassify, b)


    # todo: numberOfLayersToProcess parameter redundant
    def preclassificationFilter(self, dataViewer, numberOfLayersToProcess=None):
        """Applies optional filtering to the originalImage to produce blurredImage. Performed before patch classification."""

        # todo: use runLoadOriginalImage to do this
        #originalImageNodePath = ('Volumes', 'originalImage')
        originalImageNodePath = ('Volumes', self.originalVolumeName)

        originalImage = loadImageStack(self.originalImageFilePath, None)

        originalImage = originalImage[:, :, 0:self.numberOfLayersToProcess]

        # this might be redundant
        dataViewer.addVolumeAndRefreshDataTree(originalImage, originalImageNodePath[1])

        print "starting itk filtering"
        medianFilteredImage = itkFilter(originalImage, 'Median', radius=1)
        blurredImage = itkFilter(medianFilteredImage, 'SmoothingRecursiveGaussian', sigma=1)
        print "itk filtering complete"

        dataViewer.addPersistentVolumeAndRefreshDataTree(originalImage,
                                                         self.originalVolumeName)

        dataViewer.addPersistentVolumeAndRefreshDataTree(blurredImage,
                                                         self.blurredVolumeName)


    def classifyVoxels_old(self, dataViewer, numberOfLayersToProcess=None,
                           minLabelValue=1, maxLabelValue=None):
        """Deprecated"""

        inputVolumeDict = odict()
        originalImageNodePath = ('Volumes', 'originalImage')
        inputVolumeDict['originalVolume'] =\
            self.dataViewer.getPersistentObject(originalImageNodePath)
        if self._voxelClassificationIteration > 0:
            inputVolumeDict['previousResult'] =\
                self.dataViewer.getPersistentObject(
                    self.previousVoxelClassificationResultPath)

        # inputVolumeName = self.blurredVolumeName for sfn2009 results
        
        #inputImageFilePath =\
        #    driveName + "/images/HPFcere_vol/HPF_rotated_tif/median_then_gaussian_8bit"
        exampleListFileName = os.path.join(cytosegDataFolder, "exampleList.tab")
        
        voxelTrainingImageNodePath = ('Volumes', 'voxelTrainingImage')
        voxelTrainingLabelNodePath = ('Volumes', 'voxelTrainingLabel')
        inputImageNodePath = ('Volumes', 'inputImage')
    
        # load training images
        dataViewer.addVolumeAndRefreshDataTree(
            loadImageStack(self.voxelTrainingImageFilePath,
                           None,
                           maxNumberOfImages=self.numberOfTrainingLayersToProcess),
            voxelTrainingImageNodePath[1])
    
        inputTrainingVolumeDict = odict()
        inputTrainingVolumeDict['originalVolume'] =\
            self.dataViewer.getPersistentObject(voxelTrainingImageNodePath)
        if self._voxelClassificationIteration > 0:
            inputTrainingVolumeDict['previousResult'] =\
                self.dataViewer.getPersistentObject(
                    self.previousVoxelTrainingClassificationResultPath)

        # load training labels
        rawLabelVolume = loadImageStack(self.voxelTrainingLabelFilePath,
                            None,
                            maxNumberOfImages=self.numberOfTrainingLayersToProcess)

        # open input image data to be classified
        #inputImage = self.dataViewer.getPersistentVolume_old(self.blurredVolumeName)
        inputImage = self.dataViewer.getPersistentVolume_old(
                                                    self.voxelClassificationInputVolumeName)
        # crop input image data if specified
        if numberOfLayersToProcess != None:
            inputImage = inputImage[:, :, 0:numberOfLayersToProcess]

        if maxLabelValue == None:
            labelVolume = rawLabelVolume >= minLabelValue
        else:
            labelVolume =\
                logical_and(minLabelValue <= rawLabelVolume,
                            rawLabelVolume <= maxLabelValue)

        dataViewer.addVolumeAndRefreshDataTree(labelVolume, voxelTrainingLabelNodePath[1])
        
        #inputImage = loadImageStack(inputImageFilePath, None)
        
        dataViewer.addVolumeAndRefreshDataTree(inputImage, inputImageNodePath[1])
    
        if self.voxelClassificationMethod == 'randomForest':

            # uses training data
            print "learning features of training data"
            dataViewer.learnFeaturesOfMembraneVoxels(inputTrainingVolumeDict,
                                                     voxelTrainingImageNodePath,
                                                     voxelTrainingLabelNodePath,
                                                     exampleListFileName)
        
            # uses training data, generates voxel probabilities
            print "classifying training set voxels"
            dataViewer.classifyVoxels('intermediateTrainingDataLabel1',
                               self.currentVoxelTrainingClassificationResultPath(),
                               exampleListFileName,
                               inputTrainingVolumeDict,
                               voxelTrainingImageNodePath)

            # uses test data, generates voxel probabilities
            print "classifying voxels"
            dataViewer.classifyVoxels('intermediateTestDataLabel1',
                               self.currentVoxelClassificationResultPath(),
                               exampleListFileName,
                               inputVolumeDict,
                               inputImageNodePath)

        elif self.voxelClassificationMethod == 'neuralNetwork':

            #dataViewer.learnFeaturesOfMembraneVoxels(voxelTrainingImageNodePath,
            #                                  voxelTrainingLabelNodePath,
            #                                  exampleListFileName)

            dataViewer.classifyVoxelsNN('intermediateDataLabel1',
                               self.currentVoxelClassificationResultPath()[1],
                               exampleListFileName,
                               inputImageNodePath)


    def classifyVoxels(self, dataViewer, numberOfLayersToProcess=None):
        """Train then classify voxels.
        dataView contains input and output.
        numberOfLayersToProcess limits the number of layers if it is set to a number. The default Node includes all layers.
        Results are placed at this node self.currentVoxelClassificationResultPath()"""

        inputVolumeDict = odict()
        #originalImageNodePath = ('Volumes', 'originalImage')
        originalImageNodePath = ('Volumes', self.originalVolumeName)
        inputVolumeDict['originalVolume'] =\
            self.dataViewer.getPersistentObject(originalImageNodePath)
        if self._voxelClassificationIteration > 0:
            resultsNode = self.dataViewer.mainDoc.dataTree.getSubtree(
                            self.previousVoxelClassificationResultPath())
            #resultsNode = getNode(self.dataViewer.mainDoc.dataRootNode,
            #                self.previousVoxelClassificationResultPath)
            for childNode in resultsNode.children:
                inputVolumeDict['previousResult_' + childNode.name] = childNode.object

        exampleListFileName = os.path.join(default_path.cytosegDataFolder, "exampleList.tab")
        
        voxelTrainingImageNodePath = ('Volumes', 'voxelTrainingImage')
        voxelTrainingLabelNodePath = ('Volumes', 'voxelTrainingLabel')
        inputImageNodePath = ('Volumes', 'inputImage')
    
    
        inputTrainingVolumeDict = odict()
        inputTrainingVolumeDict['originalVolume'] =\
            self.dataViewer.getPersistentObject(voxelTrainingImageNodePath)
        if self._voxelClassificationIteration > 0:

            resultsNode = self.dataViewer.mainDoc.dataTree.getSubtree(
                            self.previousVoxelTrainingClassificationResultPath())

            for childNode in resultsNode.children:
                inputTrainingVolumeDict['previousResult_' + childNode.name] =\
                    childNode.object


        # open input image data to be classified
        #inputImage = self.dataViewer.getPersistentVolume_old(self.blurredVolumeName)
        inputImage = self.dataViewer.getPersistentVolume_old(
                                                    self.voxelClassificationInputVolumeName)
        # crop input image data if specified
        if numberOfLayersToProcess != None:
            inputImage = inputImage[:, :, 0:numberOfLayersToProcess]


        dataViewer.addVolumeAndRefreshDataTree(inputImage, inputImageNodePath[1])


        if self.voxelClassificationMethod == 'randomForest':

            ###############################################################
            # Training with random forest
            # uses training data
            logging.info("recording features of training data")
            print "recordLocalFeatures"
            dataViewer.recordLocalFeatures(inputTrainingVolumeDict,
                                           self.labelIdentifierDict,
                                           voxelTrainingImageNodePath,
                                           voxelTrainingLabelNodePath,
                                           exampleListFileName,
                                           self.voxelWeightDict)
            logging.info("finished recording features of training data")
        
            if 0:
                # Used for serial iterations
                print "Classifying training set voxels"
                dataViewer.classifyVoxels('intermediateTrainingDataLabel1',
                                   self.currentVoxelTrainingClassificationResultPath(),
                                   exampleListFileName,
                                   inputTrainingVolumeDict,
                                   voxelTrainingImageNodePath)
            else:
                print "Classification of training data disabled. Serial iterations will not be supported."

            ###############################################################
            # Classification step with random forest
            # reads test data, generates voxel probabilities
            print "classifying voxels"
            print "volume shapes"
            for item in inputVolumeDict.items():
                key = item[0]
                print key, inputVolumeDict[key].shape
            dataViewer.classifyVoxels('intermediateTestDataLabel1',
                               self.currentVoxelClassificationResultPath(),
                               exampleListFileName,
                               inputVolumeDict,
                               inputImageNodePath)

        # Neural network option, currently not used
        elif self.voxelClassificationMethod == 'neuralNetwork':

            dataViewer.classifyVoxelsNN('intermediateDataLabel1',
                               self.currentVoxelClassificationResultPath()[1],
                               exampleListFileName,
                               inputImageNodePath)



    def runRadonLikeFeaturesProcess(self):
        """Executes matlab code to extract radon like features"""

        inputImage = self.dataViewer.getPersistentVolume_old(
                                            self.voxelClassificationInputVolumeName)

        tempInputPath = os.path.join(self.blobImageStackOutputFolder, 'tempInput')
        tempOutputPath = os.path.join(self.blobImageStackOutputFolder, 'tempOutput')
        outputPath = os.path.join(self.blobImageStackOutputFolder, 'radonOutput')

        for path in (tempInputPath, tempOutputPath, outputPath):
            if not(os.path.exists(path)):
                os.mkdir(path)

        # delete any old files in input folder
        deleteFiles(tempInputPath)


        print "writing input image to", tempInputPath
        writeStack(tempInputPath, inputImage)

        import subprocess
        command = ["C:\\Program Files\\MATLAB\\R2009a\\bin\\matlab.exe", "-nodesktop", "-wait", "-r", "cd c:\\;cd eclipse_workspace;cd blobcenter;cd cytoseg;cd radonLikeFeatures;radonLikeProcessStack('%s', '%s');exit" % (tempInputPath, tempOutputPath)]
        print command

        if 1:
            deleteFiles(tempOutputPath)
            errorValue = subprocess.call(command)
    
            if errorValue != 0:
                raise Exception("matlab command didn't work")

        # open stack in tempOutput folder as outputImage
        outputImage = loadImageStack(tempOutputPath, None)

        print "writing output image to", outputPath
        self.writeVolumeResult(outputPath,
                                outputImage / 255.0,
                                outputImage / 255.0,
                                self.regionToClassify,
                                [0, 0, 0])


    def findContours(self, contoursNodePath,
                        originalVolumeNodePath,
                        probabilityMapNodePath,
                        groupNodeName,
                        threshold,
                        numberOfLayersToProcess):
            """
            Use ContourDetector object to find isocontours in the probability map.
            Contours results are placed in the contoursGroupedByImage node
            parameters:
            contoursNodePath: identifies the node under which sets of contours are placed
            originalVolumeNodePath: identifies the node where the original 3D image is stored
            probabiliyMapNodePath: identifies the node where the probability map 3D image is stored (the result of voxel classification)
            groupNodeName: name of the new node with the contours detected in this step. The node is placed under the node that contoursNodePath identifies
            threshold: threshold to apply to the image before detecting contours
            numberOfLayersToProcess: limit on the number of layers to process. (This should be set to None to process all layers.)
            """

            originalVolume =\
                self.dataViewer.getPersistentObject(originalVolumeNodePath)


            originalVolumeShape = originalVolume.shape

            detector = ContourDetector((originalVolumeShape[0], originalVolumeShape[1]))
            detector.threshold = threshold
            detector.probabilityFunction = self.probabilityFunctionDict[self.target]

    
            if (self.target == 'primaryObject') or (self.target == 'blankInnerCell'):

                if numberOfLayersToProcess != None:
                    detector.originalVolume = self.dataViewer.getPersistentVolume_old(self.blurredVolumeName)\
                    [:, :, 0:numberOfLayersToProcess]
                    detector.filteredVolume = self.dataViewer.getPersistentVolume_old(self.currentVoxelClassificationResultPath()[1])\
                    [:, :, 0:numberOfLayersToProcess]
                else:
                    detector.originalVolume = self.dataViewer.getPersistentVolume_old(self.blurredVolumeName)
                    detector.filteredVolume = self.dataViewer.getPersistentVolume_old(self.currentVoxelClassificationResultPath()[1])
    
                #detector.originalVolume = frm.getPersistentVolume_old(blurredVolumeName)
                if self.target == 'primaryObject':
                    #detector.probabilityFunction = mitochondriaProbability
                    detector.filteredVolume = filterVolume2D(detector.filteredVolume,
                                                            'GrayscaleErode', kernelSize=4)
                elif self.target == 'blankInnerCell':
                    #detector.probabilityFunction = blankInnerCellProbability
                    detector.filteredVolume = filterVolume2D(detector.filteredVolume,
                                                             'GrayscaleDilate',
                                                             kernelSize=4)
                else:
                    raise Exception, "Invalid target"
                #detector.filteredVolume = frm.getPersistentVolume_old(filteredVolumeName)
    
            elif self.target == 'vesicles':
            
                #detector = ContourDetector()
                fullVolume = self.dataViewer.getPersistentVolume_old(self.originalVolumeName)
    
                if numberOfLayersToProcess != None:
                    detector.originalVolume = fullVolume[:, :, 0:numberOfLayersToProcess]
                else:
                    detector.originalVolume = fullVolume
    
                #detector.probabilityFunction = vesicleProbability
                detector.contourFilterFunction2D = greaterThanSurroundingPixelsFilter
                detector.minPerimeter = 1
                detector.maxPerimeter = 50

            elif self.target == 'membranes':

                if numberOfLayersToProcess != None:
                    detector.originalVolume = self.dataViewer.getPersistentVolume_old(self.originalVolumeName)\
                    [:, :, 0:numberOfLayersToProcess]
                    detector.filteredVolume = self.dataViewer.getPersistentVolume_old(self.currentVoxelClassificationResultPath()[1])\
                    [:, :, 0:numberOfLayersToProcess]
                else:
                    detector.originalVolume = self.dataViewer.getPersistentVolume_old(self.originalVolumeName)
                    detector.filteredVolume = self.dataViewer.getPersistentVolume_old(self.currentVoxelClassificationResultPath()[1])

            elif self.target == 'membranes_test':
            
                if numberOfLayersToProcess != None:
                    detector.originalVolume = self.dataViewer.getPersistentVolume_old(self.originalVolumeName)\
                    [:, :, 0:numberOfLayersToProcess]
                    detector.filteredVolume = self.dataViewer.getPersistentVolume_old(self.originalVolumeName)\
                    [:, :, 0:numberOfLayersToProcess]
                else:
                    detector.originalVolume = self.dataViewer.getPersistentVolume_old(self.originalVolumeName)
                    detector.filteredVolume = self.dataViewer.getPersistentVolume_old(self.originalVolumeName)

            elif self.target == 'mitochondria_new':
            
                detector.retrievalMode = cv.CV_RETR_EXTERNAL
                detector.minPerimeter = 60
                detector.maxPerimeter = 600

                if numberOfLayersToProcess != None:
                    detector.originalVolume = self.dataViewer.getPersistentObject(originalVolumeNodePath)\
                    [:, :, 0:numberOfLayersToProcess]
                    detector.filteredVolume = self.dataViewer.getPersistentObject(probabilityMapNodePath)\
                    [:, :, 0:numberOfLayersToProcess]
                else:
                    detector.originalVolume = self.dataViewer.getPersistentObject(originalVolumeNodePath)
                    detector.filteredVolume = self.dataViewer.getPersistentObject(probabilityMapNodePath)

            else:

                raise Exception, "findContours: invalid target: %s" % self.target


            contoursGroupedByImage = detector.findContours()
            contoursGroupedByImage.name = groupNodeName
            
            # add a node for all detected contours
            contoursNode = getNode(self.dataViewer.mainDoc.dataRootNode,
                                   contoursNodePath)
            contoursNode.addChild(contoursGroupedByImage)
            
            self.dataViewer.refreshTreeControls()




    def groupContoursByConnectedComponents(self, contoursNode):
        "Deprecated"
        
        contourList = nonnullObjectNodes(contoursNode)

        g = Graph()
        
        for contour in contourList:
            g.add_node_object(contour)
            #print contour.object.getAveragePointLocation()
            print contour.name
            contour.object.setColor((200, 100, 0))
        
        # regroup contours according to image only, not threshold and image
        numLayers = contoursNode.children[0].numberOfChildren()
        contoursGroupedByImage = GroupNode('contoursGroupedByImage')

        for layerIndex in range(numLayers):
            contoursGroupedByImage.addChild(Node('layer_%d' % layerIndex))

        for imageLayersNode in contoursNode.children:
            for layerIndex in range(len(imageLayersNode.children) - 1):
                layerNode = imageLayersNode.children[layerIndex]
                contoursGroupedByImage.children[layerIndex].addChildren(layerNode.children)

        self.dataViewer.addPersistentSubtreeAndRefreshDataTree((), contoursGroupedByImage)

        contourPairNode = GroupNode('contourPairNode')
        contourPairNode.children = [None, None]
        for imageIndex in range(len(contoursGroupedByImage.children) - 1):
            for contourNode1 in contoursGroupedByImage.children[imageIndex].children:
                contour1 = contourNode1.object
                center1 = contour1.getAveragePointLocation()
                for contourNode2 in contoursGroupedByImage.children[imageIndex + 1].children:
                    contour2 = contourNode2.object
                    contourPairNode.children[0] = contourNode1
                    contourPairNode.children[1] = contourNode2
                    featureDict = getContourListFeatures(contourPairNode,
                                        includeIndividualContourFeatures=False)
                    print featureDict
                    center2 = contour2.getAveragePointLocation()
                    #if linalg.norm(center1 - center2) < 10.0:
                    if linalg.norm(center1 - center2) < 50.0:
                        if overlap(contour1, contour2) > 0.4:
                            g.add_edge((contourNode1.name, contourNode2.name))
                        #print "overlap", overlap(contour1, contour2)
                    #print len(g.edges())
                    #print linalg.norm(center1 - center2)

        return pygraph.algorithms.accessibility.connected_components(g), g


    def runComputeContourRegions(self):

        self.computeContourRegions(self.contourProcessingTrainingRegion,
                                    self.trainingContoursNodePath)



    def computeContourRegions(self, contourProcessingTrainingRegion,
                                trainingContoursNodePath):
        """Set labels on contours according to underlying training data which is in raster form"""

        for labelName in self.labelFilePaths.keys():
            self.dataViewer.addPersistentVolumeAndRefreshDataTree(
                        resizeVolume(loadImageStack(self.labelFilePaths[labelName],
                                       contourProcessingTrainingRegion),
                                       (0.5, 0.5, 1)),
                        labelName)

        contoursRootNode = self.dataViewer.mainDoc.dataTree.getSubtree(
                                                        trainingContoursNodePath)
        self.dataViewer.refreshTreeControls()

        # flatten tree of contours into a list
        contourList = nonnullObjects(contoursRootNode)

        # visit each contour and look at the label that goes with each point
        for contour in contourList:
            count = {}
            contour.labelSet.clear()
            totalPixelCount = 0
            for labelVolumeName in self.labelFilePaths.keys():
                #count[labelVolumeName] = 0
                labelVolume = self.dataViewer.getVolume(labelVolumeName)

                boundingBox = contour.get2DBoundingBox()
                xOffset = boundingBox[0][0]
                yOffset = boundingBox[0][1]

                z = contour.points()[0].loc[2]

                for i in range(contour.binaryImage.shape[0]):
                    for j in range(contour.binaryImage.shape[1]):
                        #xOffset = boundingBox[0][0]
                        #yOffset = boundingBox[0][1]
                        location = (i+xOffset, j+yOffset, z)
                        if contour.binaryImage[i, j] != 0:
                            #volume[x, y, z] = 255

                            totalPixelCount += 1

                            try:
                                labelValue = at(labelVolume, location)
                            except IndexError:
                                raise IndexError, "Contour point %s outside of label volume with shape %s" \
                                    % (str(location), labelVolume.shape)
                            #componentLabelName = (labelVolumeName, str(labelValue))
                            componentLabel = (labelVolumeName, labelValue)

                            if componentLabel in count:
                                count[componentLabel] += 1
                            else:
                                count[componentLabel] = 1

            contour.numericLabelCountDict = count
            contour.labelCountDict = self.makeLabelCountDict(
                                            count,
                                            totalPixelCount)

            print "---------------------------"
            print "contour.labelCountDict:", contour.labelCountDict
            for numericLabel in count:
                print numericLabel, "   fraction of coverage:", float(count[numericLabel]) / float(totalPixelCount)


        self.dataViewer.mainDoc.dataTree.writeSubtree(trainingContoursNodePath)


    def makeLabelCountDict(self, numericLabelCountDict, contourArea):
        """Identifies the label associated with a contour, if any.
        The result labelCountDict associates a nonzero value with the label found inside of the contour.
        Labeled pixels must occupy 90% or more of the contour the label to be applied to the contour."""

        labelCountDict = {}

        for numericLabel in numericLabelCountDict:

            numPixels = numericLabelCountDict[numericLabel]

            if numPixels > (contourArea * 0.90):
            #if numPixels > (contourArea * 0.30):

                value = numericLabel[1]
                className = self.labelIdentifierDict.getClassName(value)

                if className in labelCountDict:
                    labelCountDict[className] += 1
                else:
                    labelCountDict[className] = 1

        return labelCountDict


    def makeContourLists(self,
                         contoursNodePath,
                         contourStackName,
                         allListsName,
                         probabilityThreshold, pathLength):
        """Make lists of contours. The list is a set of N contour extracted from N adjacent planes."""

        self.dataViewer.mainDoc.dataTree.getSubtree(contoursNodePath)
        self.dataViewer.refreshTreeControls()

        contoursNode = getNode(self.dataViewer.mainDoc.dataRootNode,
                                contoursNodePath)

        newContourStack = GroupNode(contourStackName)

        firstThresholdNode = contoursNode.children[0]
        numPlanes = len(firstThresholdNode.children)
        for i in range(numPlanes):
            newContourStack.addChild(GroupNode('plane_%d' % i))

        for thresholdSetNode in contoursNode.children:
            for contourPlaneNodeIndex in range(numPlanes):
                #print len(thresholdSetNode.children)
                #print numPlanes
                contourPlaneNode = thresholdSetNode.children[contourPlaneNodeIndex]
                for contourNode in contourPlaneNode.children:
                    newContourStack.children[contourPlaneNodeIndex].addChild(contourNode)

        self.dataViewer.addPersistentSubtreeAndRefreshDataTree((), newContourStack)

        #allPathsNode = GroupNode(self.contourPathsNodePath[0])
        #todo: change "Paths" to "Lists"
        allPathsNode = GroupNode(allListsName)

        #print "numPlanes - pathLength =", str(numPlanes - pathLength)

        for startIndex in range(numPlanes - pathLength):

            #print "startIndex", startIndex

            pathList = GroupNode()
            #pathList.addChild(GroupNode())
    
            # initialize the paths with the contours at the startIndex plane
            planeNode = newContourStack.children[startIndex]
            for contourNode in planeNode.children:
                pathNode = GroupNode()
                pathNode.addChild(contourNode)
                pathList.addChild(pathNode)

            for planeIndex in range(startIndex + 1, startIndex + pathLength):
    
                print "planeIndex:", planeIndex, "pathLength:", pathLength
    
                planeNode = newContourStack.children[planeIndex]
    
                newPathList = GroupNode()
    
                for contourNode in planeNode.children:
    
                    # contour that may be appended to path if it is close enough
                    newContour = contourNode.object
                    newCenter = newContour.getAveragePointLocation()
    
                    for pathNode in pathList.children:
    
                        # last contour in path that may be appended to
                        endOfPathContourNode = pathNode.children[-1]
                        contour1 = endOfPathContourNode.object
                        center1 = contour1.getAveragePointLocation()
    
                        if linalg.norm(center1 - newCenter) < 40:
                        #if linalg.norm(center1 - newCenter) < 20:
                        #if linalg.norm(center1 - newCenter) < 2000:
                        #if linalg.norm(center1 - newCenter) < 80:
                        #if 1:
    
                            newPathNode = copy_module.deepcopy(pathNode)
                            newPathNode.addObject(newContour)
                            newPathList.addChild(newPathNode)
    
                pathList = newPathList
                #pathList.name = 'planeIndex_%d' % planeIndex

            # calculate features
            for contourListNode in pathList.children:
                contourListNode.object = getContourListProperties(contourListNode)

            # calculate probabilities based on features
            classifyContourListsBayes(mitochondriaProbability, pathList)

            filteredPathList = GroupNode()

            # filter out low probability paths
            for contourListNode in pathList.children:
                #print contourListNode.object.probability()
                if contourListNode.object.probability() >=\
                   pow(probabilityThreshold, pathLength) / 200.0\
                   or not(enablePathProbabilityFilter):
                    filteredPathList.addChild(contourListNode)

            allPathsNode.addChildren(filteredPathList.children)
            
        self.dataViewer.addPersistentSubtreeAndRefreshDataTree((), allPathsNode)


    def calculateContourListFeatures(self, contourListsNodePath):

        contourListsNode = self.dataViewer.mainDoc.dataTree.getSubtree(contourListsNodePath)

        for contourListNode in contourListsNode.children:
            contourListNode.object = getContourListProperties(contourListNode)

        self.dataViewer.mainDoc.dataTree.writeSubtree(contourListsNodePath)
    
    
    def runCalculateVoxelClassificationAccuracy_deprecated(self):
        """
        Display accuracy information as text
        """

        if self.fullManualSegFilePath == None:
            raise Exception,\
                "fullManualSegFilePath is None, no actual segmentation specified"

        resultVolume =\
            self.dataViewer.getPersistentObject(self.currentVoxelClassificationResultPath())
        fullManualSegVolume = loadImageStack(self.fullManualSegFilePath,
                                             None,
                                             maxNumberOfImages=self.numberOfLayersToProcess)
        self.dataViewer.addVolumeAndRefreshDataTree_new(fullManualSegVolume,
                                                        self.fullManualSegNodePath)

        #print resultVolume[10, 10, 10]

        for i in range(0, 20, 1):

            threshold = i / 20.0
            print "threshold:", threshold

            accuracy = Accuracy(fullManualSegVolume, (resultVolume > threshold))
            accuracy.printAccuracy()


    def runCalculateFinalAccuracy_deprecated(self):
        """
        Compare output files to manual segmentation and display accuracy
        information as text
        """


        if self.fullManualSegFilePath == None:
            raise Exception,\
                "fullManualSegFilePath is None, no actual segmentation specified"

        resultVolume = loadImageStack("O:/images/HPFcere_vol/HPF_rotated_tif/output/blobOutput",
                                      None,
                                      maxNumberOfImages=self.numberOfLayersToProcess)
        self.dataViewer.addVolumeAndRefreshDataTree_new(resultVolume,
                                                        self.fullManualSegNodePath)

        fullManualSegVolume = loadImageStack(self.fullManualSegFilePath,
                                             None,
                                             maxNumberOfImages=self.numberOfLayersToProcess)
        self.dataViewer.addVolumeAndRefreshDataTree_new(fullManualSegVolume,
                                                        self.fullManualSegNodePath)

        #print resultVolume[10, 10, 10]

        accuracy = Accuracy(fullManualSegVolume, resultVolume)
        accuracy.printAccuracy()


    def runCalculateVoxelClassificationAccuracy_new_deprecated(self):
        """Deprecated"""

        import matplotlib.pyplot as pyplot

        fullManualSegVolume = loadImageStack(self.fullManualSegFilePath,
                                             None,
                                             maxNumberOfImages=self.numberOfLayersToProcess)
        self.dataViewer.addVolumeAndRefreshDataTree_new(fullManualSegVolume,
                                                        self.fullManualSegNodePath)


        #pyplot.hold(False)

        # for each type of subcellular component
        #for childNode in resultsNode.children:
        for target in self.labelIdentifierDict:

            pyplot.hold(True)

            for iteration in range(self._voxelClassificationIteration + 1):

                resultsNode = self.dataViewer.mainDoc.dataTree.getSubtree(
                                            self.voxelClassificationResultPath(iteration))


                #target = childNode.name

                #resultVolume = childNode.object

                try:

                    resultVolume = resultsNode.getChild(target).object


                    targetLabel = self.labelIdentifierDict[target].getBooleanVolume(
                                                                fullManualSegVolume)

                    self.dataViewer.addVolumeAndRefreshDataTree_new(targetLabel,
                                                                ('Volumes',
                                                                 target + 'Label'))

                    truePositiveRates = []
                    falsePositiveRates = []

                    #for i in range(0, 20, 1):
                    if 0:

                        threshold = i / 20.0
                        print "target:", target
                        print "threshold:", threshold

                        b = borderWidthForFeatures

                        accuracy = Accuracy(targetLabel[b[0]:-b[0], b[1]:-b[1], b[2]:-b[2]],
                                            (resultVolume[b[0]:-b[0], b[1]:-b[1], b[2]:-b[2]]
                                             > threshold))
                        accuracy.printAccuracy()

                        truePositiveRates.append(accuracy.truePositiveRate())
                        falsePositiveRates.append(accuracy.falsePositiveRate())


                    pyplot.plot(falsePositiveRates, truePositiveRates)
                    pyplot.axis([0, 0.3, 0.7, 1])
                    pyplot.title(target)
                    pyplot.xlabel('False Positive Rate')
                    pyplot.ylabel('True Positive Rate')
                    pyplot.grid(True)

                except NodeDoesNotExist:

                    warnings.warn("Subcellular component node %s does not exist." %
                                  target)

            pyplot.show()


    def runCalculateVoxelClassificationAccuracySingleComponent(self):
        """Calculate voxel accuracy for a single type of biological entity
        Compares automatic process to ground truth and generates plots"""

        calcRadon = False

        import matplotlib.pyplot as pyplot

        region = self.accuracyCalcRegion

        #b = 2 * array(borderWidthForFeatures)
        dummy = loadImageStack(self.voxelTrainingLabelFilePath, region)
        b = borderWidthForFeatures
        b[0] = 2 * b[0]
        b[1] = 2 * b[1]
        if b[2] != 0:
            startZ = b[2]
            endZ = -b[2]
        else:
            startZ = 0
            endZ = dummy.shape[2]
    
        print "borderWidthForFeatures:", borderWidthForFeatures
        #print "targetLabel size:%s shape:%s" % (str(size(targetLabel)),
        #                                        str(targetLabel.shape))
        print "accuracyCalcRegion:", self.accuracyCalcRegion

        fullManualSegVolume = (loadImageStack(self.voxelTrainingLabelFilePath,
                                             region))[b[0]:-b[0], b[1]:-b[1], startZ:endZ]
        print "fullManualSegVolume.shape", fullManualSegVolume.shape
        print "b", b
        print "startZ", startZ
        print "endZ", endZ
        self.dataViewer.addVolumeAndRefreshDataTree_new(fullManualSegVolume,
                                                        self.fullManualSegNodePath)

        originalVolume = 255 - (loadImageStack(self.originalImageFilePath,
                                             region))[b[0]:-b[0], b[1]:-b[1], startZ:endZ]

        voxelClassificationVolume = (loadImageStack(self.precomputedProbabilityMapFilePath,
                                             region))[b[0]:-b[0], b[1]:-b[1], startZ:endZ]

        self.dataViewer.addVolumeAndRefreshDataTree_new(voxelClassificationVolume,
                                                        ('Volumes',
                                                         'precomputedProbabilityMap'))

        #contourOutputVolume = (loadImageStack(r"O:\cytoseg_data\resized",
        #                                     region))[b[0]:-b[0], b[1]:-b[1], b[2]:-b[2]]
        contourOutputVolume = (loadImageStack(
                        os.path.join(self.highProbabilityContourOutputPath(), "resized"),
                        region))[b[0]:-b[0], b[1]:-b[1], startZ:endZ]

        #blobOutputVolume = (loadImageStack(r"O:\cytoseg_data\blobOutput\blobs\resized\700x700",
        #                                     region))[b[0]:-b[0], b[1]:-b[1], b[2]:-b[2]]
        blobPath = os.path.join(self.blobImageStackOutputFolder, "blobs", "resized")
        blobOutputVolume = (loadImageStack(blobPath,
                                           region))[b[0]:-b[0], b[1]:-b[1], startZ:endZ]


        target = 'primaryObject'

        pyplot.hold(True)

        targetLabel = self.labelIdentifierDict[target].getBooleanVolume(
                                                    fullManualSegVolume)

        self.dataViewer.addVolumeAndRefreshDataTree_new(targetLabel,
                                                    ('Volumes',
                                                     target + 'Label'))


        if calcRadon:
            radonPath = os.path.join(self.blobImageStackOutputFolder, "radonOutput", "resized")
            radonOutputVolume = 255 - (loadImageStack(radonPath,
                                               region))[b[0]:-b[0], b[1]:-b[1], startZ:endZ]


        volumes = {}
        volumes['originalVolume'] = originalVolume
        if calcRadon:
            volumes['radonVolume'] = radonOutputVolume
        volumes['voxelClassificationVolume'] = voxelClassificationVolume
        volumes['contourOutputVolume'] = contourOutputVolume
        volumes['blobOutputVolume'] = blobOutputVolume

        plotData = {}

        print "-----------------------------------"
        print "blob accuracy at threshold 50"
        blobAccuracy = Accuracy(targetLabel, (blobOutputVolume > 50))
        blobAccuracy.printAccuracy()
        print "-----------------------------------"

#        for resultVolume in (originalVolume, voxelClassificationVolume, blobOutputVolume):
#        for resultVolume in (blobOutputVolume,):
#        for resultVolume in (voxelClassificationVolume,):
#        for resultVolume in (contourOutputVolume,):
        for volumeName in volumes:

            print "-----------------------------------"
            print "volumeName:", volumeName
            print "-----------------------------------"

            resultVolume = volumes[volumeName]
            plotData[volumeName] = {}

            truePositiveRates = []
            falsePositiveRates = []
            accuracies = []
            VOCs = []


            if volumeName == 'originalVolume':
                step = 2 #20
            elif volumeName == 'radonVolume':
                step = 2
            elif volumeName == 'voxelClassificationVolume':
                step = 2
            else:
                step = 10 #20

            #for i in range(0, 25, 2):
            for i in range(0, 255, step):
            #for i in range(102, 105, step):
            #if 0:

                #threshold = i / 20.0
                #threshold = i * 10.0
                threshold = i
                print "target:", target
                print "threshold:", threshold

                accuracy = Accuracy(targetLabel, (resultVolume > threshold))
                accuracy.printAccuracy()

                truePositiveRates.append(accuracy.truePositiveRate())
                falsePositiveRates.append(accuracy.falsePositiveRate())
                accuracies.append(accuracy.accuracy())
                VOCs.append(accuracy.VOC())


            plotData[volumeName]['truePositiveRates'] = truePositiveRates
            plotData[volumeName]['falsePositiveRates'] = falsePositiveRates
            plotData[volumeName]['accuracies'] = accuracies
            plotData[volumeName]['VOCs'] = VOCs


            print "falsePositiveRates", falsePositiveRates
            print "truePositiveRates", truePositiveRates
            pyplot.plot(falsePositiveRates, truePositiveRates)
            #pyplot.title(target)
            pyplot.xlabel('False Positive Rate')
            pyplot.ylabel('True Positive Rate')
            pyplot.grid(True)

            singleThreshold = 50
            #singleAccuracy = Accuracy(targetLabel, blobOutputVolume > singleThreshold)
            #singleAccuracy = Accuracy(targetLabel, contourOutputVolume > singleThreshold)
            singleAccuracy = Accuracy(targetLabel, resultVolume > singleThreshold)
            xCoords = (singleAccuracy.falsePositiveRate(),)
            yCoords = (singleAccuracy.truePositiveRate(),)
            plotData[volumeName]['singlePointX'] = xCoords[0]
            plotData[volumeName]['singlePointY'] = yCoords[0]
            print "xCoords", xCoords
            print "yCoords", yCoords
            pyplot.scatter(xCoords,
                           yCoords,
                           s=10,
                           c='r')
            #pyplot.scatter((0, 0.1, 0.2),
            #               (0, 0.1, 0.2),
            #               s=10,
            #               c='r')

            #pyplot.axis([0.05, 0.3, 0.7, 1])
            #pyplot.axis([0, 0.3, 0.7, 1])
            pyplot.axis([0, 1, 0, 1])


        print plotData

        filename = strftime("plotData_%Y-%m-%d_%H.%M.%S.pickle", localtime())
        fullFilename = os.path.join(default_path.cytosegDataFolder, filename)
        print "writing", fullFilename

        file = open(fullFilename, 'wb')
        pickle.dump(plotData, file)
        file.close()

        pyplot.show()


    def runCalculateFinalAccuracyWithManualCorrection_deprecated(self):
        """
        Compare manually corrected output files to manual segmentation and
        display accuracy information as text
        """

        if self.fullManualSegFilePath == None:
            raise Exception,\
                "fullManualSegFilePath is None, no actual segmentation specified"

        resultVolume = loadImageStack("O:\images\HPFcere_vol\HPF_rotated_tif\output\cleaned with seg3d",
                                      None,
                                      maxNumberOfImages=self.numberOfLayersToProcess)
        self.dataViewer.addVolumeAndRefreshDataTree_new(resultVolume,
                                                        self.fullManualSegNodePath)

        fullManualSegVolume = loadImageStack(self.fullManualSegFilePath,
                                             None,
                                             maxNumberOfImages=self.numberOfLayersToProcess)
        self.dataViewer.addVolumeAndRefreshDataTree_new(fullManualSegVolume,
                                                        self.fullManualSegNodePath)

        #print resultVolume[10, 10, 10]

        accuracy = Accuracy(fullManualSegVolume, resultVolume)
        accuracy.printAccuracy()


    def runInitialize(self):

        """Initialize the name of the node for high probability contours and
        set which volume will be used to guide the fast march operation"""

        self.highProbabilityContoursNodeName = self.target + 'HighProbabilityContours'
    
        if self.target == 'primaryObject':
            self.fastMarchInputVolumeName = self.currentVoxelClassificationResultPath()[1]
        if self.target == 'mitochondria_new':
            self.fastMarchInputVolumeName =\
                self.inputProbabilityMapNodePath[1]
        elif self.target == 'vesicles':
            self.fastMarchInputVolumeName = self.originalVolumeName
        else:
            raise Exception, "find_3d_blobs target error"


    def runLoadInputImage(self):
        """
        Load subvolume input image and keep it at the tree location ('Volumes', self.originalVolumeName).
        self.regionToClassify specifies dimensions of the subvolume that will be loaded.
        """

        self.loadInputImage(('Volumes', self.originalVolumeName),
                            self.regionToClassify)




    def runLoadContourProcessingTrainingImage(self):
        """
        Load the raster image label map that corresponds to the training region
        for contour classification. Note that the same training image volume is
        used for voxel training and contour training. However, the regions used
        for voxel training and contour training may be specified separately.
        """

        nodePath = self.contourProcessingTrainingVolumeNodePath
        region = self.contourProcessingTrainingRegion

        image = loadImageStack(self.voxelTrainingImageFilePath, region)

        self.dataViewer.addPersistentVolumeAndRefreshDataTree(
                                    resizeVolume(image, (0.5, 0.5, 1)),
                                    #todo: this is a hack
                                    #it will only work for path with 'Volumes'
                                    nodePath[-1])




    def runLoadContourProcessingInputImage(self):
        """Load subvolume of input image from which contours will be extracted"""

        self.loadInputImage(self.contourProcessingInputVolumeNodePath,
                            self.contourProcessingRegionToClassify)


    def loadInputImage(self, nodePath, region):
        """
        Load 3D region of input image and place it at the node specified by nodePath.
        Node specified by nodePath must be directly under the Volumes node.
        """

        originalImage = loadImageStack(self.originalImageFilePath, region)

        originalImage = originalImage[:, :, 0:self.numberOfLayersToProcess]

        #self.dataViewer.addVolumeAndRefreshDataTree(originalImage, originalImageNodePath[1])

        self.dataViewer.addPersistentVolumeAndRefreshDataTree(
                                    resizeVolume(originalImage, (0.5, 0.5, 1)),
                                    # expects node to be under 'Volumes' node
                                    nodePath[-1])




    def runLoadInputProbabilityMap(self):
        """
        Load input probability map subvolume from image file stack.
        self.inputProbabilityMapNodePath is the node where the loaded volume will be placed.
        self.contourProcessingRegionToClassify specifies the subvolume dimensions.
        """

        self.loadInputProbabilityMap(self.inputProbabilityMapNodePath,
                                     self.contourProcessingRegionToClassify)


    def runLoadTrainingProbabilityMap(self):

        self.loadTrainingProbabilityMap(self.trainingProbabilityMapNodePath,
                                        self.contourProcessingTrainingRegion)




    def loadInputProbabilityMap(self, nodePath, region):
        """
        Loads a subvolume of the input probability map.
        The subvolume is placed at the node specified by nodePath.
        (Note that the training probability map is created by classifying
        voxels of the the input image.)
        """

        probabilityMap =\
            loadImageStack(self.precomputedInputProbabilityMapFilePath, region)

        probabilityMap = probabilityMap[:, :, 0:self.numberOfLayersToProcess]

        self.dataViewer.addPersistentObjectAndRefreshDataTree(
                                    resizeVolume(probabilityMap, (0.5, 0.5, 1)),
                                    nodePath)


    def loadTrainingProbabilityMap(self, nodePath, region):
        """
        Loads a subvolume of the training probability map.
        The subvolume is placed at the node specified by nodePath.
        (Note that the training probability map is created by classifying
        voxels of the the training image.)
        """

        probabilityMap =\
            loadImageStack(self.precomputedTrainingProbabilityMapFilePath, region)

        probabilityMap = probabilityMap[:, :, 0:self.numberOfLayersToProcess]

        self.dataViewer.addPersistentObjectAndRefreshDataTree(
                                    resizeVolume(probabilityMap, (0.5, 0.5, 1)),
                                    nodePath)


    def runLoadTrainingData(self):
        """
        Loads training image volumes and corresponding label volumes.
        Only the trainingRegion of the data is loaded.
        The training image volume is placed at the node specified by voxelTrainingImageNodePath.
        The training label volume is placed at the node specified by voxelTrainingLabelNodePath.
        """

        voxelTrainingImageNodePath = ('Volumes', 'voxelTrainingImage')
        voxelTrainingLabelNodePath = ('Volumes', 'voxelTrainingLabel')

        # load training images
        trainingDataVolume = loadImageStack(
                        self.voxelTrainingImageFilePath,
                        self.trainingRegion,
                        maxNumberOfImages=self.numberOfTrainingLayersToProcess)
        self.dataViewer.addVolumeAndRefreshDataTree_new(
                    resizeVolume(trainingDataVolume, (0.5, 0.5, 1)),
                    voxelTrainingImageNodePath)

        # load training labels
        labelVolume = loadImageStack(self.voxelTrainingLabelFilePath,
                            self.trainingRegion,
                            maxNumberOfImages=self.numberOfTrainingLayersToProcess)

        self.dataViewer.addVolumeAndRefreshDataTree_new(
                    resizeVolume(labelVolume, (0.5, 0.5, 1)),
                    voxelTrainingLabelNodePath)


    def runLoadAccuracyCalcData(self):
        """
        Loads training image volumes and corresponding label volumes.
        Only the accuracyCalcRegion of the data is loaded.
        The training image volume is placed at the node specified by voxelTrainingImageNodePath.
        The training label volume is placed at the node specified by voxelTrainingLabelNodePath.
        """

        voxelTrainingImageNodePath = ('Volumes', 'accuracyCalcImage')
        voxelTrainingLabelNodePath = ('Volumes', 'accuracyCalcLabel')

        print "voxelTrainingImageFilePath:", self.voxelTrainingImageFilePath
        print "voxelTrainingLabelFilePath:", self.voxelTrainingLabelFilePath
        #print "accuracyCalcRegion:", self.accuracyCalcRegion

        # load training images
        trainingDataVolume = loadImageStack(
                        self.voxelTrainingImageFilePath,
                        self.accuracyCalcRegion)
        self.dataViewer.addVolumeAndRefreshDataTree_new(
                    resizeVolume(trainingDataVolume, (0.5, 0.5, 1)),
                    voxelTrainingImageNodePath)

        # load training labels
        labelVolume = loadImageStack(self.voxelTrainingLabelFilePath,
                                     self.accuracyCalcRegion)

        self.dataViewer.addVolumeAndRefreshDataTree_new(
                    resizeVolume(labelVolume, (0.5, 0.5, 1)),
                    voxelTrainingLabelNodePath)


    def runPreclassificationFilter(self):

            self.preclassificationFilter(self.dataViewer,
                                numberOfLayersToProcess=self.numberOfLayersToProcess)


    def runClassifyVoxels(self):
        """Run voxel classification"""

        print "runClassifyVoxels"
        print "self.numberOfLayersToProcess", self.numberOfLayersToProcess
        self.classifyVoxels(self.dataViewer,
                            #self.labelIdentifierDict[self.target],
                            numberOfLayersToProcess=self.numberOfLayersToProcess)




    def writeVolumeResult(self, outputPath, rawOriginalVolume, rawOutputVolume, region,
                          borderWidth, zCrop=None):
        """
        Outputs results in 3 forms for viewing:
        1. Output images showing segmentation
        2. Segmentation overlaid on the original images
        3. Rescaled (to original file size) images showing segmentation
        """

        print "writeVolumeResult"
        print "outputPath", outputPath

        outputVolume = resizeVolume(rawOutputVolume, (2, 2, 1))
        if not(os.path.exists(outputPath)):
            os.mkdir(outputPath)
        b = borderWidth
        s = outputVolume.shape

        start = [None, None, None]
        stop = [None, None, None]

        for coordinate in range(0, 2):
            #start[coordinate] = b[coordinate]
            start[coordinate] = 0
            #stop[coordinate] = s[coordinate] - b[coordinate]
            stop[coordinate] = s[coordinate]

        if zCrop != None:
            start[2] = zCrop[0]
            stop[2] = s[2] - zCrop[1]
        else:
            start[2] = b[2]
            stop[2] = s[2] - b[2]


        rawOutputPath = os.path.join(outputPath, 'raw')
        if not(os.path.exists(rawOutputPath)):
            os.mkdir(rawOutputPath)

        if region == None:
            writeStack(rawOutputPath, rawOutputVolume * 255.0)
        else:
            writeStack(rawOutputPath,
                        #todo: resize will make offsets wrong
                        rawOutputVolume[:,
                                        :,
                                        start[2]:stop[2]] * 255.0,
                        startIndex=region.cornerA[2]+start[2])
    

        resizedOutputPath = os.path.join(outputPath, 'resized')
        if not(os.path.exists(resizedOutputPath)):
            os.mkdir(resizedOutputPath)
        
        if region == None:
            writeStack(resizedOutputPath, outputVolume * 255.0)
        else:
            writeStack(resizedOutputPath,
                        #todo: resize will make offsets wrong
                        outputVolume[start[0]:stop[0],
                                     start[1]:stop[1],
                                     start[2]:stop[2]] * 255.0,
                        startIndex=region.cornerA[2]+start[2])
    

        originalVolume = resizeVolume(rawOriginalVolume, (2, 2, 1))
        compositeImagePath = os.path.join(outputPath, "composite")

        if not(os.path.exists(compositeImagePath)):
            os.mkdir(compositeImagePath)

        if region == None:
            out = outputVolume * 255.0
            #rawOut = rawOutputVolume * 255.0
            orig = originalVolume
            #rawOrig = rawOriginalVolume
            startIndex = 0
        else:
            out = outputVolume[start[0]:stop[0],
                                 start[1]:stop[1],
                                 start[2]:stop[2]] * 255.0
            orig = originalVolume[start[0]:stop[0],
                                 start[1]:stop[1],
                                 start[2]:stop[2]]
            startIndex = region.cornerA[2] + start[2]

        writeStackRGB(compositeImagePath,
                          orig,
                          numpy.clip(orig + (out * 0.7), 0, 255),
                          orig,
                          startIndex=startIndex)


    def runWriteTrainingVoxelClassificationResult(self):
            """Writes training image voxel classification results to an image stack for viewing"""

            print "runWriteTrainingVoxelClassificationResult"

            resultsNode = self.dataViewer.mainDoc.dataTree.getSubtree(
                            self.currentVoxelClassificationResultPath())
            self.dataViewer.refreshTreeControls()

            # create folder if neccesary
            trainingPath = os.path.join(self.blobImageStackOutputFolder, "training")
            if not(os.path.exists(trainingPath)):
                os.mkdir(trainingPath)

            for childNode in resultsNode.children:
                self.writeVolumeResult(os.path.join(trainingPath, childNode.name),
                                        self.dataViewer.getPersistentVolume_old(
                                            self.voxelClassificationInputVolumeName),
                                        childNode.object,
                                        self.regionToClassify,
                                        borderWidthForFeatures)


    def runWriteInputVoxelClassificationResult(self):
            """Writes input image voxel classification results to an image stack for viewing"""

            #log.info("runWriteVoxelClassificationResult")
            print "runWriteInputVoxelClassificationResult"

            # write classification result to a stack of tiffs
    
            #volume = self.dataViewer.getPersistentObject(
            #    list(self.voxelClassificationResultPath).append('0'))
            resultsNode = self.dataViewer.mainDoc.dataTree.getSubtree(
                            self.currentVoxelClassificationResultPath())
            self.dataViewer.refreshTreeControls()

            for childNode in resultsNode.children:
                self.writeVolumeResult(os.path.join(self.blobImageStackOutputFolder,
                                                    childNode.name),
                                        self.dataViewer.getPersistentVolume_old(
                                            self.voxelClassificationInputVolumeName),
                                        childNode.object,
                                        self.regionToClassify,
                                        borderWidthForFeatures)


    def multithresholdFindContours(self,
                                   contoursNodePath,
                                   originalVolumeNodePath,
                                   probabilityMapNodePath):
            """
            Find isocontours at multiple values.
            Parameters:
            contoursNodePath: identifies node where result contours are placed
            originalVolumeNodePath: identifies image volume
            probabilityMapNodePath: identifies probability map from which isocontours will be extracted
            """

            self.dataViewer.mainDoc.dataRootNode.addChild(
                GroupNode(contoursNodePath[-1]))

            for thresholdIndex in range(self.numberOfThresholds):

                self.findContours(contoursNodePath,
                    originalVolumeNodePath,
                    probabilityMapNodePath,
                    "thresholdIndex_%d" % thresholdIndex,
                    self.firstThreshold + (self.thresholdStep * thresholdIndex),
                    self.numberOfLayersToProcess)

            self.dataViewer.mainDoc.dataTree.writeSubtree(contoursNodePath)


    def runFindTrainingContours(self):
        """Use multithresholdFindContours to make training contours."""

        print "runFindTrainingContours", self.trainingContoursNodePath

        self.multithresholdFindContours(self.trainingContoursNodePath,
                                        self.contourProcessingTrainingVolumeNodePath,
                                        self.trainingProbabilityMapNodePath)


    def runFindInputContours(self):
        """Use multithresholdFindContours to make contours from the input
        image volume that will be classified."""

        print "runFindInputContours", self.inputContoursNodePath
        print "numberOfThresholds", self.numberOfThresholds
        print "firstThreshold", self.firstThreshold
        print "thresholdStep", self.thresholdStep

        # print out thresholds that will be used
        for thresholdIndex in range(self.numberOfThresholds):
            threshold = self.firstThreshold + (self.thresholdStep * thresholdIndex)
            #print threshold
            print "%f%%" % ((float(threshold) / 255.0) * 100.0)

        self.multithresholdFindContours(self.inputContoursNodePath,
                                        self.contourProcessingInputVolumeNodePath,
                                        self.inputProbabilityMapNodePath)


    def runMakeTrainingContourLists(self):
        """Make training contour lists. (Training data is the data that has been segmented manually.)"""

        self.makeContourLists(
            self.trainingContoursNodePath,
            'TrainingContourStack',
            self.trainingContourListsNodePath[0],
            self.displayParametersDict[self.target].contourProbabilityThreshold,
            self.pathLength[self.target])


    def runMakeInputContourLists(self):
        """Make input contour lists. (Input data is the data that is to be segmented automatically.)"""

        self.makeContourLists(
            self.inputContoursNodePath,
            'InputContourStack',
            self.inputContourListsNodePath[0],
            self.displayParametersDict[self.target].contourProbabilityThreshold,
            self.pathLength[self.target])




    def runWriteContoursToImageStack(self):
        """Write filled contours to image stack."""

        self.writeContoursToImageStack(self.inputContourListsNodePath)


    def runWriteInputContoursToBinaryImageStack(self):
        """Write filled contours to binary image stack."""

        unfilteredContourOutputPath = self.unfilteredContourOutputPath()
        if not(os.path.exists(unfilteredContourOutputPath)):
            os.mkdir(unfilteredContourOutputPath)

        self.writeContoursToBinaryImageStack(self.inputContourListsNodePath,
                                             unfilteredContourOutputPath,
                                             probabilityThreshold=0)


    def loadOriginalVolume(self):
        """Load original input volume."""

        self.dataViewer.getPersistentVolume_old(self.originalVolumeName)


    def loadVoxelClassificationResult(self):
        """Load the voxel classification result, i.e. probability map"""

        self.dataViewer.getPersistentVolume_old(
                                self.currentVoxelClassificationResultPath()[1])


    def runTrainingContourListClassifier(self):
        """Classifies the training contour lists, this can be used to test accuracy."""

        self.executeContourListClassifier(self.trainingContoursNodePath,
                                                self.trainingContourListsNodePath,
                                                self.contourListTrainingExamplesIdentifier)


    def runInputContourListClassifier(self):
        """Classifies the input contour lists."""

        self.executeContourListClassifier(self.inputContoursNodePath,
                                                self.inputContourListsNodePath,
                                                self.contourListTrainingExamplesIdentifier)


    def executeContourListClassifier(self, contoursNodePath, contourListsNodePath,
                                            inputTrainingExamplesIdentifier):

        """
        Classifies contour lists.  Probability values for the lists will be modified.
        Parameters:
        contoursNodePath: deprecated
        contourListsNodePath: identifies contour lists.
        inputTrainingExamplesIdentifier: string that identifies the training examples to be used
        """

        contoursGroupedByImage = self.dataViewer.mainDoc.dataTree.getSubtree(
                                    contoursNodePath)

        # test code
        # individual contour probabilities
        if 0:
            updateContourProbabilities(contoursGroupedByImage,
                                        self.probabilityFunctionDict[self.target])


        # load contour lists for processing
        self.dataViewer.mainDoc.dataTree.getSubtree(contourListsNodePath)

        # perform classification
        if self.contourListClassificationMethod == 'randomForest':
            print "classifyContourLists"
            classifyContourLists(self.dataViewer,
                    inputTrainingExamplesIdentifier=inputTrainingExamplesIdentifier,
                    contourListsNodePath=contourListsNodePath)
        elif self.contourListClassificationMethod == 'bayes':
            classifyContourListsNodePathBayes(self.dataViewer,
                    self.probabilityFunctionDict[self.target],
                    contourListsNodePath=contourListsNodePath)
        else:
            raise Exception, "invalid classification method"

        print "writing contour lists"
        self.dataViewer.mainDoc.dataTree.writeSubtree(contourListsNodePath)
        print "refreshing tree controls"
        self.dataViewer.refreshTreeControls()
        print "finished execute contour list classifier"


    def saveContourPathsToJinxFile(self):
        """Save contour paths to Jinx file"""

        saveBlobsToJinxFile(self.dataViewer.mainDoc.dataTree.getSubtree(
                                                        self.contourPathsNodePath),
                            self.target + "_contours")


    def runFill3DBlobsFromContours(self):
        """Perform 3D shell active contour operation to fill 3D blobs"""

        fillAndDisplayResults(self.dataViewer, self.fastMarchInputVolumeName,
                                   self.contourPathsNodePath[0],
                                   self.displayParametersDict[self.target],
                                   self.enable3DPlot,
                                   fillMethod='shellActiveContour')


    def runFill3DBlobsFromContoursHighProbabilityOnly(self):
            """
            Depricated
            Perform 3D shell active contour operation to fill 3D blobs.
            Seed only from high probability contours
            """
    
            if self.enable3DPlot:
                display3DContours(self.dataViewer, self.originalVolumeName, self.highProbabilityContoursNodeName,
                                    self.displayParametersDict[self.target])
    
            fillAndDisplayResults(self.dataViewer, self.fastMarchInputVolumeName,
                                       self.highProbabilityContoursNodeName,
                                       self.displayParametersDict[self.target],
                                       self.enable3DPlot,
                                       fillMethod='shellActiveContour')


    def runFill3DBlobsFromContourListsHighProbabilityOnly(self):
            """
            Perform 3D shell active contour operation to fill 3D blobs.
            Seed only from high probability contours lists
            """
    
            fillAndDisplayResults(self.dataViewer,
                                  self.fastMarchInputVolumeName,
                                  'HighProbabilityInputContourLists',
                                  self.displayParametersDict[self.target],
                                  self.enable3DPlot,
                                  fillMethod='shellActiveContour')


    def runContourProbabilityFilter(self):
            """
            Depricated as this only applies to single contours
            This function does the following:
            - calculate probabilities that contours are salient
            - filter contours by probability threshold, adding nodes for the high probability contours only
            """

            allContoursNode =\
                self.dataViewer.mainDoc.dataTree.getSubtree(self.trainingContoursNodePath)

            updateContourProbabilities(allContoursNode,
                                       self.probabilityFunctionDict[self.target])

            threshold = self.displayParametersDict[self.target].contourProbabilityThreshold
            highProbabilityContoursNode = copyTree_old(allContoursNode,
                                                   ProbabilityFilter(threshold))
            highProbabilityContoursNode.name = self.highProbabilityContoursNodeName
 
            self.dataViewer.addPersistentSubtreeAndRefreshDataTree((), highProbabilityContoursNode)
            self.dataViewer.getPersistentVolume_old(self.originalVolumeName)
            self.dataViewer.refreshTreeControls()

            #print "writing", highProbabilityContoursNode, "to image stack"
            #self.writeContoursToBinaryImageStack(highProbabilityContoursNode)

            print self.highProbabilityContoursNodeName
            saveBlobsToJinxFile(self.dataViewer.mainDoc.dataTree.getSubtree(
                                                (self.highProbabilityContoursNodeName,)),
                                                self.highProbabilityContoursBaseFilename)

            # write contours to an image stack for viewing
            #temporarily commenting this out#self.writeContoursToImageStack((self.highProbabilityContoursNodeName,))


    def runContourListProbabilityFilter(self):

            """
            This function does the following:
            - calculate probabilities that contour lists are salient
            - filter contour lists by probability threshold, adding nodes for the high probability contour lists only
            """

            threshold = self.contourListProbabilityThreshold

            print "runContourListProbabilityFilter, threshold: %f" % threshold

            allContourListsNode =\
                self.dataViewer.mainDoc.dataTree.getSubtree(
                                                self.inputContourListsNodePath)

            #updateContourProbabilities(allContourListsNode,
            #                           self.probabilityFunctionDict[self.target])

            print "copyTree allContoursListNode"
            highProbabilityContourListsNode = copyTree(allContourListsNode,
                                                   ActiveProbabilityFilter(threshold))

            highProbabilityContourListsNode.name = 'HighProbabilityInputContourLists'
 
            self.dataViewer.addPersistentSubtreeAndRefreshDataTree(
                                        (), highProbabilityContourListsNode)
            #self.dataViewer.getPersistentVolume_old(self.originalVolumeName)
            self.dataViewer.refreshTreeControls()

            highProbabilityContourOutputPath = self.highProbabilityContourOutputPath()
            if not(os.path.exists(highProbabilityContourOutputPath)):
                os.mkdir(highProbabilityContourOutputPath)

            print "writing highProbabilityContourListsNode to image stack"
            print "output path: %s" % highProbabilityContourOutputPath
            self.writeContoursToBinaryImageStack((highProbabilityContourListsNode.name,),
                                                 highProbabilityContourOutputPath,
                                                 self.contourListProbabilityThreshold)

            #print self.highProbabilityContourListsNodeName
            #saveBlobsToJinxFile(self.dataViewer.mainDoc.dataTree.getSubtree(
            #                                    (self.highProbabilityContoursNodeName,)),
            #                                    self.highProbabilityContoursBaseFilename)


    def runWrite3DBlobsVolume(self):
            """Write 3D blobs to a stack of tiffs"""

            print sys._getframe().f_code.co_name
    
            allBlobs = self.dataViewer.getPersistentVolume_old(
                                                    self.fastMarchInputVolumeName +
                                                    'AllFastMarchBlobs')
            self.dataViewer.refreshTreeControls()
            path = os.path.join(self.blobImageStackOutputFolder, "blobs")
            print path

            borderWidth = copy_module.deepcopy(borderWidthForFeatures)
            borderWidth[2] = 0

            #writeTiffStack(self.blobImageStackOutputFolder, (allBlobs > 0) * 255.0)
            self.writeVolumeResult(path,
                              self.dataViewer.getPersistentObject(
                                    self.contourProcessingInputVolumeNodePath),
                              (allBlobs > 0) * 0.5,
                              self.contourProcessingRegionToClassify,
                              borderWidth,
                              (globals.blobOutputCropZLower(),
                               globals.blobOutputCropZUpper()))
                              #(2,
                               #1))


    def runGroupContoursByConnectedComponents(self):
            """Deprecated"""
            
            contoursGroupedByImage = self.dataViewer.mainDoc.dataTree.getSubtree(
                                      (self.contoursNodeName,))
            updateContourProbabilities(contoursGroupedByImage,
                                       self.probabilityFunctionDict[self.target])
            connectedComponents, graph =\
                self.groupContoursByConnectedComponents(contoursGroupedByImage)
            
            #count = 0
            s = 1.0
            v = 1.0
            
            print connectedComponents
            
            for nodeNameKey in connectedComponents:
                #nodeName = connectedComponents[key]
                attributes = graph.node_attributes(nodeNameKey)
                contourNode = attributes[0]
                #h = 0.05 * count
                h = 0.05 * connectedComponents[nodeNameKey]
                print contourNode.object.color()
                print "h", h, "s", s, "v", v
                h = remainder(h, 1.0)
                contourNode.object.setColor(255.0 * array(colorsys.hsv_to_rgb(h, s, v)))
                #contourNode.object.setColor((200, 200, 200))
                #count += 1

            originalVolume = self.dataViewer.getPersistentVolume_old(self.originalVolumeName)
            contourRenderingVolume = zeros((originalVolume.shape[0],
                                            originalVolume.shape[1],
                                            originalVolume.shape[2],
                                            3))

            self.dataViewer.renderPointSetsInVolumeRecursive(contourRenderingVolume,
                                                      contoursGroupedByImage,
                                                      valueMode='RGB')


            originalVolumeDark = originalVolume * 0.5

            writeStackRGB(os.path.join(defaultOutputPath, "rgb"),
                              contourRenderingVolume[:, :, :, 0] + originalVolumeDark,
                              contourRenderingVolume[:, :, :, 1] + originalVolumeDark,
                              contourRenderingVolume[:, :, :, 2] + originalVolumeDark)


    def runCalculateTrainingContourListFeaturesTask(self):
        """Compute features of the contour lists that are used for training."""

        self.calculateContourListFeaturesTask(self.trainingContourListsNodePath,
                                    self.contourListExamplesIdentifier,
                                    recordKnownClassificationWithExamples=True)


    def runCalculateInputContourListFeaturesTask(self):
        """Compute festures of contour lists that are to be classified from the input data."""

        self.calculateContourListFeaturesTask(self.inputContourListsNodePath,
                                    self.contourListInputDataExamplesIdentifier,
                                    recordKnownClassificationWithExamples=False)


    def calculateContourListFeaturesTask(self, contourListsNodePath,
                                            outputExamplesIdentifier,
                                            recordKnownClassificationWithExamples):
            """
            Calculate features of contours.
            Parameters:
            contourListsNodePath: the contour lists whose features will be calculated.
            outputExamplesIdentifier: specifies the basename of the file where results are placed.
            recordKnownClassificationWithExamples: (boolean) option, if True and there is known classification (training data), record it also in the output file.
            """

            self.calculateContourListFeatures(contourListsNodePath)
            recordFeaturesOfContourLists(self.dataViewer,
                            inputTrainingContourListsNodePath=contourListsNodePath,
                            outputExamplesIdentifier=outputExamplesIdentifier,
                            recordKnownClassificationWithExamples=\
                                recordKnownClassificationWithExamples,
                            contourListWeightDict=self.contourListWeightDict)
            #self.dataViewer.getPersistentVolume_old(self.originalVolumeName)

            # display label volumes
            if self.labelFilePaths != None:
                for labelName in self.labelFilePaths.keys():
                    self.dataViewer.getPersistentVolume_old(labelName)

            self.dataViewer.refreshTreeControls()


    def runStep(self, stepNumber):
        """Deprecated. Use runSteps from run_steps module."""
        

        print "running step number", stepNumber
        self.runInitialize()
        

        if stepNumber == 0:

            self.runPreclassificationFilter()


        elif stepNumber == 1:

            self.runClassifyVoxels()


        elif stepNumber == 2:

            self.dataViewer.getPersistentVolume_old(
                                    self.currentVoxelClassificationResultPath()[1])


        # find contours
        elif stepNumber == 3:

            self.runFindContours()


        elif stepNumber == 4:

            self.dataViewer.getPersistentVolume_old(self.originalVolumeName)
            self.runComputeContourRegions()


        elif stepNumber == 5:

            self.writeContoursToImageStack(self.trainingContoursNodePath)


        elif stepNumber == 6:

            self.dataViewer.getPersistentVolume_old(self.originalVolumeName)

            saveBlobsToJinxFile(
                self.dataViewer.mainDoc.dataTree.getSubtree(self.trainingContoursNodePath))

            self.dataViewer.refreshTreeControls()


        elif stepNumber == 7:
            
            self.runMakeContourLists()


        elif stepNumber == 8:

            saveBlobsToJinxFile(
                self.dataViewer.mainDoc.dataTree.getSubtree(self.contourPathsNodePath))


#        elif stepNumber == 8:
#
#            self.calculateContourListFeatures()


        elif stepNumber == 9:

            self.calculateContourListFeatures()
            recordFeaturesOfContourLists(self.dataViewer,
                            inputTrainingContourListsNodePath=self.contourPathsNodePath,
                            outputExamplesIdentifier=self.contourListExamplesIdentifier,
                            contourListWeightDict=contourListWeightDict)
            self.dataViewer.getPersistentVolume_old(self.originalVolumeName)

            # display label volumes
            if self.labelFilePaths != None:
                for labelName in self.labelFilePaths.keys():
                    self.dataViewer.getPersistentVolume_old(labelName)

            self.dataViewer.refreshTreeControls()


        elif stepNumber == 10:
            
            self.loadItemsForViewing()


        elif stepNumber == 11:

            self.saveContourPathsToJinxFile()


        elif stepNumber == 12:
    
            self.runFill3DBlobsFromContours()


        elif stepNumber == 106:

            self.runContourProbabilityFilter()
    
        
        elif stepNumber == 107:

            self.runGroupContoursByConnectedComponents()


        elif stepNumber == 108:
    
            # use GUI to display high probability contours
    
            if self.enable3DPlot: display3DContours(self.dataViewer, self.originalVolumeName, self.highProbabilityContoursNodeName,
                                                self.displayParametersDict[self.target])
            self.dataViewer.mainDoc.dataTree.getSubtree((self.highProbabilityContoursNodeName,))
            self.dataViewer.refreshTreeControls()
    
    
        elif stepNumber == 109:
    
            self.runFill3DBlobsFromContoursHighProbabilityOnly()
    

        elif stepNumber == 110:
    
            # write 3D blobs to an XML file and into a stack of tiffs for viewing
    
            self.dataViewer.mainDoc.dataTree.readSubtree(('Blobs',))
            saveBlobsToJinxFile(self.dataViewer.mainDoc.dataTree.getSubtree(('Blobs',)))
            original = self.dataViewer.getPersistentVolume_old(self.originalVolumeName)
            allBlobs = self.dataViewer.getPersistentVolume_old(self.fastMarchInputVolumeName + 'AllFastMarchBlobs')
            self.dataViewer.refreshTreeControls()
            writeStackRGB(defaultOutputPath,
                              #redVolume=rescale(allBlobs, 0, 255.0),
                              redVolume = (allBlobs > 0) * 255.0,
                              greenVolume=original,
                              blueVolume=None)
            writeStack(os.path.join(defaultOutputPath, "blobVolume"),
                           (allBlobs > 0) * 255.0)
    
    
        print "finished step"
        self.runMainLoop()


    def runVoxelTestSteps(self):
        """Deprecated. Test code."""

        self.runStep(0)
        self.runStep(1)


    def runContourTestSteps(self):
        """Deprecated. Test code."""

        ##self.runStep(3)
        self.runStep(7)
        self.runStep(9)
        #self.runStep(10)
        self.runStep(106)


