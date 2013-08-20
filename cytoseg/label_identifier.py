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

# LabelIdentifier class for defining how a value or set of values in a label
# volume maps to a type of object.

import numpy

class LabelIdentifier:
    """
    Represents a label for a particular biological object.
    Specifies the voxel label value or values that are associated with this object.
    """

    def __init__(self, objectName, min=None, max=None, values=None, weight=1.0):

        self.objectName = objectName
        self.min = min
        self.max = max

        if values != None:
            self.values = {}
            for value in values:
                self.values[value] = True
        else:
            self.values = None
        #self.values = values

        self.labelWeight = weight


    def isMember(self, value):
        """Value is a value in a label raster. If the value matches this label identifier,
        then return True. Otherwise return false."""

        returnValue = False

        if self.min != None and self.max != None:
            if self.min <= value <= self.max:
                returnValue = True

        if self.values != None:
            if value in self.values:
                returnValue = True

        return returnValue


    def count(self, volume):
        """Count how many times this label occurs in the volume."""

        countResult = 0

        for x in range(volume.shape[0]):
            for y in range(volume.shape[1]):
                for z in range(volume.shape[2]):
                    if self.isMember(volume[x,y,z]):
                        countResult += 1

        return countResult


    def getBooleanVolume(self, inputLabel):
        """Make a single label volume for only this label's object type."""

        returnVolume = numpy.zeros(inputLabel.shape, dtype=bool)

        if self.min != None and self.max != None:
            returnVolume = numpy.logical_and(self.min <= inputLabel, inputLabel <= self.max)

        if self.values != None:
            for value in self.values:
                returnVolume |= (inputLabel == value)
            #if value in self.values:
            #    returnValue = True

        return returnVolume


class LabelIdentifierDict(dict):

    def getClassName(self, value):
        """
        Each key of the dictionary is the name of an object type.
        Each value of the dictionary is a LabelIdentifier.
        Convenience method to get the object type (dictionary key) name based on the label value.
        """

        className = None

        for target in self:
            #print "target", target
            #print "value", value
            #print "self[target].isMember(value)", self[target].isMember(value)
            labelIdentifier = self[target] 
            if labelIdentifier.isMember(value):
                className = labelIdentifier.objectName

        return className

