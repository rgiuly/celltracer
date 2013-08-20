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

# Voxel/pixel classification module (with experimental GUI features).

#from scipy import ndimage
#import geometry

#import SciPy
import statistics
import os
import threading
import random

try:
    import orange, orngTree, orngEnsemble
    print "orange loaded"
except ImportError:
    print "orange data mining tool not loaded" 

print "importing filters"
from filters import *
print "importing volume3d_util"
from volume3d_util import *
print "importing data_viewer"
from data_viewer import *
print "importing geometry"
from geometry import *
print "importing neural_network"
from neural_network import *
if 0:
    print "importing cytoseg_logging"
    from cytoseg_logging import *
else:
    import logging

cubeSizeNames = ('3X3', '5X5', '7x7')
cubeOffsets = (1, 2, 3)
#salientLabelValue = 100

count = 0

class Bubble:
    """Deprecated"""
    def __init__(self, location, radius, thickness):
        self.loc = location
        self.radius = radius
        self.thickness = thickness



class BubblePhantom:
    """Deprecated"""
    
    def __init__(self, signalBubbles, noiseBubbles, volumeShape):
        """Deprecated"""
        self.volumeShape = volumeShape
        self.signalBubbles = signalBubbles
        self.noiseBubbles = noiseBubbles
        
        self.salientLabelValue = 100
        
    def createSignalVolume(self):
        """Deprecated"""
        bubbles = self.signalBubbles
        return self.createVolumeWithBubbles(bubbles)

    def createVolume(self):
        """Deprecated"""
        bubbles = self.signalBubbles + self.noiseBubbles
        return self.createVolumeWithBubbles(bubbles)


    def createVolumeWithBubbles(self, bubbles):
        """Deprecated"""
        
        
        v = numpy.zeros(self.volumeShape, numpy.uint8)
        
        for x in range(self.volumeShape[0]):
            for y in range(self.volumeShape[1]):
                for z in range(self.volumeShape[2]):
                    #print ""
                    for bubble in bubbles:
                        distanceFromSphereSurface = abs(bubble.radius - distance(bubble.loc, array([x,y,z])))
                        v[x,y,z] += gaussian(distanceFromSphereSurface, 50, bubble.thickness)
    
        return v



    def createSignalLabelVolume(self):
        """Deprecated"""
        #return 100.0 * (self.createSignalVolume() > 20)
        return self.salientLabelValue * (self.createSignalVolume() > 20)


def makeClassifyGUITree():
    """Create GUI specification."""

    rootNode = makeDefaultGUITree()
    #print "rootNode"
    #print rootNode
    node = getNode(rootNode, ('particleMotionTool',))
    #print node
    #node.insertChildrenAt((
    node.addChildren((
                    DataNode("facesProbabilityThreshold","slider",{'caption' : 'facesProbabilityThreshold', 'max' : 300},0),
                    DataNode("useFacesProbabilityThreshold","boolean",{'caption' : 'useFacesProbabilityThreshold'},False),
                    DataNode("displayPixelFeature","boolean",{'caption' : 'displayPixelFeature'},False),
                    #DataNode("learnFeaturesOfMembraneVoxels","button",{'caption' : 'step 1. learnFeaturesOfMembraneVoxels'},'old_onLearnFeaturesOfMembraneVoxels'),
                    #DataNode("classifyVoxelsOfCurrentImage","button",{'caption' : 'step 2. classifyVoxelsOfCurrentImage'},'old_onClassifyVoxelsOfCurrentImage'),
                    DataNode("learnFeaturesOfMembraneVoxels","button",{'caption' : 'step 1. learnFeaturesOfMembraneVoxels'},'onLearnFeaturesOfMembraneVoxels'),
                    #DataNode("classifyVoxelsOfCurrentImage","button",{'caption' : 'step 2. classifyVoxelsOfCurrentImage'},'old_onClassifyVoxelsOfCurrentImage'),
                    DataNode("classifyVoxelsOfImageStack","button",{'caption' : 'step 2. classifyVoxelsOfImageStack'},'onClassifyVoxelsOfImageStack'),

                    #DataNode("learnFeaturesOfMembraneFaces","button",{'caption' : 'learnFeaturesOfMembraneFaces'},'onLearnFeaturesOfMembraneFaces'),
                    DataNode("findAndClassifyFaces","button",{'caption' : 'findAndClassifyFaces'},'onFindAndClassifyFaces'),

                    DataNode("calculateDerivatives","button",{'caption' : 'calculateDerivatives'},'onCalculateDerivatives'),
                    DataNode("calculateSecondDerivatives","button",{'caption' : 'calculateSecondDerivatives'},'onCalculateSecondDerivatives'),
                    DataNode("convolutionTest","button",{'caption' : 'convolutionTest'},'onConvolutionTest'),
                    DataNode("makeVoxelClassificationDataFile","button",{'caption' : 'makeVoxelClassificationDataFile'},'old_onMakeVoxelClassificationDataFile'),
                    DataNode("makePointFeatureViewer","button",{'caption' : 'makePointFeatureViewer'},'onMakePointFeatureViewer'),
                    DataNode("makeFaceFeatureViewer","button",{'caption' : 'makeFaceFeatureViewer'},'onMakeFaceFeatureViewer'),
                    DataNode("makeBubblePhantom","button",{'caption' : 'Make Bubble Phantom'},'onMakeBubblePhantom')))
    
    return rootNode


class ClassificationSequenceThread(threading.Thread):
    """Experimental: Thread to run classification from GUI."""
    
    def __init__(self, frame):
        threading.Thread.__init__(self)
        self.frame = frame
    
    def run(self):
        self.frame.runClassificationSequence()
        



class ClassificationControlsFrame(ControlsFrame):
    """Class for pixel/voxel classification (with some experimental optional GUI support)"""

    def __init__(self, settingsTree, guiVisible=True):
        ControlsFrame.__init__(self, settingsTree, guiVisible=guiVisible)
        print "ClassificationControlsFrame init"
        
        # classification
        self.numberOfTrees = 50
        #self.balanceExamples = False
        #self.balanceExamples = True

        # gui
        self.mouseClickCallbackDict['updatePointFeaturesAtMouseLocation'] = self.updatePointFeaturesAtMouseLocation
        self.mouseClickCallbackDict['printBlobNameAtMouseLocation'] = self.printBlobNameAtMouseLocation
        self.refreshGUI()
        
        #sourceType = 'phantom'
        sourceType = 'imageFile'
        
        # this chooses whether to use original image or probability of salient pixel image for watershed
        useOriginalForWatershed = True

        self.viewerRootNode = None


        thread = ClassificationSequenceThread(self)
        thread.start()


        if 0:
            # display volumes
            self.getPersistentVolume_old('test_Original')
            self.getPersistentVolume_old('voxelClassificationOnTestVolume_ProbabilityVolume')
            self.getPersistentVolume_old('forFaceTraining_ProbabilityVolume')
                        
            for i in range(3):
                self.getPersistentVolume_old('%s_0Gradient_blur%d' % ('test', i))
                self.getPersistentVolume_old('%s_1Gradient_blur%d' % ('test', i))
                self.getPersistentVolume_old('%s_2Gradient_blur%d' % ('test', i))


    def runClassificationSequence(self):
        """Depricated"""

        voxelTrainingImageFilePath = "O:\\images\\HPFcere_vol\\HPF_rotated_tif\\three_compartment\\"
        voxelTrainingLabelFilePath = "O:\\images\\HPFcere_vol\\HPF_rotated_tif\\three_compartment\\membrane_label_for_three_compartments\\"

        #self.trainingImageFilePath = "O:\\images\\HPFcere_vol\\HPF_rotated_tif\\8bit\\training\\filtered_tif\\"
        self.trainingImageFilePath = "O:\\images\\HPFcere_vol\\HPF_rotated_tif\\median_then_gaussian_8bit\\"
        self.trainingLabelFilePath = "O:\\images\\HPFcere_vol\\face_training_labels_feb_2009\\"
        self.trainingMembranePhantom = self.membranePhantom1
        
        self.testImageFilePath = "O:\\images\\HPFcere_vol\\HPF_rotated_tif\\seg3D\\tifs\\cropped\\" 
        self.testMembranePhantom = self.membranePhantom2

        self.derivativesForPointViewerIdentifier = "test"

        currentStep = 0
        
        
        if 0:
            print "running step", currentStep
            if currentStep == 0:
                # uses training data
                self.learnFeaturesOfMembraneVoxels(voxelTrainingImageFilePath, voxelTrainingLabelFilePath, "c:\\temp\\output.tab")
                
                # uses test data, generates voxel probabilities
                self.classifyVoxels('intermediate1', 'forFaceTraining', "c:\\temp\\output.tab", self.trainingImageFilePath)

            elif currentStep == 1:
                self.classifyVoxels('intermediate2', 'voxelClassificationOnTestVolume', self.testImageFilePath)


            elif currentStep == 2:
                # uses training data
                self.learnFeaturesOfMembraneFaces(sourceType, useOriginalForWatershed, self.trainingImageFilePath, self.trainingLabelFilePath, 'faceTraining', 'forFaceTraining_ProbabilityVolume', (1, 1, 0, 0))
                
                # uses test data, uses pixel probabilities for test data
                self.findAndClassifyFaces('faceTraining', sourceType, useOriginalForWatershed, 'voxelClassificationOnTestVolume_ProbabilityVolume', (1, 0, 0))
                
            elif currentStep == 3:
                self.learnFeaturesOfMembraneFaces(sourceType, useOriginalForWatershed, self.trainingImageFilePath, self.trainingLabelFilePath, 'faceTraining', 'forFaceTraining_ProbabilityVolume', (0, 0, 1, 1))
                self.findAndClassifyFaces('faceTraining', sourceType, useOriginalForWatershed, 'voxelClassificationOnTestVolume_ProbabilityVolume', (0, 1, 1))




    def calculateDerivatives(self, volume, groupName):
        """Calculate derivatives. Nolonger using these as features"""

        # size of volume used form computing filters
        volumeShape = [9,9,9]
        
        # todo: not really using cubeOffsets list anymore so you could remove it from the code
        for i in range(len(cubeOffsets)):
            #offset = cubeOffsets[i] * 2
            offset = 1
            for coordinate in range(0,3):
                sigma = .5 + i
                #g = [[None,None],[None,None],[None,None]]
                offsetVector = [0,0,0]
                #offsetVector[coordinate] = offset
                offsetVector[coordinate] = offset + (i*2)
                #print 'offset', offset
                print "amount of blur:", sigma

                DoOG = differenceOfOffsetGaussians(volumeShape, offsetVector, sigma)

                convolvedVolume = ndimage.convolve(array(volume, dtype=float), DoOG)
                
                #self.addPersistentVolumeAndRefreshDataTree(mlab.convn(volume, DoOG, 'same'), '%s_%dGradient_blur%d' % (groupName, coordinate, i))
                self.addPersistentVolumeAndRefreshDataTree(convolvedVolume, '%s_%dGradient_blur%d' % (groupName, coordinate, i))
        


    # calculates elements of Hessian matrix
    def calculateSecondDerivatives(self, volume, groupName):
        """Calculate second derivatives. Nolonger using these as features"""

        from mlabwrap import mlab
        volumeShape = [9,9,9]
        sigma = 0.5

        for coordinateA in range(3):
            for coordinateB in range(3):
                
                offsetVectorA = [0,0,0]
                offsetVectorA[coordinateA] = 1
                
                offsetVectorB = [0,0,0]
                offsetVectorB[coordinateB] = 1
                
                DoOG_A = differenceOfOffsetGaussians(volumeShape, offsetVectorA, sigma)
                DoOG_B = differenceOfOffsetGaussians(volumeShape, offsetVectorB, sigma)
                secondDerivativeKernel = mlab.convn(DoOG_A, DoOG_B, 'same')
                self.addPersistentVolumeAndRefreshDataTree(mlab.convn(volume, secondDerivativeKernel, 'same'), '%s_%d,%d' % (groupName, coordinateA, coordinateB))

        
    
    def onCalculateDerivatives(self, event):
        """Calculate derivatives event handler"""
        if self.getCurrentVolume() == None:
            raise Exception, "no current volume is selected"
        else:
            self.calculateDerivatives(self.getCurrentVolume(), 'default')


    def onCalculateSecondDerivatives(self, event):
        """Calculate second derivatives event handler"""
        self.calculateSecondDerivatives(self.getCurrentVolume(), 'default')


    def onConvolutionTest(self, event):
        """Convolution test event handler"""
        kernel = zeros((5,5,5))
        kernel[2,2,2] = 1
        result = ndimage.convolve(array(self.getCurrentVolume(), dtype=float), kernel)
        self.addVolumeAndRefreshDataTree(result, 'ConvolutionTest')


    def onMakePointFeatureViewer(self, event):
        """Make point feature event handler"""
        if self.getCurrentVolume() == None:
            print "error: no volume selected"
        else:
            dictionary = getPointFeaturesAt(self.getCurrentVolume(), self.derivativesForPointViewerIdentifier, self, [3,3,3])
            for item in dictionary.items():
                print item[0]
            self.viewerRootNode = self.makeFeatureViewer(dictionary, 'featureSelection', "Feature Selection")


    def onMakeFaceFeatureViewer(self, event):
        """Make face feature event handler"""
        #print ""
        dictionary = getFaceFeatures(self.getCurrentBlob(), self.mainDoc.volumeDict['Original'], self.superVoxelDict)
        self.blobFeatureViewerRootNode = self.makeFeatureViewer(dictionary, 'faceFeatureSelection', "Face Feature Selection")


    def onMakeBubblePhantom(self, event):
        """Make bubble phantom event handler"""
        
        # shape of volume
        sh = (30,35,40)
        #sh = (15,15,15)
        factor = 30
        #centers = [array([10,10,10])]
        
                
        membraneBubbles = [Bubble(factor * array([.5, .5, .5]), 6, .4),
                           Bubble(factor * array([0, .4, .5]), 8, .2),
                           Bubble(factor * array([.6, .8, 1]), 7, .6),
                           Bubble(factor * array([0, .5, .5]), 7, .2),
                           Bubble(factor * array([.3, 1, .8]), 7, .4),
                           Bubble(factor * array([.5, .5, .5]), 12, .6)]
                   
        noiseBubbles = [Bubble(factor * array([.2, 1.0, .5]), 14, 4),
                        Bubble(factor * array([1.0, .2, .5]), 14, 4),
                        Bubble(factor * array([1.0, 1.0, .2]), 14, 4)]
                   
        #radius = 5

        b = BubblePhantom(membraneBubbles, noiseBubbles, sh) 
        
        v = b.createSignalVolume()
        
        #self.addVolume(255-v, 'Original')
        self.addPersistentVolumeAndRefreshDataTree(v, 'Original')
        
        #membraneLabelVolume = makeBubblePhantom(membraneBubbles, sh) > 20
        #self.addVolume(membraneLabelVolume, 'MembraneLabelVolume')
        
        

    def makeFeatureViewer(self, dictionary, nodeName, caption):
        """Make graphical feature viewer, experimental code"""
        #self.viewerRootNode = DataNode("root","group","params","value")
        
        viewerNode = DataNode(nodeName,"group",{'caption' : caption, 'position' : (700,300), 'size' : (500,700)},None)
        
        #for key in getFeaturesAt(self.getCurrentVolume(), [3,3,3]):
        #dictionary = getFeaturesAt(self.getCurrentVolume(), [3,3,3])

        listOfFeatures = []
        
        for item in dictionary.items():
            key = item[0]
            node = DataNode(key,"slider",{'caption' : key, 'min' : -300, 'max' : 300},0)
            viewerNode.addChild(node)
            listOfFeatures.append(key)
            

        featureSelection = DataNode(nodeName,"listBox",{'caption' : caption, 'items' : listOfFeatures},0)
        viewerNode.addChild(featureSelection)

        self.generateComponents(viewerNode, 0, [], None, None, None)

        return viewerNode


    def getXYImage(self, volume, displayedRegionBox):
        """Get XY image from volume for display."""

        if not(self.getValue(('particleMotionTool','displayPixelFeature'))):
            
            imageArray = ControlsFrame.getXYImage(self, volume, displayedRegionBox)
            
        else:
            
            if self.viewerRootNode != None:
            
                selectedFeature = (getNode(self.viewerRootNode, ('featureSelection',))).guiComponent.GetStringSelection()
                #print selectedFeature
               
                imageArray = zeros((displayedRegionBox.shape()[0], displayedRegionBox.shape()[1]))
                box = displayedRegionBox
                for x in range(box.cornerA[0] + borderWidthForFeatures[0]+1, box.cornerB[0] - borderWidthForFeatures[0]-1):
                    for y in range(box.cornerA[1] + borderWidthForFeatures[1]+1, box.cornerB[1] - borderWidthForFeatures[1]-1):
                        location = (x, y, box.cornerA[2])
                        
                        # if z value is out of range just return a image that has zeros in it
                        if not(isInsideVolumeWithBorder(volume, location, borderWidthForFeatures)):
                            return imageArray
                        
                        dictionary = getPointFeaturesAt(self.getCurrentVolume(), self.derivativesForPointViewerIdentifier, self, location)
                        #print dictionary
                        #print imageArray.shape
                        #print 'volume shape', volume.shape
                        #print 'box.cornerA[2]', box.cornerA[2]
                        imageArray[location[0], location[1]] = dictionary[selectedFeature]
                        #imageArray[location[0], location[1]] = 1
                
            else:
                imageArray = zeros((10,10))
                
        #return log(imageArray)
        
        return(imageArray)

        

    def old_onMakeVoxelClassificationDataFile(self, event):
        """Deprecated"""

        file = open("c:\\temp\\output.tab", "w")

        currentVolume = self.getCurrentVolume()
        sh = currentVolume.shape

        volume = numpy.zeros(sh)
        #selected x, y, and z
        
        dictionary = getPointFeaturesAt(currentVolume, self, [3,3,3])
        featureList = []
        for item in dictionary.items():
            key = item[0]
            featureList.append(key)
        
        writeOrangeNativeDataFormatHeader(file, featureList)
        
        # create a volume that has pixels turned on where the membrane is
        m = zeros(sh, numpy.uint8)
        for p in particleGroup.getAll():
            
            # todo: isInsideVolumeWithBorder should take shape as argument rather than volume
            if isInsideVolumeWithBorder(volume, p.loc, borderWidthForFeatures):
                m[p.loc[0],p.loc[1],p.loc[2]] = 1
                
                # write all true examples into tab file
                d = getPointFeaturesAt(currentVolume, self, p.loc)
                self.writeExample(file, d, True)
            
            
        self.addPersistentVolumeAndRefreshDataTree(m, 'MembraneVoxel')
        membraneVoxelVolume = self.getVolume('MembraneVoxel')
        
        border = borderWidthForFeatures
        for x in range(border[0],sh[0]-border[0],2):
            print "%d out of %d" % (x, sh[0])
            for y in range(border[1],sh[1]-border[1],2):
                for z in range(border[2],sh[2]-border[2],2):
                    
                    d = getPointFeaturesAt(currentVolume, self, (x,y,z))
                    
                    #xG = volumes['xGradient'][x,y,z]
                    #yG = volumes['yGradient'][x,y,z]
                    #zG = volumes['zGradient'][x,y,z]
        
                    #st = structureTensor(xG,yG,zG)
                    #eigenValues = numpy.linalg.eigvals(st)
                    
                    self.writeExample(file, d, (membraneVoxelVolume[x,y,z] != 0))

                    
        
        file.close()




    def recordLocalFeatures(self,
                            inputVolumeDict,
                            labelIdentifierDict,
                            voxelTrainingImageNodePath,
                            voxelTrainingLabelNodePath,
                            voxelExamplesFilename,
                            voxelWeightDict):
        """Record local feature for each voxel into a file that the orange data mining tool can read."""


        file = open(voxelExamplesFilename, "w")

        filteredVolume = self.getPersistentObject(voxelTrainingImageNodePath)
        sh = filteredVolume.shape

        #originalVolume = self.getPersistentObject(originalVolumeNodePath)

        print "learnLocalFeatures dimensions", sh
        if 0:
            self.calculateDerivatives(filteredVolume, 'training')

        volume = numpy.zeros(sh)
        #selected x, y, and z
        
        # get point features at the arbitrary point borderWidthFeatures
        # to get a list of feature names
        dictionary = getPointFeaturesAt(inputVolumeDict, filteredVolume,
                                        'training', self, borderWidthForFeatures)
        #dictionary = testDict
        featureList = []
        for item in dictionary.items():
            key = item[0]
            featureList.append(key)
        
        writeOrangeNativeDataFormatHeader(file, featureList)

        # create a volume that has pixels turned on where the membrane is
        membraneVoxelVolume = self.getPersistentObject(voxelTrainingLabelNodePath)
        
        #self.addPersistentVolumeAndRefreshDataTree(membraneVoxelVolume, 'MembraneVoxel')
        
#        if self.balanceExamples:
#
#            print "balanceExamples==true"
#
#            membranesCount = labelIdentifierDict['membranes'].count(membraneVoxelVolume)
#            blankInnerCellCount =\
#                labelIdentifierDict['blankInnerCell'].count(membraneVoxelVolume)
#            print 'membranes count', membranesCount
#            print 'blankInnerCell count', blankInnerCellCount
#            ratio = round(float(blankInnerCellCount) / float(membranesCount))
#            print "ratio", ratio
#
#        else:
#
#            print "balanceExamples==false"


        step = 1

        countDict = {}
        countDict[str(None)] = 0
        for target in labelIdentifierDict:
            countDict[labelIdentifierDict[target].objectName] = 0
        #print "countDict initialization:", countDict

        recordedExampleCountDict = {}
        for target in labelIdentifierDict:
            recordedExampleCountDict[labelIdentifierDict[target].objectName] = 0

        border = borderWidthForFeatures
        for x in range(border[0], sh[0]-border[0], step):
            print "%d out of %d" % (x, sh[0])
            print "recorded example counts so far:", recordedExampleCountDict
            sys.stdout.flush()
            for y in range(border[1], sh[1]-border[1], step):
                for z in range(border[2], sh[2]-border[2], step):

                    className = None

                    value = membraneVoxelVolume[x,y,z]
                    for id in labelIdentifierDict:
                        if labelIdentifierDict[id].isMember(value):
                            labelIdentifier = labelIdentifierDict[id]
                            className = labelIdentifier.objectName

                    #print className
                    countDict[str(className)] += 1

                    mitochondriaProbability = voxelWeightDict['foreground']
                    NoneProbability = voxelWeightDict['background']
                    if (className == 'primaryObject' and\
                        random.random() < (mitochondriaProbability * labelIdentifier.labelWeight)) or\
                        (className != None and\
                        random.random() < (NoneProbability * labelIdentifier.labelWeight)):
                        #random.random() < 0.025:

                        # This records an example.
                        # It skips over some examples to balance the number.
                        #if not(self.balanceExamples) or\
                        #    className != 'blankInnerCell' or\
                        #    (countDict['blankInnerCell'] % ratio) == 0:
                        #if 1:

                        recordedExampleCountDict[className] += 1

                        d = getPointFeaturesAt(inputVolumeDict, filteredVolume,
                                           'training', self, (x,y,z))

                        self.writeExample(file, d, className)

        print "recorded example counts:", recordedExampleCountDict

        file.close()



    def onLearnFeaturesOfMembraneVoxels(self, event):
        """Event handler for learn features of membrane voxels"""

        dialog = wx.DirDialog(self, "Training Image Stack", os.getcwd(), style=wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            voxelTrainingImageFilePath = dialog.GetPath()
            print "Training Image Stack", dialog.GetPath()
        dialog.Destroy()

        dialog = wx.DirDialog(self, "Training Label Stack", os.getcwd(), style=wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            voxelTrainingLabelFilePath = dialog.GetPath()
            print "Training Label Stack", dialog.GetPath()
        dialog.Destroy()

        wildcard = "(*.tab)|*.tab|All files (*.*)|*.*"
        dialog = wx.FileDialog(self, "Write Examples to File", os.getcwd(), style=wx.OPEN, wildcard=wildcard)
        if dialog.ShowModal() == wx.ID_OK:
            print dialog.GetPath()
            voxelExamplesFilename = dialog.GetPath()
        dialog.Destroy()

        
        self.learnFeaturesOfMembraneVoxels(voxelTrainingImageFilePath,
                                           voxelTrainingLabelFilePath,
                                           voxelExamplesFilename)



    factor = 15.0
    #factor = 30.0
    
    membranePhantomVolumeShape = (round(1*factor), round(1.16*factor), round(1.33*factor))

    membraneBubbles1 = [Bubble(factor * array([.5, .5, .5]), 6, .4),
                   Bubble(factor * array([0, .4, .5]), 8, .2),
                   Bubble(factor * array([.6, .8, 1]), 7, .6),
                   Bubble(factor * array([0, .5, .5]), 7, .2),
                   Bubble(factor * array([.3, 1, .8]), 7, .4),
                   Bubble(factor * array([.5, .5, .5]), 12, .6)]
                   
    noiseBubbles1 = [Bubble(factor * array([.2, 1.0, .5]), 14, 4),
                Bubble(factor * array([1.0, .2, .5]), 14, 4),
                Bubble(factor * array([1.0, 1.0, .2]), 14, 4)]

    membraneBubbles2 = [Bubble(factor * array([.5, .5, .5]), 6, .4),
                   Bubble(factor * array([.4, 0, .5]), 8, .2),
                   Bubble(factor * array([.6, 1, .8]), 7, .6),
                   Bubble(factor * array([.5, 0, .5]), 7, .2),
                   Bubble(factor * array([.3, .8, 1]), 7, .4),
                   Bubble(factor * array([.5, .5, .5]), 12, .6)]


                   
    noiseBubbles2 = [Bubble(factor * array([.2, .5, 1.0]), 14, 4),
                Bubble(factor * array([.2, 1.0, .5]), 14, 4),
                Bubble(factor * array([1.0, .2, 1.0]), 14, 4)]


    membranePhantom1 = BubblePhantom(membraneBubbles1, noiseBubbles1, membranePhantomVolumeShape)
    membranePhantom2 = BubblePhantom(membraneBubbles2, noiseBubbles2, membranePhantomVolumeShape)




    def calculateBorderBlobs(self, originalVolume, originalVolumeName, watershedVolumeName, inbetweenPointsBlobName):
        """Deprecated. Generates watershed transform and blob of pixels between watershed regions, saves watershed transform and blob"""

        #self.addVolume(255-v, 'Original')
        self.addPersistentVolumeAndRefreshDataTree(originalVolume, originalVolumeName)
        
        #resizedVolume = makeEnlargedVolume(originalVolume, 2)
        
        #watershedVolume = watershed(resizedVolume, 26)
        watershedVolume = watershed(originalVolume, 26)
        self.addPersistentVolumeAndRefreshDataTree(watershedVolume, watershedVolumeName)

        blobForBorderVoxels = makeBlobFromVoxelsLabeledZero(watershedVolume, 1)

        #self.addBlobAndRefreshDataTree(blobForBorderVoxels, self.getBlobsNode(), inbetweenPointsBlobName)

        computeAdjacentValueSets(watershedVolume, blobForBorderVoxels)
        self.addPersistentBlobAndRefreshDataTree(blobForBorderVoxels, inbetweenPointsBlobName)
        
        if 0:
            listSizes = []
            for labeledPoint in blob.points():
                if len(labeledPoint.adjacentNonzeroValueSet) != 2:
                    listSizes.append(len(labeledPoint.adjacentNonzeroValueSet))
            print "list of sizes other than 2"
            print listSizes
        
        

    def splitBlobIntoFacesAndComputeSuperVoxelFeatures(self, facesNodeName, nonfacesNodeName, inbetweenPointsBlobName, membraneLabelVolumeName, watershedVolumeName):
        """Deprecated. Split blob into faces and compute super voxel features."""

        #self.onOpenDocument(None)
        #print "finished opening document"
    
        facesNode = DataNode(facesNodeName, 'type of node', None, None)
        self.getBlobsNode().addChild(facesNode)

        nonfacesNode = DataNode(nonfacesNodeName, 'type of node', None, None)
        self.getBlobsNode().addChild(nonfacesNode)

        
        #blobDict = splitBlobBasedOnAdjacentValueSet(self.mainDoc.blobDict['inbetweenPoints'])
        logStart("splitBlobBasedOnAdjacentValueSet")
        blobDict = splitBlobBasedOnAdjacentValueSet(self.getPersistentBlob(inbetweenPointsBlobName))
        logFinished("splitBlobBasedOnAdjacentValueSet")

        logStart("add blobs to tree")
       
        for key in blobDict:
            #self.mainDoc.blobDict['face_%s' % str(key)] = blobDict[key]
            #self.mainDoc.blobDict['%s' % str(key)] = blobDict[key]
            
            # faces have exactly two adjacent supervoxels. (other blobs are considered nonfaces)
            if len(key) == 2:
                self.addBlob(blobDict[key], facesNode, str(key))
            else:
                self.addBlob(blobDict[key], nonfacesNode, str(key))

    
        self.refreshGUI()

        logFinished("add blobs to tree")


        superVoxelDict = computeSuperVoxelFeatures(self.getPersistentVolume_old(watershedVolumeName))

        return (blobDict, superVoxelDict)

    def learnFeaturesOfMembraneFaces(self, sourceType, useOriginalForWatershed, trainingImageFilePath, trainingLabelFilePath, generatedDataIdentifier, volumeForWatershedName, doPart):
        """Deprecated. Learn features of membrane faces."""

        if sourceType == 'phantom':
            membranePhantom = self.trainingMembranePhantom
            salientLabelValue = membranePhantom.salientLabelValue
        elif sourceType == 'imageFile':
            salientLabelValue = 1
        else:
            raise Exception, "invalid type %s" % sourceType                



        logStart("learnFeaturesOfMembraneFaces")

        if len(doPart) != 4:
            raise Exception, "doPart should be a list of 4 boolean values"

        prefix = generatedDataIdentifier + "_"
        membraneLabelVolumeName = prefix+'MembraneLabelVolume'
        originalVolumeName = prefix+'Original'

        if doPart[0]:

            if sourceType == 'phantom':
                originalVolume = self.makeEnlargedPhantom(membranePhantom)
            elif sourceType == 'imageFile':
                # load training image data from disk
                originalVolume = loadImageStack(trainingImageFilePath, None)
            else:
                raise Exception, "invalid type %s" % sourceType                

            if useOriginalForWatershed:
                volumeForWatershed = originalVolume
            else:
                volumeForWatershed = self.getPersistentVolume_old(volumeForWatershedName)


            # generates watershed transform and blob of pixels between watershed regions, saves watershed transform and blob
            self.calculateBorderBlobs(volumeForWatershed, originalVolumeName, prefix+'Watershed', prefix+'inbetweenPoints')  

            self.calculateDerivatives(self.getPersistentVolume_old(originalVolumeName), generatedDataIdentifier)


        if doPart[1]:

            if sourceType == 'phantom':
                #todo: enlarge the volume before thresholding rather than after
                membraneLabelVolume = membranePhantom.createSignalLabelVolume()
                #membraneLabelVolume = makeEnlargedVolume(membraneLabelVolume, 2)
                membraneLabelVolume = resizeVolume(membraneLabelVolume, (2, 2, 2))
            elif sourceType == 'imageFile':
                # load membrane label volume from disk
                membraneLabelVolume = loadImageStack(trainingLabelFilePath, None)
            else:
                raise Exception, "invalid type %s" % sourceType

            self.addPersistentVolumeAndRefreshDataTree(membraneLabelVolume, membraneLabelVolumeName)

        if doPart[2]:

            # splits the blob of pixels that are inbetween watershed regions to produce faces
            blobDict, superVoxelDict = self.splitBlobIntoFacesAndComputeSuperVoxelFeatures(prefix+'faces', prefix+'nonfaces', prefix+'inbetweenPoints', prefix+'MembraneLabelVolume', prefix+'Watershed')
        
            #self.onMakePointFeatureViewer(None)
            #self.onMakeFaceFeatureViewer(None)

            # set blob colors
            for key in blobDict:
                value = calculateAverageValue(blobDict[key], self.getPersistentVolume_old(membraneLabelVolumeName))
                blobDict[key].setColor(faceBlobColorBasedOnAverageValue(value, salientLabelValue))
        
        
        if doPart[3]:
            # make face classification data file
            logStart("writeFaceClassificationTrainingData")
            self.writeFaceClassificationTrainingData(generatedDataIdentifier, "c:\\temp\\%sfaceClassificationTrainingData.tab" % prefix, superVoxelDict, prefix+'faces', prefix+'Original', volumeForWatershedName, membraneLabelVolumeName, salientLabelValue)
            logFinished("writeFaceClassificationTrainingData")

        logFinished("learnFeaturesOfMembraneFaces")        


    def onFindAndClassifyFaces(self, event):
        pass

    def makeEnlargedPhantom(self, membranePhantom):
            """Deprecated. Make enlarge phantom."""
            v = membranePhantom.createVolume()
            #v = makeEnlargedVolume(v, 2)
            v = resizeVolume(v, (2, 2, 2))
            return v
    
    def findAndClassifyFaces(self, inputFileIdentifier, sourceType, useOriginalForWatershed, volumeForWatershedName, doPart):
        """Deprecated. Find and classify faces."""

        logStart("findAndClassifyFaces")
        
        
        if len(doPart) != 3:
            raise Exception, "doPart should be a list of 3 boolean values"

        generatedDataIdentifier = 'test'
        prefix = generatedDataIdentifier + "_"
        originalVolumeName = prefix+'Original'


        if doPart[0]:
        
            if sourceType == 'phantom':
                membranePhantom = self.testMembranePhantom
                originalVolume = self.makeEnlargedPhantom(membranePhantom)
            elif sourceType == 'imageFile':
                #self.onLoadImageStack(None)
                # todo: the volume should come from the data tree rather than this dictionary and the dictionary for volumes should nolonger exist
                #originalVolume = self.getPersistentVolume_old('LoadedVolume')
                originalVolume = loadImageStack(self.testImageFilePath, None)            
                self.addPersistentVolumeAndRefreshDataTree(originalVolume, originalVolumeName)


            else:
                raise Exception, "invalid type %s" % sourceType

            # generates watershed transform and blob of pixels between watershed regions, saves watershed transform and blob
            # todo: originalVolumeName should be something like forWatershedVolumeName
            if useOriginalForWatershed:
                volumeForWatershed = originalVolume
            else:
                volumeForWatershed = self.getPersistentVolume_old(volumeForWatershedName)
            
            self.calculateBorderBlobs(volumeForWatershed, originalVolumeName, prefix+'Watershed', prefix+'inbetweenPoints')  

            self.calculateDerivatives(self.getPersistentVolume_old(originalVolumeName), generatedDataIdentifier)


        if doPart[1]:

            # splits the blob of pixels that are inbetween watershed regions to produce faces
            blobDict, superVoxelDict = self.splitBlobIntoFacesAndComputeSuperVoxelFeatures(prefix+'faces', prefix+'nonfaces', prefix+'inbetweenPoints', prefix+'MembraneLabelVolume', prefix+'Watershed')
        
            #self.onMakePointFeatureViewer(None)
            #self.onMakeFaceFeatureViewer(None)
        
        if doPart[2]:
            # read face classification data file
            # todo: filter blobDict so it only has faces with exactly two adjacencies - or use faces in the data tree that you have already filtered in this way
            faceDict = {}
            for key in blobDict:
                if len(key) == 2:
                    faceDict[key] = blobDict[key]
            # todo: remove the volumeDict and use the data tree instead
            self.classifyFaces(inputFileIdentifier, faceDict, self.getPersistentVolume_old(originalVolumeName), self.getPersistentVolume_old(volumeForWatershedName), superVoxelDict)

        logFinished("findAndClassifyFaces")        


    def classifyFaces(self, inputFileIdentifier, faceBlobDict, volume, probabilityVolume, superVoxelDict):
        """Deprecated. Classify faces nolonger maintained."""

        #tree = orngTree.TreeLearner(storeNodeClassifier = 0, storeContingencies=0, storeDistributions=1, minExamples=5, ).instance()
        tree = orngTree.TreeLearner(storeNodeClassifier = 0, storeContingencies=0, storeDistributions=1, minExamples=150, ).instance()
        gini = orange.MeasureAttribute_gini()
        tree.split.discreteSplitConstructor.measure = tree.split.continuousSplitConstructor.measure = gini
        tree.maxDepth = 5
        tree.split = orngEnsemble.SplitConstructor_AttributeSubset(tree.split, 3)

        data = orange.ExampleTable("c:\\temp\\%s_faceClassificationTrainingData.tab" % inputFileIdentifier)
        #forest = orngEnsemble.RandomForestLearner(data, trees=50, name="forest", learner=tree)

        print "data.domain.attributes", data.domain.attributes, len(data.domain.attributes) 
        print "data.domain.variables", data.domain.variables, len(data.domain.variables)

        #forest = orngEnsemble.RandomForestLearner(data, trees=50, name="forest")
        forest = orngEnsemble.RandomForestLearner(data, trees=300, name="forest")
        
        print "Possible classes:", data.domain.classVar.values

        #print probabilities
        if False:
            for i in range(len(data)):
                p = forest(data[i], orange.GetProbabilities)
                print "%d: %5.10f (originally %s)" % (i+1, p[1], data[i].getclass())

        
        for key in faceBlobDict:
            
            faceBlob = faceBlobDict[key]
            
            #dictionary = getFeaturesAt(self.getCurrentVolume(), self.mainDoc.volumeDict, (x,y,z))
            #dictionary = getFaceFeatures('training', faceBlob, volume, superVoxelDict, self.mainDoc.volumeDict)
            dictionary = getFaceFeatures('test', faceBlob, volume, probabilityVolume, superVoxelDict, self)
            list = []
            #print "dictionary.items()", len(dictionary.items()), dictionary.items()
            for item in dictionary.items():
                value = item[1]
                list.append(value)
            list.append('False') # todo: what would happen if you used True here
    
            example = orange.Example(data.domain, list)
            p = forest(example, orange.GetProbabilities)    
            
            # todo: this should be checked once immediately after the training data file is read rather than checked here
            if len(p) == 1:
                raise Exception, "There is only one class in the data. There should be two classes like true and false."
            
            faceBlob.setColor([200 - (p[1] * 200), p[1] * 200, 0]) 
            faceBlob.setProbability(p[1])


    def writeFaceClassificationTrainingData(self, identifier, filename, superVoxelDict, facesNodeName, originalVolumeName, probabilityVolumeName, membraneLabelVolumeName, salientLabelValue):
        """Deprecated. Write face classification training data."""

        file = open(filename, "w")
        
        sh = self.getPersistentVolume_old(originalVolumeName).shape

        volume = numpy.zeros(sh)
        #selected x, y, and z
        
        dummyDictionary = makeFaceFeaturesDictionary()
        featureList = []
        for item in dummyDictionary.items():
            key = item[0]
            featureList.append(key)
        
        writeOrangeNativeDataFormatHeader(file, featureList)
        
        facesNode = getNode(self.getBlobsNode(), (facesNodeName,))
        for faceNode in facesNode.children:
            faceBlob = faceNode.object
            d = getFaceFeatures(identifier, faceBlob, self.getPersistentVolume_old(originalVolumeName), self.getPersistentVolume_old(probabilityVolumeName), superVoxelDict, self)
            
            # assume it is a salient face if average value is greater than a certain number
            averageValue = calculateAverageValue(faceBlob, self.getPersistentVolume_old(membraneLabelVolumeName))
            self.writeExample(file, d, faceBlobSalientBasedOnAverageValue(averageValue, salientLabelValue))
            #print "faceBlobSalientBasedOnAverageValue(averageValue)"
            #print faceBlobSalientBasedOnAverageValue(averageValue)
        
        file.close()



    def onClassifyVoxelsOfImageStack(self, event):
        """Event handler for classify voxels of image stack."""

        dialog = wx.DirDialog(self, "Choose Image Stack for Pixel Classification", os.getcwd(), style=wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            inputImageStackPath = dialog.GetPath()
        dialog.Destroy()

        wildcard = "(*.tab)|*.tab|All files (*.*)|*.*"
        dialog = wx.FileDialog(self, "Choose Examples File", os.getcwd(), style=wx.OPEN, wildcard=wildcard)
        if dialog.ShowModal() == wx.ID_OK:
            print dialog.GetPath()
            voxelExamplesFilename = dialog.GetPath()
        dialog.Destroy()


        self.classifyVoxels('intermediate2', 'voxelClassificationOnTestVolume', voxelExamplesFilename, inputImageStackPath)

        

    def classifyVoxels(self,
                       intermediateDataIdentifier,
                       outputNodePath,
                       voxelExamplesFilename,
                       inputVolumeDict,
                       inputImageNodePath):
        """
        Classify voxels using random forest
        Parameters:
        intermediateDataIdentifier: text label that will be assigned to intermediate data files
        outputNodePath: specifies the node where output will be saved
        voxelExamplesFilename: examples that generate the classifier
        inputVolumeDict: set of input volumes, filters are not run on them
        inputImageNodePath: input volume (that does have filters run on it)
        """

        data = orange.ExampleTable(voxelExamplesFilename)
        
        if len(data) == 0:
            raise Exception, "There are zero examples in the training data."

        #minimumExamples = len(data) / 5
        #minimumExamples = len(data) / 40 # BMC Bioinformatics, used for cerebellum
        minimumExamples = len(data) / 120 # BMC Bioinformatics, used for dentate gyrus test
        logging.info("minimumExamples: %d" % minimumExamples)        

        #originalVolume = self.getPersistentObject(originalVolumeNodePath)
        inputVolume = self.getPersistentObject(inputImageNodePath)
        
        self.calculateDerivatives(inputVolume, intermediateDataIdentifier)

        tree = orngTree.TreeLearner(storeNodeClassifier = 0,
                                    storeContingencies=0,
                                    storeDistributions=1,
                                    minExamples=minimumExamples, ).instance()
        gini = orange.MeasureAttribute_gini()
        tree.split.discreteSplitConstructor.measure = \
         tree.split.continuousSplitConstructor.measure = gini
        #tree.maxDepth = 5
        logging.info("tree.maxDepth: %d" % tree.maxDepth)
        tree.maxDepth = 40

        split = 3
        logging.info("tree.split: %d", split)
        tree.split = orngEnsemble.SplitConstructor_AttributeSubset(tree.split, split)

        logging.info("creating random forest")
        logging.info("number of trees: %d" % self.numberOfTrees)
        forest = orngEnsemble.RandomForestLearner(data, trees=self.numberOfTrees,
                                                  name="forest", learner=tree)
        logging.info("finished creating random forest")


        print "Possible classes:", data.domain.classVar.values
        if False:
            for i in range(len(data)):
                p = forest(data[i], orange.GetProbabilities)
                print "%d: %5.10f (originally %s)" % (i+1, p[1], data[i].getclass())

        print "number of examples:", len(data)
        print "minimumExamples:", minimumExamples
        
        count = 0

        v = []
        logV = []

        for i in range(len(data.domain.classVar.values)):
            v.append(zeros(inputVolume.shape))
            logV.append(zeros(inputVolume.shape))
        #self.addPersistentVolumeAndRefreshDataTree(v,
        #                                outputNodePath + '_ProbabilityVolume')

        logging.info("classifying voxels")

        for x in range(borderWidthForFeatures[0], v[0].shape[0]-borderWidthForFeatures[0]):
            print x, "out of", v[0].shape[0]-borderWidthForFeatures[0]-1
            sys.stdout.flush()
            for y in range(borderWidthForFeatures[1],
                           v[0].shape[1]-borderWidthForFeatures[1]):
                for z in range(borderWidthForFeatures[2],
                               v[0].shape[2]-borderWidthForFeatures[2]):
                    
                    
                    dictionary = getPointFeaturesAt(inputVolumeDict, inputVolume,
                                        intermediateDataIdentifier, self, (x,y,z))
                    valueList = []
                    for item in dictionary.items():
                        value = item[1]
                        valueList.append(value)
                    #valueList.append('False') # todo: what would happen if you used True here
                    valueList.append(data.domain.classVar.values[0])
                    example = orange.Example(data.domain, valueList)
                    p = forest(example, orange.GetProbabilities)    
                    
                    for i in range(len(p)):
                        v[i][x,y,z] = p[i]
                        logV[i][x,y,z] = numpy.log(p[i])

                    count += 1

        logging.info("finished classifying voxels")

        parentNode = getNode(self.mainDoc.dataRootNode, outputNodePath[0:-1])

        outputNode = GroupNode(outputNodePath[-1])
        logOutputNode = GroupNode(outputNodePath[-1] + '_LogProbabilityVolume')
        parentNode.addChild(outputNode)
        parentNode.addChild(logOutputNode)

        for i in range(len(v)):

            volume = v[i]
            volumeNode = Node(data.domain.classVar.values[i])
            volumeNode.object = volume
            outputNode.addChild(volumeNode)

        for i in range(len(logV)):

            logVolume = logV[i]
            volumeNode = Node(str(i))
            volumeNode.object = logVolume
            logOutputNode.addChild(volumeNode)

        self.mainDoc.dataTree.writeSubtree(outputNodePath)


    def classifyVoxelsNN(self,
                         intermediateDataIdentifier,
                         outputDataIdentifier,
                         voxelExamplesFilename,
                         inputImageNodePath):
        """Classify using neural network. Not yet implemented."""

        inputVolume = self.getPersistentObject(inputImageNodePath)
        
        network = NeuralNetwork(inputVolume)
        #network.input = inputVolume
        network.update()

        #v = zeros(inputVolume.shape)


        self.addPersistentVolumeAndRefreshDataTree(network.getOutput(),
                                                   outputDataIdentifier)


    def setPointFeatureSliders(self, location):
        """Set point feature sliders."""

        # todo: rename self.viewerRootNode to self.pointFeatureViewerRootNode
        viewerNode = self.viewerRootNode
        loc = numpy.int_(location)
        dictionary = getPointFeaturesAt(self.getCurrentVolume(), self, loc)
        self.setFeatureSliders(viewerNode, dictionary)
        
    def setBlobFeatureSliders(self, blob):
        """Set blob feature sliders."""

        viewerNode = self.blobFeatureViewerRootNode
        dictionary = getFaceFeatures(blob, self.mainDoc.volumeDict['Original'], self.superVoxelDict)
        self.setFeatureSliders(viewerNode, dictionary)


    # todo: function is not written yet
    def calculateDistributionFeatures(faceBlob, volume):
        print ""
        
        

    def setFeatureSliders(self, viewerNode, dictionary):
        """Set GUI feature sliders. Experimental."""
        #loc = numpy.int_(location)
        #dictionary = getFeaturesAt(self.getCurrentVolume(), self.mainDoc.volumeDict, loc)
        #if dictionary != None:
        for item in dictionary.items():
            key = item[0]
            value = item[1]
            #'featuresAtPoint',key
            
            if value < self.getSliderMin(viewerNode, (key,)):
                self.setSliderMin(viewerNode, (key,), value)

            if value > self.getSliderMax(viewerNode, (key,)):
                self.setSliderMax(viewerNode, (key,), value)
                            
            #(getNode(self.viewerRootNode, (key,))).set(value)
            #(getNode(self.settingsTree, ('featuresAtPoint',key))).set(value)
            #viewerNode.set(value)
            (getNode(viewerNode, (key,))).set(value)


    def printBlobNameAtMouseLocation(self, event):
        """Print name of the blob that's at the mouse location. Experimental."""

        # display information about the blob at this point
        if (getNode(self.settingsTree, ('particleMotionTool','drawBlobs'))).get():
            loadedVolumeLocation = self.screenXYToLoadedVolumeXYZ((event.X, event.Y))
            #blob = self.mainDoc.blobDict['InbetweenPoints']
            #blob = getNode(self.getBlobsNode(), ('InbetweenPoints',)).object
            #print "value %s" % str(at(self.getCurrentVolume(), loadedVolumeLocation))
            
            watershedLabel = at(self.mainDoc.volumeDict['Watershed1'], loadedVolumeLocation)
            print "watershed label %s" % str(watershedLabel)

            print "size %d" % self.superVoxelDict[watershedLabel].size()

            facesNode = getNode(self.getBlobsNode(), ('faces',))
            for childNode in facesNode.children:
                blob = childNode.object
                for labeledPoint in blob.points():
                    if (loadedVolumeLocation.round() == labeledPoint.loc).all():
                        treeControl = getNode(self.settingsTree, ('particleMotionTool','dataTree')).guiComponent
                        itemId = childNode.guiComponent
                        treeControl.SelectItem(itemId)
                        self.setBlobFeatureSliders(blob)


    def writeExample(self, file, dictionary, classification):
        """Write example to a form that the orange data mining tool can read."""

        for item in dictionary.items():
            value = item[1]
            file.write("%f\t" % value)
                        
        #file.write("%s" % particleGroup.containsIntegerPoint((x,y,z)))
        file.write("%s" % classification)
        file.write("\n")




class FaceBlob(Blob):
    """Deprecated"""
    def __init__(self):
        Blob.__init__(self)
        self.adjacentSuperVoxelIDs = None
        #self.averageValueFromTrainingLabelVolume = None


        

def getPointFeaturesAt(inputVolumeDict, volume, derivativeVolumesIdentifier, gui, point):
    """Get features (for classification) at a particular point"""

    # f is dictionary of features
    
    if not(isInsideVolumeWithBorder(volume, point, borderWidthForFeatures)):
        raise Exception, 'The point %s is not inside the volume enough. In needs to be away from the border by %d pixels for x, %d pixels for y, and %d pixels for z. Volume shape: %s' % (point, borderWidthForFeatures[0], borderWidthForFeatures[1], borderWidthForFeatures[2], str(volume.shape))
    
    f = odict()


    #sizeIdentifiers = ('3x3x3', '5x5x5', '7x7x7')
    sizeIdentifiers = ('(3)', '(5)', '(7)')
    v = [None, None, None] 
    
    #for i in range(3):
    for i in range(1):
        size = i+1
        v = volume[point[0]-size:point[0]+size,point[1]-size:point[1]+size,point[2]-size:point[2]+size]
    
    
        # experimental features
        if 0:

            #i = 0
            #todo: note that getVolume may be a slow operation
            xGVolume = gui.getVolume('%s_0Gradient_blur%d' %\
                                     (derivativeVolumesIdentifier, i))
            xG = at(xGVolume, point)
            yGVolume = gui.getVolume('%s_1Gradient_blur%d' %\
                                     (derivativeVolumesIdentifier, i))
            yG = at(yGVolume, point)
            zGVolume = gui.getVolume('%s_2Gradient_blur%d' %\
                                     (derivativeVolumesIdentifier, i))
            zG = at(zGVolume, point)

        # experimental features
        if 0:

            if i == 0:
                f['grayValue'] = at(volume, point)
                #'differenceOfGaussian'
                f['gradientMagnitude'] = sqrt(pow(xG,2) + pow(yG,2) + pow(zG,2))
            
            
        # experimental features
        if 0:

            stAtSelectedPoint = structureTensor(xG,yG,zG)
        
            sortedEigAtSelectedPoint = numpy.linalg.eigvals(stAtSelectedPoint)
            sortedEigAtSelectedPoint.sort()

            prefix = sizeIdentifiers[i] + '_'
        
            f[prefix + 'eig0'] = sortedEigAtSelectedPoint[0]
            f[prefix + 'eig1'] = sortedEigAtSelectedPoint[1]
            f[prefix + 'eig2'] = sortedEigAtSelectedPoint[2]
    
            values = v.flatten(1)
            #print "i", i, "values", values
    
            moments = statistics.moments(values)
            f[prefix + 'mean'] = moments[0]
            f[prefix + 'standardDeviation'] = moments[1]
            f[prefix + 'thirdMoment'] = moments[2]
            f[prefix + 'fourthMoment'] = moments[3]
        
            quantiles = statistics.sortAndReturnQuantiles(values)
            f[prefix + 'minimum'] = quantiles[0]
            f[prefix + '0.25-quantile'] = quantiles[1]
            f[prefix + 'median'] = quantiles[2]
            f[prefix + '0.75-quantile'] = quantiles[3]
            f[prefix + 'maximum'] = quantiles[4]

    
    if 1:

        for (key, value) in inputVolumeDict.items():

            inputVolume = inputVolumeDict[key]
            #print "inputs", inputVolumeDict.keys()

            # experimental features
            if 0:
                for xOffset in range(-9, 10, 3):
                    for yOffset in range(-9, 10, 3):
                        f['inputVolume_%s_%d_%d' % (key, xOffset, yOffset)] =\
                            inputVolume[point[0] + xOffset, point[1] + yOffset, point[2]]

            #windowSize = 3
            #windowSize = 5

            scale = 1

            if key == 'originalVolume':
                windowSize = 6 * scale
            else:
                windowSize = 2 * scale


            step = 1 * scale

            #print "point"
            #print point[0]
            #print point[1]
            #print point[2]
            #print inputVolume.shape

            for xOffset in range(-(windowSize+1), windowSize, step):
                for yOffset in range(-(windowSize+1), windowSize, step):
                    f['focus_%s_%d_%d' % (key, xOffset, yOffset)] =\
                        inputVolume[point[0] + xOffset, point[1] + yOffset, point[2]]


        # experimental features
        if 0:
            for xOffset in range(-(windowSize+1), windowSize, step):
                for yOffset in range(-(windowSize+1), windowSize, step):
                    f['xG_%d_%d' % (xOffset, yOffset)] =\
                        xGVolume[point[0] + xOffset, point[1] + yOffset, point[2]]
                    f['yG_%d_%d' % (xOffset, yOffset)] =\
                        yGVolume[point[0] + xOffset, point[1] + yOffset, point[2]]

    # return features
    return f


    

def makeFaceFeaturesDictionary():
    """Deprecated. Make face features dictionary."""

    list = ['logNumberOfVoxels',
                                          'logDifference',


                                          'voxelProbability_mean',
                                          'voxelProbability_standardDeviation',
                                          'voxelProbability_thirdMoment',
                                          'voxelProbability_fourthMoment',
                                          'voxelProbability_minimum',
                                          'voxelProbability_0.25-quantile',
                                          'voxelProbability_median',
                                          'voxelProbability_0.75-quantile',
                                          'voxelProbability_maximum']
    return OrderedDictionaryFixedKeyList(list)

                                           
                                           
def getFaceFeatures(gradientIdentifier, faceBlob, originalVolume, probabilityVolume, superVoxelDict, gui):
    """Deprecated. Get face features."""
    # f is dictionary of features
    
    f = makeFaceFeaturesDictionary()
    
    #self.mainDoc.blobDict['inbetweenPoints'][faceIdentifier]
    
    f['logNumberOfVoxels'] = log(faceBlob.numPoints())
    #f['grayValue'] = at(volume, point)
    
    if len(faceBlob.adjacentSuperVoxelIDs) != 2:
        raise Exception, "The face blob with id %s does not have exactly two adjacent super voxels." % faceBlob.adjacentSuperVoxelIDs
    
    
    sv = [None, None]
    i = 0
    for superVoxelID in faceBlob.adjacentSuperVoxelIDs:
        sv[i] = superVoxelDict[superVoxelID]
        i += 1
    
    f['logDifference'] = log(1 + abs(sv[0].size() - sv[1].size()))

    xGradientVolume = gui.getPersistentVolume_old(gradientIdentifier + "_" + '0Gradient_blur%d' % 1)
    yGradientVolume = gui.getPersistentVolume_old(gradientIdentifier + "_" + '1Gradient_blur%d' % 1)
    zGradientVolume = gui.getPersistentVolume_old(gradientIdentifier + "_" + '2Gradient_blur%d' % 1)

    grayValues = []
    gradientMagnitudes = []
    voxelProbabilities = []
    for point in faceBlob.points():

        grayValues.append(at(originalVolume, point.loc))

        xG = at(xGradientVolume, point.loc)
        yG = at(yGradientVolume, point.loc)
        zG = at(zGradientVolume, point.loc)
        gradientMagnitudes.append(sqrt(pow(xG,2) + pow(yG,2) + pow(zG,2)))

        voxelProbabilities.append(at(probabilityVolume, point.loc))

    valueTypeDict = {}
    #valueTypeDict['grayValue'] = grayValues
    #valueTypeDict['gradientMagnitude'] = gradientMagnitudes 
    valueTypeDict['voxelProbability'] = voxelProbabilities

    for key in valueTypeDict:
        
        prefix = key + "_"
        
        values = valueTypeDict[key]

        moments = statistics.moments(values)
        f[prefix + 'mean'] = moments[0]
        f[prefix + 'standardDeviation'] = moments[1]
        f[prefix + 'thirdMoment'] = moments[2]
        f[prefix + 'fourthMoment'] = moments[3]
    
        quantiles = statistics.sortAndReturnQuantiles(values)
        f[prefix + 'minimum'] = quantiles[0]
        f[prefix + '0.25-quantile'] = quantiles[1]
        f[prefix + 'median'] = quantiles[2]
        f[prefix + '0.75-quantile'] = quantiles[3]
        f[prefix + 'maximum'] = quantiles[4]

   
    return f


def makeBlobFromVoxelsLabeledZero(volume, widthOfBorderToIgnore):
    """Make blob object (set of points) from voxels labeled zero in volume."""

    w = widthOfBorderToIgnore
    blob = Blob()
    for x in range(w, volume.shape[0]-w):
        for y in range(w, volume.shape[1]-w):
            for z in range(w, volume.shape[2]-w):
                if volume[x,y,z] == 0:
                    blob.points().append(LabeledPoint((x,y,z)))
    return blob


def computeSuperVoxelFeatures(watershedVolume):
    """Deprecated. Compute supervoxel features."""

    print "computing super voxel features"
    superVoxelDict = {}
    for x in range(watershedVolume.shape[0]):
        for y in range(watershedVolume.shape[1]):
            for z in range(watershedVolume.shape[2]):
                superVoxelIndex = watershedVolume[x,y,z]
                if superVoxelIndex in superVoxelDict:
                    superVoxelDict[superVoxelIndex].addToSize(1)
                else:
                    superVoxelDict[superVoxelIndex] = Blob()
                    superVoxelDict[superVoxelIndex].setSize(0)
                    
    return superVoxelDict




def splitBlobBasedOnAdjacentValueSet(blob):
    """Depricated. Return a dictionary of blobs, each has an index that is based on the set of adjacent regions (if the point is adjacent to region 2 and 3 for example, it's dictionary entry key will be a set with elements 2 and 3)"""
    dictionary = {}
    
    for labeledPoint in blob.points():
        
        # valueSet is used as a key
        
        valueSet = frozenset(labeledPoint.adjacentNonzeroValueSet)
        
        # create new face if needed
        if not(valueSet in dictionary):
            faceBlob = FaceBlob()
            faceBlob.adjacentSuperVoxelIDs = valueSet
            dictionary[valueSet] = faceBlob #[] #Blob()
        
        
        # todo: it's sort of redundant to store the set specifying adjacencies in every labeled point considering all of them (in the blob) have the same adjacent blobs 
        dictionary[valueSet].points().append(labeledPoint)
        
    
    return dictionary


   
def computeAdjacentValueSets(volume, blob):
    """
    Deprecated
    Computes the adjacent values that are not zero, for each point in the blob
    Stores the result in the labeled points of the blob
    """
    for labeledPoint in blob.points():
        computeAdjacentValueSet(volume, labeledPoint)

def computeAdjacentValueSet(volume, labeledPoint):
    """Deprecated"""
    for offset in adjacentOffsets:
        p = labeledPoint.loc + offset
        #labeledPoint.adjacentNonZeroPoints = []
        #print p

        if at(volume, p) != 0:
            #print '--------------------'
            #print p
            labeledPoint.adjacentNonzeroValueSet.add(at(volume,p))

def calculateAverageValue(faceBlob, binaryLabelVolume):
    """Deprecated."""
    total = 0.0
    
    for labeledPoint in faceBlob.points():
        total += float(at(binaryLabelVolume, labeledPoint.loc))
        
    return float(total) / float(len(faceBlob.points()))


def faceBlobColorBasedOnAverageValue(value, salientLabelValue):
    """Deprecated"""

    if faceBlobSalientBasedOnAverageValue(value, salientLabelValue):
        return [0, 200, 0] # bright green
    else:
        return [100, 0, 100] # dark purple 


def faceBlobSalientBasedOnAverageValue(value, salientLabelValue):
    """Deprecated"""

    # the face is considered salient if 50% of pixels or more are marked salient
    if value > (0.5 * salientLabelValue):
        return True # bright green
    
    # if the face is not salient:
    else:
        return False # dark purple 
        

def writeOrangeNativeDataFormatHeader(file, featureList):
        """Write header for the orange data miniting tool file format."""
    
        for featureName in featureList:
            file.write("%s\t" % featureName)
        file.write("is_membrane\n")

        for featureName in featureList:
            file.write("c\t")
        file.write("discrete\n")

        for featureName in featureList:
            file.write("\t")
        file.write("class\n")


def startClassificationControlsFrame():
    """Start GUI. Experimental."""

    app = wx.PySimpleApp()
    #frm = ClassificationControlsFrame(makeDefaultGUITree())
    frm = ClassificationControlsFrame(makeClassifyGUITree())
    frm.Show()
    
        
    app.MainLoop()


