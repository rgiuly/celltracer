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

# Experimental code for neural network.
# Currently not using this.

from numpy import *
from scipy import ndimage
from data_viewer import borderWidthForFeatures

class NeuralNetwork():
    """Neural network class"""


    def __init__(self, inputVolume):

        self.inputVolume = inputVolume
        self.outputVolume = zeros(inputVolume.shape, dtype=float32)
        self.weights = ones((11, 11, 1), dtype=float32)


    def update(self):
        """Update network output"""

        sh = self.weights.shape

        ndimage.convolve(self.inputVolume,
                         self.weights / float(sh[0] * sh[1] * sh[2]),
                         output=self.outputVolume)
        self.outputVolume[:] = tanh(self.outputVolume)[:]



    def getOutput(self):
        """Get network output"""

        return self.outputVolume



class NeuralNetworkLearner:

    def __init__(self, inputVolume, outputVolume):

        self.network = NeuralNetwork(inputVolume)
        self.trainingOutputVolume = outputVolume
        self.updateCount = 0


    def error(self):
        """Calculate error"""

        total = 0
        self.network.update()
        v = self.trainingOutputVolume

        for x in range(borderWidthForFeatures[0], v.shape[0]-borderWidthForFeatures[0]):
            #print x, "out of", v.shape[0]-borderWidthForFeatures-1
            for y in range(borderWidthForFeatures[1], v.shape[1]-borderWidthForFeatures[1]):
                for z in range(borderWidthForFeatures[2],
                               v.shape[2]-borderWidthForFeatures[2]):

                    total += abs(self.network.outputVolume[x,y,z] -
                                 self.trainingOutputVolume[x,y,z])

        return total


    def update(self):
        """Update weights"""

        #step = 0.5
        step = 5.0# * pow(0.9, self.updateCount)

        error = self.error()
        print "NeuralNetwork error: %f" % error

        weights = self.network.weights
        sh = weights.shape

        for x in range(sh[0]):
            for y in range(sh[1]):
                for z in range(sh[2]):

                    weight = weights[x, y, z]

                    weights[x, y, z] = weight + step
                    errorForIncrease = self.error()
                    #print "errorForIncrease", errorForIncrease

                    if errorForIncrease < error:
                        #self.network.offsets[key] = weight + step
                        pass
                    else:
                        weights[x, y, z] = weight - step
                        errorForDecrease = self.error()
                        #print "errorForDecrease", errorForDecrease
                        if errorForDecrease < error:
                            #weights[x, y, z] = weight - step
                            pass
                        else:
                            weights[x, y, z] = weight

        self.updateCount += 1

