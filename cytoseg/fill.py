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

# ITK level set operation support


import warnings

print "loading itk in fill.py"
try:
    import itk
except ImportError:
    warnings.warn("itk module is not installed")

print "importing sys"
from sys import argv, stderr, exit

print "importing copy"
import copy as copy_module

print "importing numpy"
from numpy import *

print "importing contour_processing"
from contour_processing import *

print "importing segmentation"
from segmentation import floodFill

print "importing tree"
from tree import getNode

print "importing active_contour"
from active_contour import *

import erosion

#from default_path import *

import os

def numpyToItkPoint(point):

    return [point[2], point[1], point[0]]
    #return point
    

def fastMarch(image1, center, contour, inputVolume):
    """
    Fast march. The fast march is seeded by every point of the contour.
    Returns fast march result.
    """

    InternalPixelType = itk.F
    Dimension = 3
    ImageType = itk.Image[InternalPixelType, Dimension]
    converter = itk.PyBuffer[ImageType]
    IT = itk.Image.F3
    #img = IT.New(Regions=[inputVolume1.shape[2], inputVolume1.shape[1], inputVolume1.shape[0]])
    #img.Allocate()
    #img.FillBuffer(0)
    InternalImageType = IT
    OutputImageType = IT
    # test code
    itk.write(image1, "/tmp/hello1.nrrd")
    itk.write(image1, "/tmp/hello2.nrrd")
    # end test code
    seedPosition = numpyToItkPoint(center)

    argv[1:] = ["O:\\images\\HPFcere_vol\\HPF_rotated_tif\\median_then_gaussian_8bit_classified_pixels\\median_then_gaussian_8bit_classified_pixels.nrrd", "o:\\temp\\fastmarch3d.nrrd", 81, 114, 1.0, -0.5, 3.0, 0.4, 0.4]

    if( len(argv) < 10 ):
      print >> stderr, """Missing Parameters
    Usage: FastMarchingImageFilter.py inputImage  outputImage seedX seedY Sigma SigmoidAlpha SigmoidBeta TimeThreshold StoppingValue"""
      exit(1)
      
    
    
    CastFilterType = itk.RescaleIntensityImageFilter[ 
                                InternalImageType, 
                                OutputImageType ]
    
    SmoothingFilterType = itk.CurvatureAnisotropicDiffusionImageFilter[ 
                                InternalImageType, 
                                InternalImageType ]
    
    smoothing = SmoothingFilterType.New()
    
    GradientFilterType = itk.GradientMagnitudeRecursiveGaussianImageFilter[
                                InternalImageType, 
                                InternalImageType ]
    
    SigmoidFilterType = itk.SigmoidImageFilter[
                                InternalImageType, 
                                InternalImageType ]
    
    gradientMagnitude = GradientFilterType.New();
    sigmoid = SigmoidFilterType.New()
    
    sigmoid.SetOutputMinimum(  0.0  )
    sigmoid.SetOutputMaximum(  1.0  )
    
    FastMarchingFilterType = itk.FastMarchingUpwindGradientImageFilter[ InternalImageType, 
                                InternalImageType ]

    NodeType = itk.LevelSetNode[InternalPixelType, Dimension]
    NodeContainer = itk.VectorContainer[itk.UI, NodeType]

    
    stopPoints = NodeContainer.New()
    for pointObject in contour.points():
        stopPointNode = NodeType()
        stopPointNode.SetValue(0) #todo: is this needed
        stopPointNode.SetIndex(numpyToItkPoint(pointObject.loc))
        stopPoints.InsertElement(0, stopPointNode)

    fastMarching = FastMarchingFilterType.New()
    fastMarching.SetTargetReachedModeToOneTarget()
    fastMarching.SetTargetOffset(0)
    fastMarching.SetTargetPoints(stopPoints)

    fastMarching.SetInput(image1)
    
    sigma = float( argv[5] )
    
    gradientMagnitude.SetSigma(  sigma  )
    
    alpha =  float( argv[6] )
    beta  =  float( argv[7] )
    
    
    seeds = NodeContainer.New()
    
    
    
    node = NodeType()
    seedValue = 0.0
    
    node.SetValue( seedValue )
    node.SetIndex( seedPosition )
    
    seeds.Initialize();
    seeds.InsertElement( 0, node )
    
    fastMarching.SetTrialPoints(  seeds  );
    
    
    fastMarching.SetOutputSize(inputVolume.GetBufferedRegion().GetSize())
    
    stoppingTime = float( argv[9] )
    
    fastMarching.SetStoppingValue(  stoppingTime  )
    
    print "update"
    fastMarching.Update()
    print "finished update"
    resultItkArray = fastMarching.GetOutput()
    return resultItkArray



def shellActiveContourWrapper(image1, seedList, contour, inputVolume):
    """
    Performs level set operation that fills in a shell-shaped object.
    Parameters:
    image1: volume to guide the level set operation
    seedList: list of points from which operation will start
    contour: deprecated parameter
    inputVolume: deprecated parameter
    """

    InternalPixelType = itk.F
    Dimension = 3
    ImageType = itk.Image[InternalPixelType, Dimension]
    converter = itk.PyBuffer[ImageType]
    IT = itk.Image.F3
    #img = IT.New(Regions=[inputVolume1.shape[2], inputVolume1.shape[1], inputVolume1.shape[0]])
    #img.Allocate()
    #img.FillBuffer(0)
    InternalImageType = IT
    OutputImageType = IT
    # Writing and reading from file works around a WrapITK bug
    itk.write(image1, os.path.join(default_path.defaultOutputPath, "hello1.nrrd"))
    itk.write(image1, os.path.join(default_path.defaultOutputPath, "hello2.nrrd"))
    #seedPosition = numpyToItkPoint(center)

    # test code
    argv[1:] = ["O:\\images\\HPFcere_vol\\HPF_rotated_tif\\median_then_gaussian_8bit_classified_pixels\\median_then_gaussian_8bit_classified_pixels.nrrd", "o:\\temp\\fastmarch3d.nrrd", 81, 114, 1.0, -0.5, 3.0, 0.4, 0.4]
    if( len(argv) < 10 ):
      print >> stderr, """Missing Parameters
    Usage: FastMarchingImageFilter.py inputImage  outputImage seedX seedY Sigma SigmoidAlpha SigmoidBeta TimeThreshold StoppingValue"""
      exit(1)
    #end of test code

    NodeType = itk.LevelSetNode[InternalPixelType, Dimension]
    NodeContainer = itk.VectorContainer[itk.UI, NodeType]

    itkSeedList = []

    for point in seedList:    

        itkSeedList.append(numpyToItkPoint(point))

    
    resultItkArray = shellActiveContour(inputImage=image1,
                                        seedPoints=itkSeedList,
                                        #advectionScaling=80.0,
                                        advectionScaling=160.0,
                                        #curvatureScaling=0.75,
                                        curvatureScaling=6.75,
                                        dimensions=3,
                                        propagationScaling=1)
                                        #advectionScaling=20.0,
                                        #curvatureScaling=1.2,
    
    return resultItkArray


def fastMarch_old(seedPositionNumpyArray, numpyTargetPointList):
    """Deprecated"""

    if 1:
        seedPosition = numpyToItkPoint(seedPositionNumpyArray)
    
        ImageType = itk.Image[itk.F, 3]
        converter = itk.PyBuffer[ImageType]
        
        #UCImageType = itk.Image[itk.UC, 3]
        #UCConverter = itk.PyBuffer[UCImageType]
    
        print "fast march inputNumpyVolume", numpyBufferFromPyBufferClass
        inputVolume = converter.GetImageFromArray(numpyBufferFromPyBufferClass)
        print "fast march inputVolume", inputVolume
        itk.write(inputVolume, "/tmp/hello.nrrd")
    
        #argv[1:] = ["O:\\software\\InsightToolkit-3.12.0\\Wrapping\\WrapITK\\images\\BrainProtonDensitySlice.png", "o:\\temp\\fastmarch2d.png", 81, 114, 1.0, -0.5, 3.0, 100, 100]
        #argv[1:] = ["O:\\temp\\3dvolume\\3d.nrrd", "o:\\temp\\fastmarch3d.nrrd", 81, 114, 1.0, -0.5, 3.0, 100, 100]
        #argv[1:] = ["O:\\images\\HPFcere_vol\\HPF_rotated_tif\\median_then_gaussian_filter.nrrd", "o:\\temp\\fastmarch3d.nrrd", 81, 114, 1.0, -0.5, 3.0, 100, 100]
        #argv[1:] = ["O:\\images\\HPFcere_vol\\HPF_rotated_tif\\median_then_gaussian_filter.nrrd", "o:\\temp\\fastmarch3d.nrrd", 81, 114, 1.0, -0.5, 3.0, 1, 1]
        #argv[1:] = ["O:\\images\\HPFcere_vol\\HPF_rotated_tif\\median_then_gaussian_8bit_classified_pixels\\median_then_gaussian_8bit_classified_pixels.nrrd", "o:\\temp\\fastmarch3d.nrrd", 81, 114, 1.0, -0.5, 3.0, 0.1, 0.1]
        argv[1:] = ["O:\\images\\HPFcere_vol\\HPF_rotated_tif\\median_then_gaussian_8bit_classified_pixels\\median_then_gaussian_8bit_classified_pixels.nrrd", "o:\\temp\\fastmarch3d.nrrd", 81, 114, 1.0, -0.5, 3.0, 0.4, 0.4]
    
        if( len(argv) < 10 ):
          print >> stderr, """Missing Parameters
        Usage: FastMarchingImageFilter.py inputImage  outputImage seedX seedY Sigma SigmoidAlpha SigmoidBeta TimeThreshold StoppingValue"""
          exit(1)
          
        #itk.auto_progress(2)
        
        
        InternalPixelType = itk.F
        Dimension = 3
        InternalImageType = itk.Image[ InternalPixelType, Dimension ]
        
        OutputPixelType = itk.UC
        OutputImageType = itk.Image[ OutputPixelType, Dimension ]
        
        
        
        CastFilterType = itk.RescaleIntensityImageFilter[ 
                                    InternalImageType, 
                                    OutputImageType ]
        
        SmoothingFilterType = itk.CurvatureAnisotropicDiffusionImageFilter[ 
                                    InternalImageType, 
                                    InternalImageType ]
        
        smoothing = SmoothingFilterType.New()
        
        GradientFilterType = itk.GradientMagnitudeRecursiveGaussianImageFilter[
                                    InternalImageType, 
                                    InternalImageType ]
        
        SigmoidFilterType = itk.SigmoidImageFilter[
                                    InternalImageType, 
                                    InternalImageType ]
        
        gradientMagnitude = GradientFilterType.New();
        sigmoid = SigmoidFilterType.New()
        
        sigmoid.SetOutputMinimum(  0.0  )
        sigmoid.SetOutputMaximum(  1.0  )
        
        FastMarchingFilterType = itk.FastMarchingUpwindGradientImageFilter[ InternalImageType, 
                                    InternalImageType ]
        #FastMarchingFilterType = itk.FastMarchingImageFilter[ InternalImageType, 
        #                            InternalImageType ]
    
        NodeType = itk.LevelSetNode[InternalPixelType, Dimension]
        NodeContainer = itk.VectorContainer[itk.UI, NodeType]
    
        #numpyStopPointList = [array(seedPosition) + array([10,10,10])]
        numpyStopPointList = numpyTargetPointList
    
        #print numpyStopPointList
        
        stopPoints = NodeContainer.New()
        for pointObject in numpyStopPointList:
            stopPointNode = NodeType()
            stopPointNode.SetValue(0) #todo: is this needed
            stopPointNode.SetIndex(numpyToItkPoint(pointObject.loc))
            stopPoints.InsertElement(0, stopPointNode)
        
        fastMarching = FastMarchingFilterType.New()
        fastMarching.SetTargetReachedModeToOneTarget()
        fastMarching.SetTargetOffset(0)
        fastMarching.SetTargetPoints(stopPoints)
    
        fastMarching.SetInput(inputVolume)
        
        sigma = float( argv[5] )
        
        gradientMagnitude.SetSigma(  sigma  )
        
        alpha =  float( argv[6] )
        beta  =  float( argv[7] )
        
        ##sigmoid.SetAlpha( alpha )
        ##sigmoid.SetBeta(  beta  )
        
        seeds = NodeContainer.New()
        
        #seedPosition = [10, 10, 10]
        
        
        node = NodeType()
        seedValue = 0.0
        
        node.SetValue( seedValue )
        node.SetIndex( seedPosition )
        #print "fastmarch seed position", seedPosition
        
        seeds.Initialize();
        seeds.InsertElement( 0, node )
        
        fastMarching.SetTrialPoints(  seeds  );
        
        
        #fastMarching.SetOutputSize( 
        #        reader.GetOutput().GetBufferedRegion().GetSize() )
        fastMarching.SetOutputSize(inputVolume.GetBufferedRegion().GetSize())
        
        stoppingTime = float( argv[9] )
        #stoppingTime = float(1000000)
        
        fastMarching.SetStoppingValue(  stoppingTime  )
        
        #writer.Update()
        
        #return UCConverter.GetArrayFromImage(thresholder.GetOutput())
        fastMarching.Update()
        resultItkArray = fastMarching.GetOutput()
        #itk.write(resultItkArray, "/tmp/result.nrrd")
    print "inputVolume2", inputVolume
    itk.write(inputVolume, "/tmp/result_something.nrrd")



def shellActiveContourWrapper_old(seedPositionNumpyArray, numpyTargetPointList):
    """Deprecated"""
    
    if 1:
        seedPosition = numpyToItkPoint(seedPositionNumpyArray)
    
        ImageType = itk.Image[itk.F, 3]
        converter = itk.PyBuffer[ImageType]
        
        print "fast march inputNumpyVolume", numpyBufferFromPyBufferClass
        inputVolume = converter.GetImageFromArray(numpyBufferFromPyBufferClass)
        print "fast march inputVolume", inputVolume
        itk.write(inputVolume, "/tmp/hello.nrrd")
    
        argv[1:] = ["O:\\images\\HPFcere_vol\\HPF_rotated_tif\\median_then_gaussian_8bit_classified_pixels\\median_then_gaussian_8bit_classified_pixels.nrrd", "o:\\temp\\fastmarch3d.nrrd", 81, 114, 1.0, -0.5, 3.0, 0.4, 0.4]
    
        if( len(argv) < 10 ):
          print >> stderr, """Missing Parameters
        Usage: FastMarchingImageFilter.py inputImage  outputImage seedX seedY Sigma SigmoidAlpha SigmoidBeta TimeThreshold StoppingValue"""
          exit(1)
          
        InternalPixelType = itk.F
        Dimension = 3
        InternalImageType = itk.Image[ InternalPixelType, Dimension ]
        
        OutputPixelType = itk.UC
        OutputImageType = itk.Image[ OutputPixelType, Dimension ]
        
        CastFilterType = itk.RescaleIntensityImageFilter[ 
                                    InternalImageType, 
                                    OutputImageType ]
        
        SmoothingFilterType = itk.CurvatureAnisotropicDiffusionImageFilter[ 
                                    InternalImageType, 
                                    InternalImageType ]
        
        smoothing = SmoothingFilterType.New()
        
        GradientFilterType = itk.GradientMagnitudeRecursiveGaussianImageFilter[
                                    InternalImageType, 
                                    InternalImageType ]
        
        SigmoidFilterType = itk.SigmoidImageFilter[
                                    InternalImageType, 
                                    InternalImageType ]
        
        gradientMagnitude = GradientFilterType.New();
        sigmoid = SigmoidFilterType.New()
        
        sigmoid.SetOutputMinimum(  0.0  )
        sigmoid.SetOutputMaximum(  1.0  )
        
        FastMarchingFilterType = itk.FastMarchingUpwindGradientImageFilter[ InternalImageType, 
                                    InternalImageType ]
    
        NodeType = itk.LevelSetNode[InternalPixelType, Dimension]
        NodeContainer = itk.VectorContainer[itk.UI, NodeType]
    
        numpyStopPointList = numpyTargetPointList
    
        stopPoints = NodeContainer.New()
        for pointObject in numpyStopPointList:
            stopPointNode = NodeType()
            stopPointNode.SetValue(0) #todo: is this needed
            stopPointNode.SetIndex(numpyToItkPoint(pointObject.loc))
            stopPoints.InsertElement(0, stopPointNode)
        
        fastMarching = FastMarchingFilterType.New()
        fastMarching.SetTargetReachedModeToOneTarget()
        fastMarching.SetTargetOffset(0)
        fastMarching.SetTargetPoints(stopPoints)
    
        fastMarching.SetInput(inputVolume)
        
        sigma = float( argv[5] )
        
        gradientMagnitude.SetSigma(  sigma  )
        
        alpha =  float( argv[6] )
        beta  =  float( argv[7] )
        
        seeds = NodeContainer.New()
        
        node = NodeType()
        seedValue = 0.0
        
        node.SetValue( seedValue )
        node.SetIndex( seedPosition )
        
        seeds.Initialize();
        seeds.InsertElement( 0, node )
        
        fastMarching.SetTrialPoints(  seeds  );
        
        
        fastMarching.SetOutputSize(inputVolume.GetBufferedRegion().GetSize())
        
        stoppingTime = float( argv[9] )
        
        fastMarching.SetStoppingValue(  stoppingTime  )
        
        fastMarching.Update()
        resultItkArray = fastMarching.GetOutput()
    print "inputVolume2", inputVolume
    itk.write(inputVolume, "/tmp/result_something.nrrd")



def computeFillFromEllipseCenters(inputVolume1, contourList, fillMethod):
    """
    Uses shellActiveContourWrapper to perform level set separately at each contour.
    Nolonger using this function.
    """

    global numpyBufferFromPyBufferClass
    global img

    InternalPixelType = itk.F
    Dimension = 3
    ImageType = itk.Image[InternalPixelType, Dimension]
    converter = itk.PyBuffer[ImageType]
    IT = itk.Image.F3
    img = IT.New(Regions=[inputVolume1.shape[2], inputVolume1.shape[1], inputVolume1.shape[0]])
    img.Allocate()
    img.FillBuffer(0)
    InternalImageType = IT
    OutputImageType = IT

    numpyBufferFromPyBufferClass = itk.PyBuffer[IT].GetArrayFromImage(img)
    numpyBufferFromPyBufferClass[:, :, :] = inputVolume1
    
    count = 0
    for contour in contourList:
        center = contour.bestFitEllipse.center
        print "compute fill", count, "total", len(contourList)
    
        inputVolume = converter.GetImageFromArray(numpyBufferFromPyBufferClass)
        inputVolumeFileName = os.path.join(default_path.defaultOutputPath, "hello.nrrd")
        # Writing and reading from file works around a WrapITK bug
        itk.write(inputVolume, inputVolumeFileName)
        reader1 = itk.ImageFileReader[InternalImageType].New(FileName=inputVolumeFileName)
        image1  = reader1.GetOutput()

        if fillMethod == 'fastMarch':
            resultItkArray = fastMarch(image1, center, contour, inputVolume)
        elif fillMethod == 'shellActiveContour':
            resultItkArray = shellActiveContourWrapper(image1, center, contour, inputVolume)
        else: raise Exception, "Invalid fill method"
        
        tempFileName = os.path.join(default_path.defaultOutputPath, "fillResult.nrrd")
        print "writing file", tempFileName
        itk.write(resultItkArray, tempFileName)

        resultVolume = numpy.array(converter.GetArrayFromImage(resultItkArray))
        if 1:
            #contour.features['fastMarchFromEllipseCenter'] = resultVolume
            blob = Blob()
            #binaryResult = resultVolume < 10000000
            binaryResult = resultVolume < 0.5
            if 0:
                print "starting flood fill"
                pointList = floodFill(binaryResult, center)
                print "flood fill finished"
                blob.setPoints(pointList)

            if count == 0:
                sumVolume = (1.0 * binaryResult)
            else:
                sumVolume += (1.0 * binaryResult)

            #contour.features['fastMarchBlobFromEllipseCenter'] = blob
            print "result volume"
        count += 1

    return sumVolume


def quickComputeFillFromEllipseCenters(inputVolume1, contourList, fillMethod):
    """
    Uses shellActiveContourWrapper to perform level set initiated at all contours in contourList.
    Parameters:
    inputVolume1: guides the level set operation
    contourList: list of seed contours
    fillMethod: specifies the fill method, use 'shellActiveContour'    
    """

    global numpyBufferFromPyBufferClass
    global img

    InternalPixelType = itk.F
    Dimension = 3
    ImageType = itk.Image[InternalPixelType, Dimension]
    converter = itk.PyBuffer[ImageType]
    IT = itk.Image.F3
    img = IT.New(Regions=[inputVolume1.shape[2], inputVolume1.shape[1], inputVolume1.shape[0]])
    img.Allocate()
    img.FillBuffer(0)
    InternalImageType = IT
    OutputImageType = IT

    numpyBufferFromPyBufferClass = itk.PyBuffer[IT].GetArrayFromImage(img)
    numpyBufferFromPyBufferClass[:, :, :] = inputVolume1
    
    centerList = []

    contourCount = 0
    print "number of contours", len(contourList)

    erodedContoursNode = GroupNode('ErodedContours')

    #file = open("o:\\temp\\contours.txt", 'w')
    for contour in contourList:
        center = contour.bestFitEllipse.center

        #centerList.append(center)

        #print "starting erosion", contourCount
        #print dir(copy_module)
        #locations = copy_module.deepcopy(contour.locations())
        #print locations
        #file.write(str(locations))
        #print "number of points", len(locations)
        erodedContourSet = erosion.erosion_polygon(contour.locations(), 10)
        erodedContourSet = erodedContourSet +\
            erosion.erosion_polygon(contour.locations(), 20)

        #print "completed erosion"
        for erodedContour in erodedContourSet:
            erodedContourObject = Contour()
            erodedContourObject.addNumpyPoints(erodedContour)
            erodedContoursNode.addObject(erodedContourObject)
            #for point in contour.locations():
            for point in erodedContour:
                #centerList.append(((array(point) - array(center)) / 2.0) + array(center))
                centerList.append(array(point))

        contourCount += 1

    #file.close()
    count = 0


    #todo: check if this center variable needs to be here
    if len(contourList) > 0:
        center = contour.bestFitEllipse.center

    print "compute fill", count, "total", len(contourList)

    inputVolume = converter.GetImageFromArray(numpyBufferFromPyBufferClass)
    inputVolumeFileName = os.path.join(default_path.defaultOutputPath, "hello.nrrd")
    # Writing and reading from file works around a WrapITK bug
    itk.write(inputVolume, inputVolumeFileName)
    reader1 = itk.ImageFileReader[InternalImageType].New(FileName=inputVolumeFileName)
    image1  = reader1.GetOutput()

    if fillMethod == 'fastMarch':
        #resultItkArray = fastMarch(image1, center, contour, inputVolume)
        raise Exception, "not implemented"
    elif fillMethod == 'shellActiveContour':
        #resultItkArray = shellActiveContourWrapper(image1, centerList, contour, inputVolume)
        resultItkArray = shellActiveContourWrapper(image1, centerList, None, inputVolume)
    else: raise Exception, "Invalid fill method"
    
    tempFileName = os.path.join(default_path.defaultOutputPath, "fillResult.nrrd")
    print "writing file", tempFileName
    itk.write(resultItkArray, tempFileName)

    resultVolume = numpy.array(converter.GetArrayFromImage(resultItkArray))
    if 1:
        #contour.features['fastMarchFromEllipseCenter'] = resultVolume
        blob = Blob()
        #binaryResult = resultVolume < 10000000
        binaryResult = resultVolume < 0.5
        if 0:
            print "starting flood fill"
            pointList = floodFill(binaryResult, center)
            print "flood fill finished"
            blob.setPoints(pointList)

        if count == 0:
            sumVolume = (1.0 * binaryResult)
        else:
            sumVolume += (1.0 * binaryResult)

        #contour.features['fastMarchBlobFromEllipseCenter'] = blob
        print "result volume"
    count += 1

    return sumVolume, erodedContoursNode


def fillAndDisplayResults(gui, inputVolumeName, contoursNodeName,
                          displayParameters, enable3DPlot, fillMethod):

    print "fastMarchAndDisplayResults"
    
    numberOfContoursToDisplay = displayParameters.numberOfContoursToDisplay

    inputVolume = gui.getPersistentVolume_old(inputVolumeName)
    #print inputVolume

    node = gui.mainDoc.dataTree.getSubtree((contoursNodeName,))
    #contourList = node.makeChildrenObjectList()
    contourList = nonnullNongroupObjects(node)
    #highProbabilityContourList = highProbabilityContours(contours)
    
    if numberOfContoursToDisplay != None:
        contourList = contourList[0:numberOfContoursToDisplay]


    if len(contourList) == 0:
        print "no high probability contours to display"

    
    #if len(contourList) > 0:
    if 1:

        # perform fast march operations
        #sumVolume = computeFillFromEllipseCenter(inputVolume, contourList, fillMethod)
        sumVolume, erodedContoursNode = quickComputeFillFromEllipseCenters(inputVolume, contourList, fillMethod)
    
        gui.addPersistentVolumeAndRefreshDataTree(sumVolume, inputVolumeName + 'AllFastMarchBlobs')
        gui.addPersistentSubtreeAndRefreshDataTree((), erodedContoursNode)
    
        # display 3D blobs
        if enable3DPlot: displayBlobsFromContourCenters(gui, contourList)
    
        if 0:
            # add blobs for the fastmarch to the data tree
            count = 0
            for contour in contourList:
                gui.addBlob(contour.features['fastMarchBlobFromEllipseCenter'], getNode(gui.mainDoc.dataRootNode, ('Blobs',)), inputVolumeName + ('Blob%d' % count))
                count += 1
    
        gui.mainDoc.dataTree.writeSubtree(('Blobs',))
        gui.refreshTreeControls()



#@mayavi2.standalone
def displayBlobsFromContourCenters(gui, contourList):
    """Deprecated. Nolonger using this GUI functionality"""

    from enthought.mayavi import mlab as enthought_mlab

    count = 0
    for contour in contourList:
        blobVolume = contour.features['fastMarchFromEllipseCenter']
        enthought_mlab.contour3d(blobVolume, contours=3)
        gui.addVolumeAndRefreshDataTree(blobVolume, 'BlobFromContour%d' % count)
        count += 1    
    
    
