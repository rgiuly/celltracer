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

# Tools for operating on and saving 3D volumes


from numpy import *
import Image
import os
from scipy import ndimage
from data_viewer import stringsWithImageFileExtensions


class Box:
    """Represents a 3D box. Often used for boundaries."""

    def __init__(self, cornerA=None, cornerB=None):
        
        # 3D point
        if cornerA == None:
            self.cornerA = [None, None, None]
        else:
            self.cornerA = list(cornerA)
        
        # 3D point
        if cornerB == None:
            self.cornerB = [None, None, None]
        else:
            self.cornerB = list(cornerB)
        

    def __repr__(self):

        return "cornerA=%s, cornerB=%s" % (self.cornerA, self.cornerB)


    def shape(self):

        return array(self.cornerB) - array(self.cornerA)


    def getBoxForShape(self, shape):
        """
        Some coordinates in cornerA and cornerB may by be None. None means use the extreme
        minimum (for minimum bound) or maximum (for maximum bound). This method fills in "None"
        coordinates with the actual extreme numbers. (0 for minimum, full dimension for maximum)
        Parameters:
        shape: boundary (provides full dimension for maximums)
        """

        resultBox = Box()

        for coordinateIndex in range(3):
            #print type(self.cornerA[coordinateIndex])
            #print type(self.cornerB[coordinateIndex])
            if self.cornerA[coordinateIndex] == None:
                resultBox.cornerA[coordinateIndex] = 0
            else:
                resultBox.cornerA[coordinateIndex] = self.cornerA[coordinateIndex]
            if self.cornerB[coordinateIndex] == None:
                resultBox.cornerB[coordinateIndex] = shape[coordinateIndex]
            else:
                resultBox.cornerB[coordinateIndex] = self.cornerB[coordinateIndex]

        return resultBox


def isInsideVolume(volume, point):
    """True if the point is inside the volume"""
    s = volume.shape
    if point[0] < s[0] and point[1] < s[1] and point[2] < s[2] and point[0] >= 0 and point[1] >= 0 and point[2] >= 0:
        return True
    else:
        return False


def at(volume, point):
    """Return value of volume at point."""
    return volume[point[0],point[1],point[2]]


def rescale(volume, min, max):
    """Rescale the values of a volume between min and max."""
    
    factor = float(max - min) / float(volume.max() - volume.min())
    return ((volume - volume.min()) * factor) + min


def resizeVolume(volume, factors):
    """Resize volume by a given factor"""
    
    inputShape = volume.shape
    
    #if type(factor) != type(1):
    #    raise Exception, "Non-integer %s used. Please use an integer." % factor
    
    Nx = ((inputShape[0])*factors[0]) # new number of samples in x direction
    Ny = ((inputShape[1])*factors[1]) # new number of samples in y direction
    Nz = ((inputShape[2]-1)*factors[2] + 1) # new number of samples in z direction

    #todo: use this
    #    coords = mgrid[0:inputShape[0]-1:Nx*1j,
    #                   0:inputShape[1]-1:Ny*1j,
    #                   0:inputShape[2]-1:Nz*1j]
    
    ivals, jvals, kvals = mgrid[0:inputShape[0]:Nx*1j,
                                0:inputShape[1]:Ny*1j,
                                0:inputShape[2]-1:Nz*1j]
    
    
    coords = array([ivals, jvals, kvals])
    
    newVolume = ndimage.map_coordinates(volume, coords, order=1)
    #newVolume = ndimage.map_coordinates(volume, coords)
    
    return newVolume


# todo: path and filename combining should be done with a function for certain operating system i think
def writeTiffStack_version1(path, redVolume, greenVolume, blueVolume):
    """Depricated"""
    maxValue = 255
    
    #path = 'c:/temp/'
    for i in range(0,redVolume.shape[2]):
        # all the volumes of each color should have the same dimensions (shape)
        colorImageArray = numpy.zeros((redVolume.shape[0], redVolume.shape[1], 3), numpy.uint8)
        
        colorImageArray[:,:,0] = redVolume[:,:,i]
        colorImageArray[:,:,1] = greenVolume[:,:,i]
        colorImageArray[:,:,2] = blueVolume[:,:,i]
        #colorImageArray[:,:,3] = maxValue
        
        #image = Image.fromarray(colorImageArray, 'RGB')
        
        image = Image.fromstring("F", (a.shape[1],a.shape[0]), a.tostring())
        
        
        fullName = path + ('output%0.3d' % i) + '.tiff'
        print fullName
        image.save(fullName)


def imageFilename(path, baseFilename, fileExtension, index):
    """Combine basename with number to form image filename."""

    return os.path.join(path, "%s%0.3d%s" % (baseFilename, index, fileExtension))


def writeImagePadding(path, baseFilename, fileExtension, volumeShape, dataStartIndex):
    """Write blank images to form padding when creating an image stack.
    This will not overwrite existing images."""

    blank = zeros((volumeShape[0], volumeShape[1]), dtype=int8)
    blankTransposed = blank.T
    blankImage = Image.fromstring("L",
                             (blankTransposed.shape[1], blankTransposed.shape[0]),
                             blankTransposed.tostring())

    for i in range(0, dataStartIndex):

        fullName = imageFilename(path, baseFilename, fileExtension, i)

        if os.path.exists(fullName):
            print fullName, "already exists"
        else:
            print fullName, "created padding image"
            blankImage.save(fullName)


# todo: maybe switch path and volume parameter order
def writeStack(path, volume, baseFilename="output", startIndex=0):
    """Write volume to image stack."""

    maxValue = 255
    fileExtension = ".png"

    # create blank image padding from 0 to (startIndex - 1)

    writeImagePadding(path, baseFilename, fileExtension, volume.shape, startIndex)


    # create images

    a = zeros((volume.shape[0], volume.shape[1]), dtype=int8)
    
    #path = 'c:/temp/'
    for i in range(0,volume.shape[2]):

        #a[:,:] = 
        a[:,:] = volume[:,:,i]
        aTransposed = a.T
        image = Image.fromstring("L", (aTransposed.shape[1],aTransposed.shape[0]),
                                 aTransposed.tostring())

        fullName = imageFilename(path, baseFilename, fileExtension, startIndex + i)
        print fullName
        image.save(fullName)


def writeStackRGB(path, redVolume, greenVolume, blueVolume,
                      baseFilename="output", startIndex=0):
    """Write volumes to color image stack."""
    
    if redVolume != None:
        volumeShape = redVolume.shape
    elif greenVolume != None:
        volumeShape = greenVolume.shape
    elif blueVolume != None:
        volumeShape = blueVolume
    else:
        raise Exception, "At least one of the volumes should be a 3D array (all of them are None)."
    
    #fileExtension = ".bmp"
    #fileExtension = ".png"
    fileExtension = ".jpg"

    writeImagePadding(path, baseFilename, fileExtension, volumeShape, startIndex)

    # array for the image
    a = zeros((volumeShape[1], volumeShape[0], 3), dtype=int8)
    
    # todo: check to make sure the three volumes have the same dimensions
    for imageIndex in range(redVolume.shape[2]):
        
        if redVolume != None: a[:,:,0] = redVolume[:,:,imageIndex].T
        if greenVolume != None: a[:,:,1] = greenVolume[:,:,imageIndex].T
        if blueVolume != None: a[:,:,2] = blueVolume[:,:,imageIndex].T
        image = Image.fromarray(a, 'RGB')
        
        fullName = imageFilename(path, baseFilename, fileExtension,
                                 startIndex + imageIndex)
        print fullName
        image.save(fullName)




def getImageStackSize(path):
    """Read dimensions of image stack."""

    fileList = os.listdir(path)
    fileList = stringsWithImageFileExtensions(fileList)
    
    if len(fileList) == 0:
        raise Exception, "There are no images files of a type that cytoseg can read in the folder %s" % path
    
    fileList.sort()
    print "Image files in the folder", path, ": ", fileList
        
    numImages = len(fileList)

    firstImage = True
    
    size = [None, None, None]

    size[2] = numImages

    #indexRange = range(box.cornerA[2], box.cornerB[2]) 

    for i in range(0, 1):
        
        filename = os.path.join(path, fileList[i])    
        print filename

        im1 = Image.open(filename)
        im1 = im1.transpose(Image.ROTATE_270)
        im1 = im1.transpose(Image.FLIP_LEFT_RIGHT)

        array2d = fromstring(im1.tostring(), uint8)
        
        if im1.size[0] * im1.size[1] != array2d.shape[0]:
            raise Exception, "problem loading the image %s. possible problem: it has to be 8bit grayscale to work" % filename

                   
        size[0] = im1.size[1]
        size[1] = im1.size[0]

        print "size", size            

        return size


