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

# Image filters

import warnings
from numpy import *
import numpy
import geometry
try:
    import itk
except ImportError:
    warnings.warn("itk module is not installed")
from containers import *


def gaussian(x, amplitude, sigma):
    """Returns Gaussian function value at x"""
    return amplitude * exp(-pow(x, 2) / (2*pow(sigma,2)))

# 3D gaussian
global defaultType
defaultType = numpy.float32
def gaussianVolume(shape, position, amplitude, sigma):
    """Returns 3D volume with Gaussian function values written into it."""
    # sigma is fatness
    volume = zeros(shape, defaultType)
    for x in range(0, shape[0]):
        for y in range(0, shape[1]):
            for z in range(0, shape[2]):
                dist = geometry.distance(position, array([x,y,z]))
                #volume[x,y,z] = dist * 20
                volume[x,y,z] = gaussian(dist, amplitude, sigma)
    return volume

def differenceOfOffsetGaussians(volumeShape, offsetVector, sigma):
    """Returns difference of offset Gaussians as a 3d volume"""
    g0 = gaussianVolume(volumeShape, array(volumeShape)/2 + -array(offsetVector), 1, sigma)
    g1 = gaussianVolume(volumeShape, array(volumeShape)/2 + array(offsetVector), 1, sigma)
    #todo: check for off-by-one when using array(volumeShape)/2
    return g0-g1

def differenceOfGaussians(volumeShape, sigma1, sigma2, amplitude1=1.0, amplitude2=1.0):
    """Returns difference of Gaussians as a 3d volume"""
    center = (array(volumeShape)-1)/2.0
    g1 = gaussianVolume(volumeShape, center, amplitude1, sigma1)
    g2 = gaussianVolume(volumeShape, center, amplitude2, sigma2)
    return g1-g2


def makeItkImage(dimensions, pixelType):
    """Make ITK image"""

    Dimension = len(dimensions)
    ImageType = itk.Image[pixelType, Dimension]
    
    index = itk.Index[Dimension]()
    for i in range(Dimension):
        index.SetElement(i, 0)
    
    size = itk.Size[Dimension]()
    for i in range(Dimension):
        size.SetElement(i, dimensions[i])
    
    imageRegion = itk.ImageRegion[Dimension]()
    imageRegion.SetSize(size)
    imageRegion.SetIndex(index)
    
    
    image = ImageType.New()
    #image.SetSize([10,10])
    #image.SetIndex([0,0])
    #image.SetPixel([0,0], 0)
    
    image.SetRegions(imageRegion)
    image.Allocate()
    image.FillBuffer(0)
    
    return image


def numpyToItk(numpyArray):
    """Copies numpy array to ITK array and returns the ITK array"""

    Dimension = len(numpyArray.shape)

    if Dimension == 2:
        return numpyToItk2D(numpyArray)
    elif Dimension == 3:
        return numpyToItk3D(numpyArray)
    else:
        raise Exception,\
         "Invalid dimension for numpyToItk: %d. Dimension should be 2 or 3" % Dimension


def itkToNumpy(itkImage):
    """Copies ITK array to numpy array and returns the numpy array"""

    #print dir(itkImage)
    #print dir(itkImage.__class__)
    #Dimension = itkImage.GetImageDimension()
    #print itkImage.__class__
    
    imageClass = itkImage.__class__
    imagePointerClass2D = itk.Image[itk.F, 2].New().__class__
    imagePointerClass3D = itk.Image[itk.F, 3].New().__class__
    if imageClass == imagePointerClass2D:
        Dimension = 2
    elif imageClass == imagePointerClass3D:
        Dimension = 3
    else:
        raise Exception, "invalid class %s needs to be %s or %s" %\
            (imageClass, imagePointerClass2D, imagePointerClass3D)

    if Dimension == 2:
        return itkToNumpy2D(itkImage)
    elif Dimension == 3:
        return itkToNumpy3D(itkImage)
    else:
        raise Exception,\
         "Invalid dimension for itkToNumpy: %d. Dimension should be 2 or 3" % Dimension


def numpyToItk2D(numpyArray):
    """Copies 2D numpy array to ITK array and returns ITK array"""

    itkImage = makeItkImage(numpyArray.shape, itk.F)

    index = [None, None]
    for i in range(numpyArray.shape[0]):
        for j in range(numpyArray.shape[1]):
            index[0] = i
            index[1] = j
            itkImage.SetPixel(index, numpyArray[i,j])

    return itkImage

    
def itkToNumpy2D(itkImage):
    """Copies 2D ITK array to numpy array and return numpy array"""

    region = itkImage.GetLargestPossibleRegion()
    size = region.GetSize()
    
    numpyArray = zeros((size.GetElement(0), size.GetElement(1)), dtype=float)

    index = [None, None]
    for i in range(size.GetElement(0)):
        for j in range(size.GetElement(1)):
            index[0] = i
            index[1] = j
            numpyArray[i,j] = itkImage.GetPixel(index)

    return numpyArray


def numpyToItk3D(numpyArray):
    """Copies 3D numpy array to ITK array and return ITK array"""

    itkImage = makeItkImage(numpyArray.shape, itk.F)

    # create an index structure (initialize entries to None)
    index = []
    for i in range(len(numpyArray.shape)):
        index.append(None)

    for i in range(numpyArray.shape[0]):
        for j in range(numpyArray.shape[1]):
            for k in range(numpyArray.shape[2]):
                index[0] = i
                index[1] = j
                index[2] = k
                itkImage.SetPixel(index, numpyArray[i,j,k])

    return itkImage

    
def itkToNumpy3D(itkImage):
    """Copies 3D ITK array to numpy array and return numpy array"""

    region = itkImage.GetLargestPossibleRegion()
    size = region.GetSize()
    
    numpyArray = zeros((size.GetElement(0),
                        size.GetElement(1),
                        size.GetElement(2)), dtype=float)

    # create an index structure (initialize entries to None)
    index = []
    for i in range(len(numpyArray.shape)):
        index.append(None)

    for i in range(size.GetElement(0)):
        for j in range(size.GetElement(1)):
            for k in range(size.GetElement(2)):
                index[0] = i
                index[1] = j
                index[2] = k
                numpyArray[i,j,k] = itkImage.GetPixel(index)

    return numpyArray


def secondDerivatives2D(numpyArray2D):
    """Returns xx, yy, xy, and yx derivates in a dictionary"""
    
    inputImage = numpyToItk(numpyArray2D)
    PixelType = itk.F
    Dimension = 2
    ImageType = itk.Image[PixelType, Dimension]
    #DuplicatorType = itk.ImageDuplicator[OutputImageType]
    FilterType = itk.RecursiveGaussianImageFilter[ImageType, ImageType]

    sigma = 3

    #duplicator = DuplicatorType.New()

    ga = FilterType.New()
    gb = FilterType.New()
    ga.SetSigma(sigma)
    gb.SetSigma(sigma)

    ga.SetDirection(0) # x direction
    gb.SetDirection(1) # y direction
    ga.SetSecondOrder()
    gb.SetZeroOrder()

    ga.SetInput(inputImage)
    gb.SetInput(ga.GetOutput())
    
    gb.Update()

    hessian = odict()
    hessian['xx'] = itkToNumpy(gb.GetOutput()) 

    ga.SetZeroOrder()
    gb.SetSecondOrder()
    gb.Update()
    hessian['yy'] = itkToNumpy(gb.GetOutput()) 

    ga.SetFirstOrder()
    gb.SetFirstOrder()
    gb.Update()
    hessian['xy'] = itkToNumpy(gb.GetOutput()) 

    ga.SetDirection(1) # y direction
    gb.SetDirection(0) # x direction
    ga.SetFirstOrder()
    gb.SetFirstOrder()
    gb.Update()
    hessian['yx'] = itkToNumpy(gb.GetOutput()) 
    
    return hessian




def itkFilter(array, filterType, kernelSize=20, radius=1, sigma=1):
    """Executes ITK filter on numpy array and returns result as numpy array"""

    InternalPixelType = itk.F
    Dimension = len(array.shape)
    ImageType = itk.Image[InternalPixelType, Dimension]
    
    #image2d = converter.GetImageFromArray(array2d)
    image = numpyToItk(array)
    kernel = itk.strel(Dimension, kernelSize)
    
    if filterType == 'GrayscaleDilate':
        filter = itk.GrayscaleDilateImageFilter[ImageType, ImageType, kernel].New(
                        image, Kernel=kernel)
    elif filterType == 'GrayscaleErode':
        filter = itk.GrayscaleErodeImageFilter[ImageType, ImageType, kernel].New(
                        image, Kernel=kernel)
    elif filterType == 'Median':
        filter = itk.MedianImageFilter[ImageType, ImageType].New(
                        image, Radius=radius)
    elif filterType == 'SmoothingRecursiveGaussian':
        filter = itk.SmoothingRecursiveGaussianImageFilter[ImageType, ImageType].New(
                        image, Sigma=sigma)
    else:
        raise Exception, "Invalid filter type: %s" % filterType

    filter.Update()
    #outputVolume[:,:,z] = converter.GetArrayFromImage(dilateFilter.GetOutput())

    return itkToNumpy(filter.GetOutput())


def filterVolume2D(inputVolume, filterType, kernelSize=2):
    """Runs 2D ITK filter on 3D volume, slice by slice, and returns result"""

    InternalPixelType = itk.F
    Dimension = 2
    ImageType = itk.Image[InternalPixelType, Dimension]
    converter = itk.PyBuffer[ImageType]
    
    outputVolume = zeros(inputVolume.shape)
    
    for z in range(inputVolume.shape[2]):
        
        print filterType, z, "total", inputVolume.shape[2]
        
        array2d = inputVolume[:,:,z]
        outputVolume[:,:,z] = itkFilter(array2d, filterType, kernelSize=kernelSize)

    return outputVolume


