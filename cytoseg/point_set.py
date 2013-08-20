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

# PointSet class which repesents a set of points and provides methods for calculating
# some properties of set such as the center.


from numpy import *
from probability_object import *


class PointSet(ProbabilityObject):
    """Point set class"""

#    def __init__(self, center=None, size=None, points=[], color=[100,0,0]):
    def __init__(self, center=None, size=None, points=None):
        
        #Node.__init__(self)
        ProbabilityObject.__init__(self)
        
        self._center = center
        self._size = size
        #self._points = points
        #self._color = color
        
        if points == None:
            self._points = []
        else:
            self._points = points    

        self.features = {}
        self.labelSet = set()
        self.numericLabelCountDict = None
        self.labelCountDict = None
        self.XMLTag = 'pointSet'
        self.pointListXMLTag = 'points'
        self.pointXMLFormatString = '%g %g %g, '
        
        #self.averageValueFromTrainingLabelVolume = None
    
    def points(self):
        return self._points
    
    def locations(self):
        """Returns points as list"""
        resultList = []
        for object in self._points:
            if isinstance(object, list):
                resultList.append(object)
            elif isinstance(object, tuple):
                resultList.append(object)
            elif isinstance(object, LabeledPoint):
                resultList.append(object.loc)
            else:
                raise Exception, "Objects in the point list of the Blob should be list, tuple, or LabeledPoint class, not of type %s." % type(object)
        return resultList
    
    def center(self):
        """Returns precomputed center value"""
        return self._center
    
    def setPoints(self, points):
        """Sets points to given sequence"""
        self._points = points
    
    def addNumpyPoints(self, numpyPoints):
        """Convenience method to add points that are represented as numpy arrays"""
        for numpyPoint in numpyPoints:
            self.addPoint(LabeledPoint(numpyPoint))

    def __repr__(self):
        """Return string representation of point set."""
        #return "Blob_with_%d_points" % len(self.points())
        return "PointSet " +\
                "numPoints:" + str(self.numPoints()) + " " +\
                "numericLabelCountDict:" + str(self.numericLabelCountDict) + " " +\
                "labelCountDict:" + str(self.labelCountDict) + " " +\
                "labelSet:" + str(self.labelSet) + " " +\
                "probability():" + str(self.probability()) + " " +\
                "features:" + str(self.features) + " " +\
                ProbabilityObject.__repr__(self)

    
    def setCenter(self, centerPoint):
        """Set center point"""
        self._center = centerPoint

    def size(self):
        """Get size"""
        return self._size
    
    def setSize(self, size):
        """Set size"""
        self._size = size
    
    def addToSize(self, value):
        """Add to size"""
        self._size += value
    
    
    # this is sort of like size() but size can be set to anything so there is no guarantee they will be the same.
    def numPoints(self):
        """Number of points"""
        return len(self.points())


    def addPoint(self, labeledPoint):
        """Add point"""
        self._points.append(labeledPoint)

    
    def addNonzeroVoxels(self, volume):
        """Add points at nonzero voxels in volume"""
        
        for i in range(volume.shape[0]):
            for j in range(volume.shape[1]):
                for k in range(volume.shape[2]):
                    if volume[i, j, k] != 0:
                        self.addPoint(LabeledPoint((i, j, k)))
    
    


    def getLocationsString(self):
        """Creates string that represents all point locations in object"""

        text = ""
        for loc in self.locations():
            text += self.pointXMLFormatString % (loc[0], loc[1], loc[2])
        
        return text
    

    def getAveragePointLocation(self):
        """Get average point location."""
        
        total = array((0, 0, 0))
        for labeledPoint in self.points():
            total += labeledPoint.loc

        return total / float(self.numPoints())
    

    def get2DBoundingBox(self):
        """2D bounding box around points"""

        locations = self.locations()

        firstPoint = locations[0]

        minX = firstPoint[0]
        minY = firstPoint[1]
        maxX = firstPoint[0]
        maxY = firstPoint[1]

        for point in locations:
            x = point[0]
            y = point[1]
            if x < minX: minX = x
            if y < minY: minY = y
            if x > maxX: maxX = x
            if y > maxY: maxY = y

        return ((minX, minY), (maxX, maxY))


    def getXMLObject(self, doc, nodeName):
        """Makes XML object representing point set"""

        #print dir(self)
        objectElement = doc.createElement(self.XMLTag)
        objectElement.setAttribute('name', nodeName)
        objectElement.setAttribute('class', 'Vesicle')
        objectElement.setAttribute('points', self.getLocationsString())

        return objectElement


class LabeledPoint:
    def __init__(self, location):
        self.loc = location
        self.adjacentNonzeroPoints = []
        self.adjacentNonzeroValues = []
        self.adjacentNonzeroValueSet = set()



class Blob(PointSet):
    """Point set that represents a 3D blob."""

    def __init__(self, center=None, size=None, points=None):
        PointSet.__init__(self, center, size, points)
        self.XMLTag = 'blob'
        self.pointListXMLTag = 'voxels'
        self.pointXMLFormatString = '%d, %d, %d '



class Contour(PointSet):
    """Set of points that represents a contour"""

    def __init__(self, center=None, size=None, points=None):

        PointSet.__init__(self, center, size, points)
        self.binaryImage = None

        self.XMLTag = 'Contour'



class ProbabilityFilter():
    """This class represents a probability filter. The minimum required probability can be set."""
    #todo: move to classification file

    def __init__(self, minimumRequiredProbability):
        self.minimumRequiredProbability = minimumRequiredProbability

    def isValid(self, node):
        return node.object.probability() >= self.minimumRequiredProbability



