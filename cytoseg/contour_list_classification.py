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

# Contour list classification.
# Contour list is an ordered set of contours (the contours are stacked on XY planes).
# Functions are provided for classification of the contour sets using random forest.


import orngTest
import orngStat

from containers import *
from cytoseg_classify import *
from probability_object import *


class ContourListProperties(ProbabilityObject):
    """Class for storing properties of contour lists"""


    def __init__(self):

        ProbabilityObject.__init__(self)
        self.featureDict = None
        self.className = None
        self.intersectionOfLabelSets = None
        self.isConnected = None


    def __repr__(self):

        #raise Exception("stop program")

        return "ContourListProperties\n" +\
                "probability: " + str(self.probability()) + "\n" +\
                "filterActive: " + str(self.filterActive) + "\n" +\
                "className: " + str(self.className) + "\n" +\
                "intersectionOfLabelSets: " + str(self.intersectionOfLabelSets) + "\n" +\
                "isConnected: " + str(self.isConnected) + "\n" +\
                str(self.featureDict)



def isConnected(contourListNode):
    """Checks if the labels of the contours have a label in common. If (and onlly if)
    they all share a common object label, then they are connected and the function
    returns True"""

    intersectionOfLabelSets = contourListNode.children[0].object.labelSet
    for contourNode in contourListNode.children:
        intersectionOfLabelSets.intersection_update(contourNode.object.labelSet)

    if intersectionOfLabelSets:
        return True # set is not empty
    else:
        return False # set is empty


def getContourListFeatures(contourListNode, includeIndividualContourFeatures=True):
    """Get the features in contour.features and their differences."""

    featureDict = odict()
    lastContourFeatures = None
    lastContourLocation = None
    firstIteration = True
    count = 0

    for contourNode in contourListNode.children:

        contour = contourNode.object
        

        # add the features in contour.features and their differences
        
        for featureName in contour.features:
            key = 'contour%d_%s' % (count, featureName)
            #print key

            if includeIndividualContourFeatures:
                featureDict[key] = contour.features[featureName]

            if not(firstIteration):
                differenceKey = 'difference_' + key
                featureDict[differenceKey] = lastContourFeatures[featureName] -\
                        contour.features[featureName]

        # add distance as a feature
        
            if not(firstIteration):
                #print "contour.getAveragePointLocation", contour.getAveragePointLocation()
                #print "lastContourLocation", lastContourLocation
                #print linalg.norm(lastContourLocation - contour.getAveragePointLocation())
                featureDict['contour%d_distance' % count] = linalg.norm(lastContourLocation - contour.getAveragePointLocation())

        firstIteration = False
        count += 1
        lastContourFeatures = contour.features
        lastContourLocation = contour.getAveragePointLocation()

    return featureDict


def getContourListProperties(contourListNode):
    """Get contour list properties including the "isConnected" value that specifices
    if the contours in the list belong to a single biological object"""

    contourListProperties = ContourListProperties()
    contourListProperties.featureDict = getContourListFeatures(contourListNode)
    #contourListProperties.className
    #contourListProperties.intersectionOfLabelSets
    contourListProperties.isConnected = isConnected(contourListNode)

    return contourListProperties


def recordFeaturesOfContourLists(dataViewer,
                                 inputTrainingContourListsNodePath,
                                 outputExamplesIdentifier,
                                 recordKnownClassificationWithExamples,
                                 contourListWeightDict):
    """
    Writes features of contour lists to a file
    Parameters:
    inputTrainingContourListsNodePath: contour lists from which features will be recorded
    outputExamplesIdentifier: specifies the base name of the tab file for orange data mining
    recordKnownClassificationWithExamples: (boolean) option to record known classification (for training data)
    contourListWeightDict: specifies how many copies are recorded for each type. This is how the examples are balanced.
    """


    file = open(os.path.join(default_path.cytosegDataFolder, outputExamplesIdentifier + ".tab"), "w")

    print "recordFeaturesOfContourLists file name: " + outputExamplesIdentifier

    contourListsNode =\
        dataViewer.mainDoc.dataTree.getSubtree(inputTrainingContourListsNodePath)

    if len(contourListsNode.children) == 0:
        raise Exception, "No contour lists were found, so there are no features to record."

    # use the feature dictionary of the first node to get a list of feature names
    dictionary = contourListsNode.children[0].object.featureDict
    featureList = []
    for item in dictionary.items():
        key = item[0]
        featureList.append(key)
    
    writeOrangeNativeDataFormatHeader(file, featureList)

    positiveCount = 0
    negativeCount = 0

    for contourListNode in contourListsNode.children:
                
                contourListProperties = contourListNode.object

                # used for membranes
                #dataViewer.writeExample(file,
                #                        contourListProperties.featureDict,
                #                        contourListProperties.isConnected)

                firstLabelCountDict =\
                    contourListNode.children[0].object.labelCountDict

                # For the list of contours, this goes through each contour and
                # determines the minimum number of labels assigned to mitochondria
                # for each individual contour. The point of this is to determine
                # if the contours are associated with a mitochondria or if they
                # are not touching mitochondria at all or touching more than one.
                # For example, if each contour is associated with 1 mitochondria,
                # that's an indication that the contour list goes with exactly one
                # mitochondria.
                if recordKnownClassificationWithExamples:

                    minimum = 10000000
                    for child in contourListNode.children:
                        countDict = child.object.labelCountDict
                        if 'primaryObject' in countDict:
                            value = countDict['primaryObject']
                            if value < minimum:
                                minimum = value
                        else:
                            minimum = 0

                    #if 'primaryObject' in firstLabelCountDict:
                    #    count = firstLabelCountDict['primaryObject']
                    #else:
                    #    count = 0

                    count = minimum
                
                else:

                    # This is typically used before the classification step
                    # when the classification is not known yet. The classification
                    # is to be determined with the classification step.
                    count = None

                if str(count) == '1':
                    numberOfRepeats = contourListWeightDict[True] #20
                elif str(count) == '0':
                    numberOfRepeats = contourListWeightDict[False]
                elif count == None:
                    numberOfRepeats = 1
                else:
                    print "count", count
                    raise Exception('number of repeats not specified')

                if str(count) == '0': negativeCount += 1
                if str(count) == '1': positiveCount += 1

                for i in range(numberOfRepeats):
                    dataViewer.writeExample(file,
                                            contourListProperties.featureDict,
                                            str(count))

    print "positive contour list count without repeats:", positiveCount
    print "negative contour list count without repeats:", negativeCount
                
    
    file.close()
    print "finished recordFeaturesOfContourLists"


def classifyContourLists(dataViewer,
                         inputTrainingExamplesIdentifier,
                         contourListsNodePath):
    """
    Classify contour lists
    Parameters:
    dataViewer: container for program data including contour lists
    inputTrainingExamplesIdentifier: basename for file with training data
    contourListsNodePath: identifies the node with the contour list objects.
     The classification probabilities that are calculated are stored as properties of the contour lists.
    """

    #identifier = 'test'

    dataFilePath = os.path.join(default_path.cytosegDataFolder,
                                            inputTrainingExamplesIdentifier + ".tab")
    data = orange.ExampleTable(dataFilePath)
    
    #depth = 25 # BMC Bioinformatics submission used for cerebellum
    #depth = 25 # BMC Bioinformatics submission used for dentate gyrus
    depth = 25 #5 #test #25 # BMC Bioinformatics submission used for retina

    minimumExamples = len(data) / depth
    
    tree = orngTree.TreeLearner(storeNodeClassifier = 0,
                                storeContingencies=0,
                                storeDistributions=1,
                                minExamples=minimumExamples, ).instance()
    gini = orange.MeasureAttribute_gini()
    tree.split.discreteSplitConstructor.measure = \
     tree.split.continuousSplitConstructor.measure = gini
    tree.maxDepth = depth
    split = 3
    tree.split = orngEnsemble.SplitConstructor_AttributeSubset(tree.split, split)

    logging.info("creating random forest")
    #numTrees = 50 # for BMC Bioinformatics
    numTrees = 50 #100 #test # 50
    forest = orngEnsemble.RandomForestLearner(data,
                                              name="forest",
                                              learner=tree,
                                              trees=numTrees)
    logging.info("finished creating random forest")
    
   
    print dataFilePath
    print "number of examples:", len(data)
    print "tree learner minimumExamples parameter:", minimumExamples
    print "depth:", depth
    print "split:", split
    print "number of trees:", numTrees
    
    count = 0

    print "data.domain.attributes", data.domain.attributes, len(data.domain.attributes) 
    print "data.domain.variables", data.domain.variables, len(data.domain.variables)

    print "Possible classes:", data.domain.classVar.values
    if len(data.domain.classVar.values) == 1:
        print '<ERROR ID=NO_VALID_TRAINING_CONTOURS_WERE_DETECTED TEXT="Contour extraction was performed on the the training data but none of the contours detected fully overlap with training contours given.">'
        raise Exception("There is only one class in the test data.")

    # optionally, calculate accuracy on the training data
    calculateAccuracyOnTrainingData = False
    if calculateAccuracyOnTrainingData:

        import matplotlib.pyplot as pyplot

        #voting = orange.ExampleTable("voting3")

        print "Training Data Accuracy:"

        learners = [orngEnsemble.RandomForestLearner(name="test_forest", learner=tree, trees=50)]

        # not correct:
        # learners = [forest]

        results = orngTest.crossValidation(learners, data, folds=5)

        falsePositiveRates = []
        truePositiveRates = []

        for cutoffInteger in range(1, 20, 1):

            cutoff = float(cutoffInteger) * 0.05

            #cm = orngStat.confusionMatrices(results, cutoff=cutoff, classIndex=1)[0]
            cm = orngStat.confusionMatrices(results, cutoff=cutoff)[0]
            #cm = orngStat.confusionMatrices(results)[0]
            print "cutoff %f:" % cutoff
            print "TP: %i, FP: %i" % (cm.TP, cm.FP)
            print dir(cm)

            falsePositiveRates.append(array(cm.FP, dtype=float) / float(cm.TN + cm.FP))
            print "negatives (cm.TN + cm.FP):", cm.TN + cm.FP
            truePositiveRates.append(array(cm.TP, dtype=float) / float(cm.FN + cm.TP))
            print "positives (cm.FN + cm.TP):", cm.FN + cm.TP
            print "truePositiveRate:", float(cm.TP) / float(cm.FN + cm.TP)


        pyplot.hold(True)
        pyplot.plot(falsePositiveRates, truePositiveRates)
        pyplot.plot(falsePositiveRates, truePositiveRates, 'bo')
        pyplot.hold(False)
        print "falsePositiveRates = ", falsePositiveRates
        print "truePositiveRates = ", truePositiveRates
        #pyplot.title(target)
        pyplot.xlabel('False Positive Rate')
        pyplot.ylabel('True Positive Rate')
        pyplot.grid(True)
        #pyplot.axis([0, 1, 0, 1])
        pyplot.axis([0, falsePositiveRates[0], 0.7, 1])

        if 0:
            pyplot.show()


    print "loading contour lists"
    contourListsNode =\
        dataViewer.mainDoc.dataTree.getSubtree(contourListsNodePath)

    logging.info("classifying contour sets")
    print contourListsNodePath
    print "setting contour list probabilities"
    print "number of contour lists:", len(contourListsNode.children)

    for contourListNode in contourListsNode.children:

        if count % 100 == 0: print "contour list number:", count

        dictionary = getContourListFeatures(contourListNode)
        list = []
        for item in dictionary.items():
            value = item[1]
            list.append(value)
        list.append('0')

        example = orange.Example(data.domain, list)
        p = forest(example, orange.GetProbabilities)    
        
        # todo: this should be checked once immediately after the training data file is read rather than checked here
        if len(p) == 1:
            raise Exception, "There is only one class in the data. There should be two classes like true and false."
        
        contourListNode.object.setProbability(p[1])
        print "classifying, contour list probability:", p[1]

        colorScaleFactor = 5.0

        if 0:
            contourListNode.object.setColor([200 - ((colorScaleFactor * p[1]) * 200),
                                             (colorScaleFactor * p[1]) * 200, 70]) 

        count += 1


    logging.info("finished classifying contour sets")


def classifyContourListsBayes(probabilityFunction,
                              contourListsNode):
    """Deprecated. Naive Bayes classification strategy."""
    
    for contourListNode in contourListsNode.children:

        probabilityProduct = 1.0

        for contourNode in contourListNode.children:
            probability = probabilityFunction(contourNode.object.features)
            probabilityProduct *= probability
            #pass
        
        contourListNode.object = ProbabilityObject()
        contourListNode.object.setProbability(probabilityProduct)

        colorScaleFactor = 100.0
        scaledProbability = colorScaleFactor * probabilityProduct

        for contourNode in contourListNode.children:
            contourNode.object.setColor([200 - (scaledProbability * 200),
                                         scaledProbability * 200, 0])
            contourNode.object.filterActive = False 


def classifyContourListsNodePathBayes(dataViewer,
                                      probabilityFunction,
                                      contourListsNodePath):
    """Deprecated. Naive Bayes classification strategy."""

    contourListsNode =\
        dataViewer.mainDoc.dataTree.getSubtree(contourListsNodePath)

    classifyContourListsBayes(probabilityFunction,
                              contourListsNode)



