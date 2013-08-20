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

# Node and tree objects.
# Support for saving and loading subtrees to and from file.


import os
import cPickle

class NodeDoesNotExist(Exception):
    """Exception for node does not exist"""
    pass



class Node():
    """Node with a list of children"""    


    count = 0

    def __init__(self, name=None, object=None):
        """
        Initialize node.
        Node contains an object specified by the object paramter.
        """

        if name != None:
            self.name = name
        else:
            self.name = 'node' + str(GroupNode.count)
        
        self.children = []
        self.object = object
        self.enableRecursiveRendering = True
        self.isGroupNode = False
        
        #Node.count += 1
        GroupNode.count += 1


    def shallowCopy(self):
        """Return copy of node that has references to the original objects."""

        nodeCopy = GroupNode(self.name)
        nodeCopy.object = self.object
        nodeCopy.enableRecursiveRendering = self.enableRecursiveRendering
        nodeCopy.isGroupNode = self.isGroupNode
        return nodeCopy


    def __str__(self):
        """String representation of children of this node"""

        result = ' %s(' % self.name 
        for child in self.children:
            result += child.__str__() 
        result += ')'
        return result
    

    def addChild(self, node):
        """Add child to node."""
        self.children.append(node)


    def insertChildAt(self, node, index):
        """Insert child at location in list of children."""
        self.children.insert(index, node)


    def addChildren(self, nodeList):
        """Add list of children nodes"""
        for node in nodeList:
            self.addChild(node)


    def addObjectList(self, objectList):
        """Add a list of objects as children. A DataNode is created for each object."""

        count = 0
        for object in objectList:
            node = DataNode(str(count), 'object-type', {}, object)
            self.addChild(node)
            count += 1


    def addObject(self, object):
        """Wrap an object in a node and add the node as a child."""

        node = Node(name=str(len(self.children)), object=object)
        self.addChild(node)


    def makeChildrenObjectList(self):
        """Returns list of children objects. The objects are unwrapped (they are not inside of DataNodes)."""

        list = []
        for child in self.children:
            list.append(child.object)
        return list
    

    def insertChildrenAt(self, nodeList, index):
        """Insert list of children into children list at given index."""

        for i in range(len(nodeList)):
            node = nodeList[i]
            self.insertChildAt(node, index + i)

    
    def getChild(self, name):
        """Get child node."""
        # todo: this could made more efficient with a dictionary

        for child in self.children:
            if child.name == name:
                return child
        raise NodeDoesNotExist, ("Tried to access node named %s but it wasn't there. (parent node name: %s) (parent node: %s)" % (name, self.name, self))


    def removeChild(self, name):
        """Remove child node that has name given by name parameter"""

        childToRemove = None
        for child in self.children:
            if child.name == name:
                childToRemove = child
                break
        if childToRemove == None:
            raise NodeDoesNotExist, ("Tried to remove node named %s but it wasn't there. (parent node %s.)" % (name, self.name))
        else:
            self.children.remove(childToRemove)


    def numberOfChildren(self):
        """Return number of child nodes."""
        return len(self.children)


    def __setstate__(self, dict):
        """Set state"""
        self.__dict__ = dict
        self.guiComponent = None
    
    
    def __getstate__(self):
        """Get state"""
        result = self.__dict__.copy()
        if 'guiComponent' in result:
            del result['guiComponent']
        return result



class GroupNode(Node):
    """Convenience class that indicates a node has children rather than being a leaf node."""

    def __init__(self, name=None):

        Node.__init__(self, name)
        self.isGroupNode = True



class ActiveProbabilityFilter():
    """
    Provides isValid function that is applied to one node. Decides
    of the object should be shown. If the probability filter is inactive,
    then the object is to be shown. If the filter is active, the
    probability must pass a threshold for the object to be shown.
    """

    def __init__(self, minimumRequiredProbability):
        self.minimumRequiredProbability = minimumRequiredProbability

    def isValid(self, node):

        return not(node.object.filterActive) or\
            node.object.probability() >= self.minimumRequiredProbability



class PersistentDataTree:
    """Data tree with ability to save and restore from file and it that way remain persistent."""

    def __init__(self, rootNode, rootFolderPath):
        """Initialize tree with root node and path to where the data will be store on the filesystem."""
        self.rootNode = rootNode
        self.rootFolderPath = rootFolderPath

    def writeSubtree(self, pathToSubtree):
        """
        Write subtree to filesystem.
        Parameters:
        pathToNode: identifies the node to be saved
        """
        #print pathToSubtree
        node = getNode(self.rootNode, pathToSubtree)
        #print node
        filename = makeFilenameFromNodePath(pathToSubtree)
        #print "filename", filename
        #print "self.rootFolderPath", self.rootFolderPath
        f = open(os.path.join(self.rootFolderPath, filename), "wb")
        #cPickle.dump(node, f)
        pickler = cPickle.Pickler(f)
        pickler.fast = True
        pickler.dump(node)
        f.close()


    def readSubtree(self, pathToSubtree):
        """Reads subtree from file and places it into tree which is specified by rootNode"""

        print "reading subtree", pathToSubtree
    
        if nodeExists(self.rootNode, pathToSubtree):
            parent = getNode(self.rootNode, pathToSubtree[0:-1])
            parent.removeChild(pathToSubtree[-1])
        else:
            createPathIfNeeded(self.rootNode, pathToSubtree[0:-1])
    
    
        # read the node from file and insert it into the data tree
    
        filename = makeFilenameFromNodePath(pathToSubtree)
    
        fullFilename = os.path.join(self.rootFolderPath, filename)
        f = open(fullFilename)
        nodeFromFile = cPickle.load(f)
        f.close()
        #self.refreshGUI()
    
        parent = getNode(self.rootNode, pathToSubtree[0:-1])
        parent.addChild(nodeFromFile)


    def getSubtree(self, pathToSubtree):
        """Get subtree. Read from disk only if necessary."""

        if not(nodeExists(self.rootNode, pathToSubtree)):
            self.readSubtree(pathToSubtree)

        return getNode(self.rootNode, pathToSubtree)

    def subtreeExists(self, pathToSubtree):
        """Return true only if subtree exists."""

        return nodeExists(self.rootNode, pathToSubtree)


    def setSubtree(self, pathToParent, newNode):
        """
        Adds newNode to subtree and saves to file
        """
        #print "setSubtree", pathToParent, newNode.name
        parent = getNode(self.rootNode, pathToParent)
        parent.addChild(newNode)
        self.writeSubtree(tuple(pathToParent) + (newNode.name,))






def getNode(rootNode, nameList):
    """Get node from tree. nameList identifies the node."""

    currentNode = rootNode
    #print 'nameList'
    #print nameList
    for name in nameList:
        #print name
        currentNode = currentNode.getChild(name)
    return currentNode

    
def nodeExists(rootNode, nameList):
    """
    Return true only if node exists.
    Parameters:
    rootNode: root node of the tree
    nameList: identifies the node whose existence is to be checked
    """

    currentNode = rootNode
    for name in nameList:
        try:
            currentNode = currentNode.getChild(name)
        except NodeDoesNotExist:
            return False

    return True
    

def makeFilenameFromNodePath(nodePath):
    """
    Make filename from node path.
    Parameters:
    nodePath: a list of node names (path from root node to specific node)
    return value is a full path for the filesystem. e.g. "folder1/folder2/file.pickle"
    """

    baseFilename = ",".join(nodePath)
    extension = ".pickle"
    return baseFilename + extension


def createPathIfNeeded(rootNode, nodePath):
    """Adds nodes for each element of the nodePath if they do not already exist."""

    currentNode = rootNode

    for name in nodePath:
        try:
            currentNode = currentNode.getChild(name)
        except NodeDoesNotExist:
            currentNode.addChild(DataNode(name, 'type of node', None, None))
            currentNode = currentNode.getChild(name)



def nonnullObjects(inputRootNode):
    """Return list of all non-null objects in the tree."""
    
    resultList = []
    nonnullObjectsHelper(inputRootNode, resultList)
    return resultList


def nonnullObjectsHelper(node, resultList):
    
    if node.object != None:
        resultList.append(node.object)

    for childNode in node.children:
        nonnullObjectsHelper(childNode, resultList)


def nonnullNongroupObjects(inputRootNode):
    """Return list of all objects in the tree that are not null and not groups."""

    resultList = []
    nonnullNongroupObjectsHelper(inputRootNode, resultList)
    return resultList


def nonnullNongroupObjectsHelper(node, resultList):
    
    #print node
    #print node.object != None
    #print node.isGroupNode

    if (node.object != None) and not(node.isGroupNode):
        resultList.append(node.object)
    #print resultList

    for childNode in node.children:
        nonnullNongroupObjectsHelper(childNode, resultList)


def nonnullObjectNodes(inputRootNode):
    "Return list of all non-null object nodes."""

    resultList = []
    nonnullObjectNodesHelper(inputRootNode, resultList)
    return resultList


def nonnullObjectNodesHelper(node, resultList):
    
    if node.object != None:
        resultList.append(node)

    for childNode in node.children:
        nonnullObjectNodesHelper(childNode, resultList)



def copyTree_old(node, filter=None):
    """Deprecated"""
    
    newNode = node.shallowCopy()
    copyTreeHelper_old(node, newNode, filter)
    return newNode


def copyTreeHelper_old(node, newNode, filter):
    """Deprecated"""

    for child in node.children:
        
        print child
        print child.name
        print child.object
        print child.isGroupNode

        if child.isGroupNode or (filter == None) or (filter.isValid(child) == True):

            newChild = child.shallowCopy()
            newNode.addChild(newChild)

            copyTreeHelper_old(child, newChild, filter)


def copyTree(node, filter=None):
    """Copy tree."""

    newNode = node.shallowCopy()
    copyTreeHelper(node, newNode, filter)
    return newNode


def copyTreeHelper(node, newNode, filter):

    for child in node.children:

        printDebugInformation = False
        if printDebugInformation:
            print child
            print child.name
            print child.object
            print child.isGroupNode

        if (filter == None) or (filter.isValid(child) == True):

            newChild = child.shallowCopy()
            newNode.addChild(newChild)

            copyTreeHelper(child, newChild, filter)


class DataNode(GroupNode):
    """
    Represents a piece of data.
    Optionally keeps a reference to GUI components that changes the data value.
    """

    def __init__(self, name, type, params, object):
        
        GroupNode.__init__(self, name)
        
        self.type = type
        self.params = params
        self.object = object
        self.guiComponent = None


    def get(self):
        self.object = self.guiComponent.GetValue()  #todo: you should really always use set method so this should not be necessary 
        return self.guiComponent.GetValue()
    

    def set(self, value):
        self.object = value
        self.guiComponent.SetValue(value)


    def test_old(self):
        n1 = DataNode("root","root",10)
        print 'n1 type'
        print type(n1)
        n2 = DataNode("b","boolean",20)
        n3 = DataNode("c","slider",30)
        n4 = DataNode("d","slider",40)
        n5 = DataNode("e","slider",50)

        n1.addChild(n2)
        n1.addChild(n3)
        n2.addChild(n4)
        n2.addChild(n5)
        
        print 'children types'
        for x in n1.children:
            print type(x)
        f = open("temp.pickle", "w")
        cPickle.dump(n1, f)
        f.close()

        f = open("temp.pickle", "r")
        loadedData = cPickle.load(f)
        print "data loaded from file"
        print loadedData
        f.close()
        
        print 'testing get node'
        print getNode(loadedData, ('particleMotionTool', 'd'))
        
        return n1



