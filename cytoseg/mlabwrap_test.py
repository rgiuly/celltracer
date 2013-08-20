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

#mlabwrap test



import numpy
#import Numeric
from mlabwrap import mlab
a=[[1.,2.,3.],[4.,5.,6.]]
b=numpy.ones((10,10,10))
b=b*10
b[1,4,6]=1
b[8,8,8]=1
b[8,8,9]=1



def matlabToPythonPointList(matlabPointList):
    newPoints = []
    for point in matlabPointList:
        #print point[0]
        #print point[1]
        #print point[2]
        newPoints.append(numpy.array((point[2]-1, point[0]-1, point[1]-1)))
    return newPoints
    
    

#mlab.sliceView(b)
#mlab.findBlobs(b.flat,[3,3,3],2)
#print mlab.norm(b.flat)
#print mlab.double(b.flat)
#print mlab.findBlobs()

#x, y = mlab.test(nout=2)
#print x
#print y

centroids, areas = mlab.findBlobs(b.flat,5,10,10,10,nout=2)
print 'centroids'
print centroids
print matlabToPythonPointList(centroids)
print 'areas'
print areas


# test to see if flatten and reshape work
#c = numpy.array([[1,2,3,4],[5,6,7,8]])
#d = c.flatten();
#e = mlab.reshape(d,c.shape[1],c.shape[0])

#print c
#print e


def reverseIndices(v):
    v1 = numpy.zeros((v.shape[2],v.shape[1],v.shape[0]))
    for i in range(0,v.shape[0]):
        for j in range(0,v.shape[1]):
            for k in range(0,v.shape[2]):
                v1[k,j,i] = v[i,j,k]
    return v1;

c = numpy.zeros((2,2,2));
#d = numpy.zeros((2,2,2));
c[0,0,0] = 1
c[0,0,1] = 2
c[0,1,0] = 3
c[0,1,1] = 4
c[1,0,0] = 5
c[1,0,1] = 6
c[1,1,0] = 7
c[1,1,1] = 80
d = reverseIndices(c)
            
'reshape and write matrix'            
mlab.reshapeAndWriteMatrix(d.flatten(),2,2,2)










