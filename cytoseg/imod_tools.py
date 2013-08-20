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

# Tools for interacting with IMOD files.




import struct
import pickle
import numpy


global indexOfFirstPoint
global sizeOfInt
global sizeOfFloat
global sizeOfPoint

indexOfFirstPointInContourChunk = 20
sizeOfInt = 4
sizeOfFloat = 4
sizeOfPoint = 3 * sizeOfFloat  


def readPointList(file):

    points = []
    
    pointList = pickle.load(file)
    
   
    for coordinateList in pointList:
        point = numpy.array(coordinateList)

        
        points.append(point)

    return points




def chunkSize(s, location):
    """Gets chunksize at given location in string"""
    #global restOfFile
    # s is a string
    id = getIdAt(s, location)
    
    if id == 'OBJT':
        return 4 + 176
       
    elif id == 'CONT':
        psize = struct.unpack('>i', s[location+4:location+8]) #number of points in contour
        return 4 + 16 + (12 * psize[0])
    
    elif id == 'MESH':
        #print "error: mesh handling not in the program yet"
        meshData = MeshData()
        meshData.readFromString(s[location:])
        return 20 + (meshData.vsize * 12) + (meshData.lsize * 4) 
        
    elif id == 'IEOF':
        #return EOF
        return 4

    elif id == 'IMAT':
        #restOfFile = s[location:]
        chunkSize = struct.unpack('>i', s[location+4:location+8])
        return 8 + chunkSize[0]

        
    else:
        chunkSize = struct.unpack('>i', s[location+4:location+8])
        return 8 + chunkSize[0]
    

def getIdAt(string, location):
    """Gets ID at given location in string"""
    id = string[location:location+idLength]
    return id

def readInt(string):
    list = struct.unpack('>i', string)
    return list[0]
    
def readFloat(string):
    list = struct.unpack('>f', string)
    return list[0]

def readPoint(string):
    numberList = []
    for i in range(0, 3 * sizeOfFloat, sizeOfFloat): 
        numberList.append(readFloat(string[i:i+sizeOfFloat]))
    
    return numpy.array(numberList)
    
    

def readContourChunk(string):
    """Read chunk of IMOD file that describes a contour."""
    if getIdAt(string, 0) != 'CONT':
        print 'error: contour chunk should start with CONT'

            
    numPoints = readInt(string[4:4+sizeOfInt])
    print 'numPoints'
    print numPoints
    
    points = []
    for i in range(indexOfFirstPointInContourChunk, 
                   indexOfFirstPointInContourChunk + numPoints * sizeOfPoint, sizeOfPoint): 
        points.append(readPoint(string[i:i+sizeOfPoint]))

    return points
   

class Chunk:
    """Represents chunk in IMOD file"""
    def __init__(self, text):
        self.text = text
    
    def __str__(self):
        return "Chunk" + self.text[:4]
        #return "%s chunk size %d" % (self.text[0:4], len(self.text))

    def __repr__(self):
        return "Chunk" + self.text[:4]
        #return "%s chunk size %d" % (self.text[0:4], len(self.text))

    
class ModelData:
    """Class to hold IMOD model data"""
    def __init__(self):
        self.id = '........'
        self.name = 'name' #char
        self.xmax = 100000 #int
        self.ymax = 100000 #int
        self.zmax = 100000 #int
        self.objsize = 0 #int, number of objects in the model
        self.flags = 0  #uint
        self.drawmode = 1  #int
        self.mousemode = 1 #int
        self.blacklevel = 0    #int
        self.whitelevel = 255  #int
        self.xoffset = 0  #float
        self.yoffset = 0  #float
        self.zoffset = 0  #float
        self.xscale = 1  #float
        self.yscale = 1  #float
        self.zscale = 1  #float
        self.object = 1 #int, current object
        self.contour = 1 #int, current contour
        self.point = 1 #int, current point
        self.res = 1   #int      
        self.thresh = 1 #int
        self.pixsize = 1 # float 
        self.units = 0 #int     
        self.csum = 0 #int
        self.alpha = 0 #float
        self.beta = 0  #float
        self.gamma = 0 #float
        
    formatString = '>8s128siiiiIiiiiffffffiiiiifiifff'
        
    def readFromString(self, s):
        """Read model data from string."""
        data = struct.unpack(ModelData.formatString, s)
        (self.id, self.name, self.xmax, self.ymax, self.zmax, self.objsize,
         self.flags, self.drawmode, self.mousemode, self.blacklevel,
         self.whitelevel, self.xoffset, self.yoffset, self.zoffset,
         self.xscale, self.yscale, self.zscale, self.object, self.contour,
         self.point, self.res, self.thresh, self.pixsize, self.units,
         self.csum, self.alpha, self.beta, self.gamma) = data
    
    def makeString(self):
        """Write model data to string."""
        return struct.pack(ModelData.formatString, self.id, self.name, self.xmax, self.ymax, self.zmax, self.objsize,
         self.flags, self.drawmode, self.mousemode, self.blacklevel,
         self.whitelevel, self.xoffset, self.yoffset, self.zoffset,
         self.xscale, self.yscale, self.zscale, self.object, self.contour,
         self.point, self.res, self.thresh, self.pixsize, self.units,
         self.csum, self.alpha, self.beta, self.gamma)
        

class ObjectData:
    """Class for object data"""
    def __init__(self):

       self.id = "chunk id"
       self.name = "object name"  # char, 64 characters 
       self.extra = "extra bytes" # uint, 64 bytes of extra data for future use
       self.contsize = 0 #int   Number of Contours in object.
       self.flags = 0 #uint      bit flags for object (IMOD_OBJFLAG...).
       self.axis = 0 #int       Z = 0, X = 1, Y = 2. (unused)
       self.drawmode = 0 #int   Tells type of scattered points to draw (unused)
       self.red = 1 #float        Color values, range is (0.0 - 1.0)
       self.green = 0 #float      
       self.blue = 0 #float       
       self.pdrawsize = 1 #int    Default radius in pixels of scattered points in 3D.
       self.symbol = 1 #uchar       Point Draw symbol in 2D, default is 1.
       self.symsize = 1 #uchar      Size of 2D symbol; radius in pixels.
       self.linewidth2 = 1 #uchar   Linewidth in 2-D view.
       self.linewidth = 1 #uchar    Linewidth in 3-D view.
       self.linesty = 0 #uchar      Line draw style, 0 = solid; 1 = dashed (unused).
       self.symflags= 0 #uchar     
       self.sympad = 0 #uchar       Set to 0, for future use.
       self.trans = 0 #uchar        Transparency, range is (0 to 100)
       self.meshsize = 0 #int     Number of meshes in object.
       self.surfsize = 1 #int     Max surfaces in object.

    formatString = '>4s64s64siIiiffficcccccccii'

    def readFromString(self, s):
        """Read object data from string."""
        print self.formatString
        data = struct.unpack(self.formatString, s)
        
        (self.id, self.name, self.extra, self.contsize, self.flags,
         self.axis, self.drawmode, self.red, self.green, self.blue,
         self.pdrawsize, self.symbol, self.symsize, self.linewidth2,
         self.linewidth, self.linesty, self.symflags, self.sympad,
         self.trans, self.meshsize, self.surfsize) = data

    def makeString(self):
        """Write object data to string."""
        return struct.pack(self.formatString, self.id, self.name, self.extra, self.contsize, self.flags,
                            self.axis, self.drawmode, self.red, self.green, self.blue,
                            self.pdrawsize, self.symbol, self.symsize, self.linewidth2,
                            self.linewidth, self.linesty, self.symflags, self.sympad,
                            self.trans, self.meshsize, self.surfsize)
          




class MeshData:
    """Class to hold mesh data"""

    def __init__(self):

        self.id = "chunk id"
        self.vsize = 0 #int (4 bytes)   Size of vertex array (# of triple floats).
        self.lsize = 0 #int (4 bytes)  Size of index array.
        self.flag = 0 #uint (4 bytes)        flag    Bit 16 on  : normals have magnitudes.
        #                           Bits 20-23 are resolution : 0 for high, 
        #                          1 for lower resolution, etc.
        self.time = 0 #short (2 bytes)   Contains a time index or 0
        self.surf = 0 #short (2 bytes)   Contains a surface number or 0
        
        

    formatString = '>4siiIhh'

    def readFromString(self, s):
        """Read mesh data from string."""
        print self.formatString
        
        # todo: note this does note read the vert and index data
        data = struct.unpack(self.formatString, s[0:20])
        
        (self.id, self.vsize, self.lsize, self.flag, self.time, self.surf) = data

          




def readIMODString(s):
    """Read IMOD file string consisting of multiple chunks"""
    chunks = []
    current = sizeOfModelDataStructure
    while current < len(s):
        sz = chunkSize(s, current)
        
        chunks.append(Chunk(s[current:current+sz]))

        if sz == EOF:
            break
        current += sz    
    
    return chunks


def getAllContoursFromIMODChunks(chunks):
    """Read all contours from chunks in the IMOD file"""

    contours = []
    for chunk in chunks:
        if chunk.text[:4] == 'CONT':
            points = readContourChunk(chunk.text)
            #print points
            contours.append(points)
            
    return contours
    
    
def makeContourForSingleSphere(pt, volumeShape, radiusOfSphere):
    """Make contours for a single sphere at point pt"""

    psize = 1 # int, number of points in contour
    flags = 0 # uint
    time = 0  # int
    surf = 0  # int
    
    #points
    #pt = [10, 20, 30]  # floats
    
    id = 'CONT'
    #data = struct.pack('>iIiifff', psize, flags, time, surf, pt[1], 141-pt[0], pt[2])
    data = struct.pack('>iIiifff', psize, flags, time, surf, pt[0], volumeShape[1] - pt[1], pt[2])
    
    return id + data + makeSizeDataChunk(radiusOfSphere)   
        

def makeSizeDataChunk(radiusOfSphere):
    """Make size data chunk"""

    psize = 1  # assuming only one point
    
    id = 'SIZE'
    lengthIndicator = 4 * psize
    data = struct.pack('>if', lengthIndicator, radiusOfSphere)
    
    return id + data   




def makeIMODFile(filename, points, sphereRadius):
    """Make imod file with sphere at each point given by points"""
    
    IMODFileInsertPoints("template.imod", filename, points, sphereRadius)
    

def old_IMODFileInsertPoints(inputFilename, outputFilename, points, sphereRadius):
    """Deprecated"""
    #file = open('template.imod', "rb")
    
    file = open(inputFilename, 'rb')
    str = file.read()
    file.close()
    
    #objectDataStructureSize = 176
        
        
    #readImodFile(str)
    readImodString(str)
    
    #print makeContourForSingleSphere()
    
    md = ModelData()
    md.readFromString(str[0:sizeOfModelDataStructure])
    print md.id
    print md.name
    print md.objsize
    print md.makeString()
    md.objsize = 1
    
    sz = chunkSize(str, sizeOfModelDataStructure)
    print ("size of object data %d" % sz)
    od = ObjectData()
    od.readFromString(str[sizeOfModelDataStructure:sizeOfModelDataStructure+sz])
    print "object contours"
    print od.contsize
    print od.id

    od.contsize = len(points)
    
    #outFile = open('c:\\temp\\out.imod', 'wb')
    #outFile = open(filename + "_inserted", 'wb')
    outFile = open(outputFilename, 'wb')

    outFile.write(md.makeString())
    outFile.write(od.makeString())
    for p in points:
        outFile.write(makeContourForSingleSphere(p, sphereRadius))
    #outFile.write('IEOF')
    outFile.write(restOfFile)
    outFile.close()
    
    
    #template = str[0:firstChunkLocation]

        

def IMODFileInsertPoints(inputFilename, outputFilename, points, volumeShape, sphereRadius):
    """Inserts more points into existing IMOD file"""

    #file = open('template.imod', "rb")
    
    file = open(inputFilename, 'rb')
    str = file.read()
    file.close()
    
    #objectDataStructureSize = 176
        
        
    #readImodFile(str)
    chunks = readIMODString(str)
    #i = indexOfFirstContourChunk(chunks)
    
    #print makeContourForSingleSphere()
    
    print chunks
    
    md = ModelData()
    md.readFromString(str[0:sizeOfModelDataStructure])
    print md.id
    print md.name
    print md.objsize
    #print md.makeString()
    md.objsize += 1
    
    sz = chunkSize(str, sizeOfModelDataStructure)
    print ("size of object data %d" % sz)
    od = ObjectData()
    od.readFromString(str[sizeOfModelDataStructure:sizeOfModelDataStructure+sz])
    print "object contours"
    print od.contsize
    print od.id

    od.contsize = len(points)
    
    #outFile = open('c:\\temp\\out.imod', 'wb')
    #outFile = open(filename + "_inserted", 'wb')
    outFile = open(outputFilename, 'wb')

    outFile.write(md.makeString())
    outFile.write(od.makeString())
    for p in points:
        outFile.write(makeContourForSingleSphere(p, volumeShape, sphereRadius))
    #outFile.write('IEOF')
    #outFile.write(restOfFile)
    
    # skips the first chunk (which is object data) because it has already been written to the file
    #for i in range(1, len(chunks)):
    #    outFile.write(chunks[i].text)


    for i in range(0, len(chunks)):
        outFile.write(chunks[i].text)

    
    outFile.close()
    
    
    #template = str[0:firstChunkLocation]

    
    
#pointsExample = [[10,20,30],[10,30,20],[20,20,20]]

def getAllContours(filename):
    """Gets all contours from IMOD file"""

    file = open(filename, "rb")
    s = file.read()
    file.close()
    return getAllContoursFromIMODChunks(readIMODString(s))



firstHeaderSize = 8
sizeOfModelDataStructure = firstHeaderSize + 128 + (26 * 4)
idLength = 4
EOF = -1

        
 
    
    
     
              
           
