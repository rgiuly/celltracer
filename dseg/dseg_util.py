
import re
import cPickle
import binascii
import cv


def regionIdentifierToNumbers(identifier):

    result = re.match(r"(.*)_(.*)", identifier)
    z = int(result.group(1))
    index = int(result.group(2))
    return (z, index)


def getRegionByID(cursor, regionIdentifier):

    zIndex, numberIndex = regionIdentifierToNumbers(regionIdentifier)
    command = 'SELECT * FROM regions where z=%d and number=%d' % (zIndex, numberIndex)
    #print command
    cursor.execute(command)
    #print "finished select"
    #1 / 0
    fetchResult = cursor.fetchone()
    z, number, regionBlob, primaryKey = fetchResult
    #print "finished fetchone"
    return cPickle.loads(binascii.unhexlify(regionBlob))


def regionToContours(storageForRegionToContours, region):

    (xMin, yMin, xMax, yMax) = boundingBox(region)

    width = xMax - xMin + 2
    height = yMax - yMin + 2

    image = cv.CreateImage((width, height), cv.IPL_DEPTH_8U, 1)
    cv.SetZero(image)

    for point in region:
        image[point[1] - yMin, point[0] - xMin] = 255

    # split the object for a test
    #for y in range(0, height):
    #    image[width/2, y] = 0

    #cv.SaveImage(r"i:\temp\out_image_intermediate.jpg", image)

    contours = cv.FindContours(image, storageForRegionToContours, mode=cv.CV_RETR_CCOMP, method=cv.CV_CHAIN_APPROX_SIMPLE, offset=(xMin, yMin))

    return contours


#def mergeContours(storage, contours):
#
#    allPoints []
#    for contour in contours:
#        allPoints += contour
#    (xMin, yMin, xMax, yMax) = boundingBox(allPoints)
#    image = cv.CreateImage((width, height), cv.IPL_DEPTH_8U, 1)
#    cv.SetZero(image)
#
#    cv.FillPoly(image, contours, [50, 50, 50], lineType=8, shift=0)
#    cv.SaveImage("/tmp/image%d.png" % random.randint(0,100), image)
#
#    contours = cv.FindContours(image, storageForRegionToContours, mode=cv.CV_RETR_CCOMP, method=cv.CV_CHAIN_APPROX_SIMPLE, offset=(xMin, yMin))
#
#    return contours


def boundingBox(points):

    xMin = points[0][0]
    xMax = points[0][0]
    yMin = points[0][1]
    yMax = points[0][1]
    for p in points:
        x = p[0]
        y = p[1]
        if x < xMin:
            xMin = x
        if x > xMax:
            xMax = x
        if y < yMin:
            yMin = y
        if y > yMax:
            yMax = y
    return (xMin, yMin, xMax, yMax)





