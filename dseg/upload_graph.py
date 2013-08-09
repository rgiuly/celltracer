from access_database import *
import sqlite3
import os
from dseg_util import *

storageForRegionToContours = cv.CreateMemStorage (0)

outputFolder = "/home/rgiuly/output/paper_cerebellum/dseg_test_z/"

conn = sqlite3.connect(os.path.join(outputFolder, 'example.db'))
cursor = conn.cursor()

graphFilename = "/home/rgiuly/output/paper_cerebellum/dseg_test_z/request_loop_data"

file = open(graphFilename, 'rb')
dictionary = cPickle.load(file)
gr = dictionary['gr']
file.close()



#print "number of regions", len(regions)
#for region in regions.values():

initializeSendContour()

print "nodes:", gr.nodes()

for regionID in gr.nodes():

    region = getRegionByID(cursor, regionID)

    #print "region", region
    contours = regionToContours(storageForRegionToContours, region)
    current = contours
    while(current):
        # send contour to spatial database
        print "z:", region.z
        print "length of contour", len(current)
        #print "contour:",
        #for (x, y) in current:
        #    print (x, y),
        #print
        sendContour(region.z, current)
        current = current.h_next()


