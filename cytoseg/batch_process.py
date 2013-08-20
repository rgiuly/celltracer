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

# Functions to handle chunking of data when processing very large datasets.

import os
import sys
import socket
import re
sys.path.append("..")
import default_path
import getopt
from volume3d_util import Box
from volume3d_util import getImageStackSize
from data_viewer import borderWidthForFeatures
from run_steps import *
import globals
from datetime import datetime


def batchProcessVoxels(segmentationParams, steps, fullRegionToClassify, chunkSize): #todo: make chunkParams a 3D region and a chunk size instea
    """Handles splitting large volume into chunks and processes one chunk in memory at a time
    steps: specifies the steps in the segmentation process that will be run on each chunk
    fullRegionToClassify: full region to be classified
    chunkSize: size of stack (in the Z direction) that represents one chunk"""

    f = fullRegionToClassify

    stackSize = getImageStackSize(segmentationParams['originalImageFilePath'])

    if f.cornerA[2] == None:
        f.cornerA[2] = 0;

    if f.cornerB[2] == None:
        f.cornerB[2] = stackSize[2];

    for zOffset in range(f.cornerA[2],
                         f.cornerB[2],
                         chunkSize):
    
    
        print "zOffset:", zOffset
        overlap = 2 * borderWidthForFeatures[2]

        finalZ = zOffset + chunkSize + overlap
        if finalZ > f.cornerB[2]: finalZ = f.cornerB[2]
        
        regionToClassify = Box([f.cornerA[0], f.cornerA[1], zOffset],
                               [f.cornerB[0], f.cornerB[1], finalZ])
    
        segmentationParams['steps'] = steps #'classifyVoxels'
        segmentationParams['regionToClassify'] = regionToClassify

        runSteps(**segmentationParams)



def batchProcessContours(segmentationParams, stepSets, fullRegionToProcess, chunkSize):
    """Handles splitting large volume into chunks and processes one chunk in memory at a time
    steps: specifies the steps in the segmentation process that will be run on each chunk
    fullRegionToClassify: full region to be classified
    chunkSize: size of stack (in the Z direction) that represents one chunk"""

    f = fullRegionToProcess

    stackSize = getImageStackSize(segmentationParams['originalImageFilePath'])

    if f.cornerA[2] == None:
        f.cornerA[2] = 0;

    if f.cornerB[2] == None:
        f.cornerB[2] = stackSize[2];

    for zOffset in range(f.cornerA[2],
                         f.cornerB[2],
                         chunkSize):
     
        print "zOffset:", zOffset
        overlap = globals.blobOutputCropZUpper() +\
                  globals.blobOutputCropZLower()
        print "zOffset + chunkSize + overlap:", zOffset + chunkSize + overlap

        initialZ = zOffset
        finalZ = zOffset + chunkSize + overlap

        
        if finalZ > f.cornerB[2]:
            finalZ = f.cornerB[2] # This is neccesary to ensure that the final Z for this chunk doesn't exceed the limit specified.
            initialZ = finalZ - (chunkSize + overlap) # This is neccesary to ensure that the chunk isn't so thin than the level set doesn't work. (Less than 4 won't work.) However, the chunksize needs to be sufficiently big.
            if initialZ < 0:
                initialZ = 0
                print "warning: chunk size plus overlap (%d) is larger than the loaded data chunk in the Z dimension (%d)" % (chunkSize + overlap, finalZ)

        print "initialZ", initialZ
        print "finalZ", finalZ

        contourProcessingRegionToClassify = Box([f.cornerA[0], f.cornerA[1], initialZ],
                                                [f.cornerB[0], f.cornerB[1], finalZ])

        params = dict(segmentationParams)
        params['contourProcessingRegionToClassify'] = contourProcessingRegionToClassify
    
        for stepSet in stepSets:
            params['steps'] = stepSet
            print "starting step", datetime.now()
            runSteps(**params)
            print "finished step", datetime.now()

