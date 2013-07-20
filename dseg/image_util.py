from PIL import Image
import cv
import os
import numpy
import struct
from volume3d_util import *

#def PILToCV(pi):
#
#    cv_im = cv.CreateImageHeader(pi.size, cv.IPL_DEPTH_8U, 3)
#    cv.SetData(cv_im, pi.tostring())
#    return cv_im

def CVToPIL(cv_im, color=False):

    if color:
        typeString = "RGB"
    else:
        typeString = "L"

    pi = Image.fromstring(typeString, cv.GetSize(cv_im), cv_im.tostring())
    return pi


def stringsWithRawFileExtensions(listOfStrings):
    """Returns subset of the strings in the list that have an image extension."""

    #todo: string comparison should ignore case
    result = []
    for s in listOfStrings:
        if (s.find('.raw') != -1):
            result.append(s)
    return result


def readRawFile(filename, s1):

    f = open(filename, 'rb')

    # read output from slic raw file
    #image = cv.CreateImage((s1[0], s1[1]), 8, 3)
    image = numpy.zeros(s1)
    #cv.SetZero(image)
    count = 0
    #bytes = 4
    #type = '<L'
    bytes = 8
    type = '<Q'
    lastNumber = -1
    for i in range(0, s1[0]):
        #print "i", i
        for j in range(0, s1[1]):
            count += bytes
            string = f.read(bytes)
            if len(string) != bytes:
                print i, j
                print len(string)
                raise Exception("ran out of bytes i %d j %d" % (i, j))
            number = struct.unpack(type, string)[0]
            #print i, j
            image[i, j] = number
            #print number
            #print "count", count
            #if number != lastNumber:
                #print "edge %d %d at (%d, %d)" % (number, lastNumber, i, j)
                #center = (i, j)
                #points.append(center)
            #lastNumber = number

    f.close()
    return image



#def writeRaw(filename, volume):
#
#    f = open(filename, 'wb')
#
#    image = numpy.zeros(volume.shape)
#
#    for k in range(0, volume.shape[2]):
#        for i in range(0, volume.shape[0]):
#            for j in range(0, volume.shape[1]):
#                string = struct.pack('<I', volume[i, j, k])
#                f.write(string)
#
#    f.close()


def writeRawFile32Bit(filename, array2D):

    f = open(filename, 'wb')

    image = numpy.zeros(array2D.shape)

    for j in range(0, array2D.shape[1]):
        for i in range(0, array2D.shape[0]):
            string = struct.pack('I', array2D[i, j])
            f.write(string)

    f.close()



def writeRawStack32Bit(basename, volume):

    for z in range(volume.shape[2]):
        writeRawFile32Bit(basename + "_" + str(z) + ".raw", volume[:, :, z])



def loadRawStack(path, subvolumeBox=None, swapXY=False, flipLR=False):

    fileList = os.listdir(path)
    fileList.sort()
    fileList = stringsWithRawFileExtensions(fileList)
    numImages = len(fileList)

    # z dimension
    if subvolumeBox == None:
        NOT_SET = None
        box = Box((NOT_SET, NOT_SET, 0), (NOT_SET, NOT_SET, numImages))
    else:
        box = subvolumeBox
    
    if box.cornerA[2] == None: box.cornerA[2] = 0
    if box.cornerB[2] == None: box.cornerB[2] = numImages


    # x and y dimensions
    if (subvolumeBox == None):

        box.cornerA[0] = 0
        box.cornerB[0] = 700
    
        box.cornerA[1] = 0
        box.cornerB[1] = 700

    else:

        box = subvolumeBox.getBoxForShape((700, 700, numImages))

    indexRange = range(box.cornerA[2], box.cornerB[2]) 


    volumeShape = box.shape()
    volume = numpy.zeros(volumeShape)

    print fileList

    for z in indexRange:

        filename = fileList[z]
        print filename
        volume[:, :, z-box.cornerA[2]] = readRawFile(os.path.join(path, filename), (700, 700))[box.cornerA[0]:box.cornerB[0], box.cornerA[1]:box.cornerB[1]]

    if swapXY:
        volume = numpy.transpose(volume, (1, 0, 2))

    if flipLR:
        volume = numpy.fliplr(volume)

    return volume


def normalize2D(image, newMaximum):

    result = zeros(image.shape)
    minimum = numpy.min(image)
    maximum = numpy.max(image)
    result = (image - minimum) * (float(newMaximum) / (maximum - minimum)) 
    return result


