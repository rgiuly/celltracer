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

# Functions for comparing contours

from numpy import *
from geometry import *
from point_set import *


def biggestGap(contour1, contour2):
    """See Hausdorff distance."""

    biggestGapValue = 0

    locations1 = contour1.locations()
    locations2 = contour2.locations()

    for index1 in range(len(locations1)):
        point1 = array(locations1[index1])

        # the minimum distance represents the gap from point1 to point2

        # initialize gap
        gap = distance(point1, array(locations2[0]))

        # find the minimum
        #print "find the minimum"
        for coordList2 in locations2:
            point2 = array(coordList2)
            dist = distance(point1, point2)
            #print dist
            if dist < gap:
                gap = dist

        # if the gap is the largest found so far, keep it
        if gap > biggestGapValue:
            biggestGapValue = gap

    return biggestGapValue


def overlap_old(contour1, contour2):
    """Deprecated"""

    temp1 = zeros((1000, 1000), dtype=int8)
    temp2 = zeros((1000, 1000), dtype=int8)

    binaryImage1 = contour1.binaryImage
    binaryImage2 = contour2.binaryImage

    boundingBox1 = contour1.get2DBoundingBox()
    boundingBox2 = contour2.get2DBoundingBox()

    temp1[boundingBox1[0][0]:boundingBox1[1][0]+1,
          boundingBox1[0][1]:boundingBox1[1][1]+1] = binaryImage1

    temp2[boundingBox2[0][0]:boundingBox2[1][0]+1,
          boundingBox2[0][1]:boundingBox2[1][1]+1] = binaryImage2

    andImage = logical_and(temp1, temp2) * 1
    orImage = logical_or(temp1, temp2) * 1
    fraction = float(sum(andImage)) / float(sum(orImage))

    return fraction


def overlap(contour1, contour2):
    """Contour overlap"""

    #temp1 = zeros((1000, 1000), dtype=int8)
    #temp2 = zeros((1000, 1000), dtype=int8)

    binaryImage1 = contour1.binaryImage
    binaryImage2 = contour2.binaryImage

    boundingBox1 = contour1.get2DBoundingBox()
    boundingBox2 = contour2.get2DBoundingBox()

    minX = min(boundingBox1[0][0], boundingBox2[0][0])
    minY = min(boundingBox1[0][1], boundingBox2[0][1])
    maxX = max(boundingBox1[1][0], boundingBox2[1][0])
    maxY = max(boundingBox1[1][1], boundingBox2[1][1])

    temp1 = zeros((maxX-minX+1, maxY-minY+1))
    temp2 = zeros((maxX-minX+1, maxY-minY+1))

    temp1[boundingBox1[0][0]-minX:boundingBox1[1][0]-minX+1,
          boundingBox1[0][1]-minY:boundingBox1[1][1]-minY+1] = binaryImage1

    temp2[boundingBox2[0][0]-minX:boundingBox2[1][0]-minX+1,
          boundingBox2[0][1]-minY:boundingBox2[1][1]-minY+1] = binaryImage2

    andImage = logical_and(temp1, temp2) * 1
    orImage = logical_or(temp1, temp2) * 1
    fraction = float(sum(andImage)) / float(sum(orImage))

    return fraction

