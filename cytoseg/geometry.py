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

# Geometry utility functions



import copy
import numpy.linalg
from numpy import *

#define MIN(x,y) (x < y ? x : y)
#define MAX(x,y) (x > y ? x : y)
#define INSIDE 0
#define OUTSIDE 1

#typedef struct {
#   double x,y;
#} Point;




def insidePolygon(polygonPoints, p):
  """Returns true if point p is inside polygon."""
  counter = 0;
  #double xinters;
  #Point p1,p2;
  N = len(polygonPoints)
  p1 = polygonPoints[0];
  for i in range(1, N+1):
    p2 = polygonPoints[i % N];
    if (p[1] > min(p1[1],p2[1])):
      if (p[1] <= max(p1[1],p2[1])):
        if (p[0] <= max(p1[0],p2[0])):
          if (p1[1] != p2[1]):
            xinters = (p[1]-p1[1])*(p2[0]-p1[0])/(p2[1]-p1[1])+p1[0]
            if (p1[0] == p2[0] or p[0] <= xinters):
              counter += 1
    #p1 = copy.deepcopy(p2);
    p1 = p2


  if ((counter % 2) == 0):
    return False
  else:
    return True


#def test():
#    polygonPoints = [[0,0],[10,0],[10,10],[0,10]]
#    print insidePolygon(polygonPoints, [.5,.5])
#    print insidePolygon(polygonPoints, [-1,.5])

    
#test()
    
    
    
def distance(vector1, vector2):
    """Euclidean distance from point specified by vector1 to point specified by vector2"""
    return numpy.linalg.norm(vector2-vector1)


def centerPoint(point1, point2):
    """Center between two points"""
    return (array(point1) + array(point2)) / 2.0


def unitVectorFromPoints(startPoint, endPoint):
    """Unit vector pointing from startPoint to endPoint"""
    return (endPoint - startPoint) / distance(startPoint, endPoint)

