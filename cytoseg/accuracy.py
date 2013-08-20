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

 

# Accuracy calculation. Used to generate comparisons to manual segmentation, e.g. ROC curves

from numpy import *
import math

# This class manages accuracy calculation.
class Accuracy:
    """Class for computing accuracy of voxel classification"""

    def __init__(self, actualLabelVolume, computedLabelVolume):
        """actualLabelVolume has known correct labels.
        computedLabelVolume will be checked against the known correct labels."""

        self.actualLabelVolume = actualLabelVolume
        self.computedLabelVolume = computedLabelVolume


    # computed true, but actual value is false
    def falsePositives(self):

        #print "self.computedLabelVolume shape:%s" % str(self.computedLabelVolume.shape)
        #print "self.actualLabelVolume shape:%s" % str(self.actualLabelVolume.shape)

        return sum(1 * logical_and(self.computedLabelVolume,
                                   logical_not(self.actualLabelVolume)))


    # computed true, and that agrees with the actual value
    def truePositives(self):

        return sum(1 * logical_and(self.computedLabelVolume,
                                   self.actualLabelVolume))


    # computed false, but actual value is true
    def falseNegatives(self):

        return sum(1 * logical_and(logical_not(self.computedLabelVolume),
                                   self.actualLabelVolume))


    # computed false, and that agrees with the actual value
    def trueNegatives(self):

        return sum(1 * logical_and(logical_not(self.computedLabelVolume),
                                   logical_not(self.actualLabelVolume)))


    def actualPositives(self):

        # todo: there may be a simpler way to convert to a boolean
        return sum(1 * logical_not(logical_not(self.actualLabelVolume)))


    def actualNegatives(self):

        return sum(1 * logical_not(self.actualLabelVolume))


    def truePositiveRate(self):

        return float(self.truePositives()) /\
               float(self.actualPositives())


    def falsePositiveRate(self):

        return float(self.falsePositives()) /\
               float(self.actualNegatives())


    def accuracy(self):

        return (float(self.truePositives()) + float(self.trueNegatives())) /\
               (float(self.actualPositives()) + float(self.actualNegatives()))


    def VOC(self):

        return float(self.truePositives()) /\
               (float(self.truePositives()) + float(self.falsePositives()) + float(self.falseNegatives()))


    def printAccuracy(self):

        print "false positives:", self.falsePositives()
        print "true positives:", self.truePositives()
        print "false negatives:", self.falseNegatives()
        print "true negatives:", self.trueNegatives()
        print "size(self.actualLabelVolume):", size(self.actualLabelVolume)
        #print self.actualLabelVolume
        print "error:",\
            float(self.falsePositives() + self.falseNegatives()) /\
            float(size(self.actualLabelVolume))
        tpr = self.truePositiveRate()
        fpr = self.falsePositiveRate()
        print "true positive rate:", float(tpr)
        print "false positive rate:", float(fpr)
        print "accuracy:", self.accuracy()
        print "VOC:", self.VOC()
        print "distance from ideal point:", math.sqrt(math.pow(fpr,2) + math.pow(tpr-1.0, 2))
        print "my error measure:", 5*fpr + (1-tpr)
        print "my error measure 2:", 5*math.pow(fpr,2) + math.pow((1-tpr),2)
        print "my error measure 3:", 10*fpr + (1-tpr)
        print "my error measure 4:", math.sqrt(math.pow(10*fpr,2) + math.pow((1-tpr),2))
        print "my error measure 5:", math.sqrt(math.pow(5*fpr,2) + math.pow((1-tpr),2))
        print "my error measure 6:", math.sqrt(math.pow(7*fpr,2) + math.pow((1-tpr),2)), "use this"

