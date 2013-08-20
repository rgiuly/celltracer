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

# test for making OBJ files

from numpy import *

 
class Face:
    """Class that represents face in OBJ file"""

    def __init__(self, triangle, normalIndex):
        self.triangle = triangle
        self.normalIndex = normalIndex

    def makeFace(self, indexOffset):
        offsetTriangle = [self.triangle[0] + indexOffset, self.triangle[1] + indexOffset, self.triangle[2] + indexOffset]
        return Face(offsetTriangle, self.normalIndex)

    def toString(self):
        return "%d//%d %d//%d %d//%d" % (self.triangle[0], self.normalIndex, self.triangle[1], self.normalIndex, self.triangle[2], self.normalIndex)


v = [array([0.0,  0.0,  0.0]),
     array([0.0,  0.0,  1.0]),
     array([0.0,  1.0,  0.0]),
     array([0.0,  1.0,  1.0]),
     array([1.0,  0.0,  0.0]),
     array([1.0,  0.0,  1.0]),
     array([1.0,  1.0,  0.0]),
     array([1.0,  1.0,  1.0])]

vn = ["vn  0.0  0.0  1.0",
      "vn  0.0  0.0 -1.0",
      "vn  0.0  1.0  0.0",
      "vn  0.0 -1.0  0.0",
      "vn  1.0  0.0  0.0",
      "vn -1.0  0.0  0.0"]
 
f = [Face([1,  7,  5], 2),
     Face([1,  3,  7], 2),
     Face([1,  4,  3], 6),
     Face([1,  2,  4], 6),
     Face([3,  8,  7], 3),
     Face([3,  4,  8], 3),
     Face([5,  7,  8], 5),
     Face([5,  8,  6], 5),
     Face([1,  5,  6], 4),
     Face([1,  6,  2], 4),
     Face([2,  6,  8], 1),
     Face([2,  8,  4], 1)]

points = [array([0,0,0]),
          array([1,2,3]), 
          array([10,2,3]), 
          array([20,2,3]), 
          array([30,2,3])] 


def makeOBJFile(points, filename):
    """OBJ file creation test that puts cube at each point"""

    outputFile = open(filename, 'w')

    endLine = "\n"
   
    outputFile.write("g cube")
    outputFile.write(endLine)
    
    numCubeVertices = len(v)
    for p in points:
        for i in range(numCubeVertices):
            outputFile.write("v %f %f %f" % (v[i][0] + p[0], v[i][1] + p[1], v[i][2] + p[2]))
            outputFile.write(endLine)

    for vertexNormalString in vn:
        outputFile.write(vertexNormalString)
        outputFile.write(endLine)

    for cubeIndex in range(len(points)):
        vertexIndexOffset = cubeIndex * numCubeVertices
        for faceIndex in range(len(f)):
            face = f[faceIndex].makeFace(vertexIndexOffset)
            outputFile.write("f " + face.toString())
            outputFile.write(endLine)
            
    outputFile.close()



