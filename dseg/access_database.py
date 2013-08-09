from sqlalchemy import *

db = create_engine('postgresql://ccdbd_dev:Test753@dev-db.crbs.ucsd.edu:5432/ccdbv2_2')

print "test"


for row in db.execute("select nextval('general_sequence')"):
    annotation_id = row[0]

print "annotation_id", annotation_id


#dataset_id = 831681
dataset_id = 10821524
#model_number = 3
model_number = 1093
print "http://galle.crbs.ucsd.edu:8081/Canvas_GWT_Test3/Canvas_GWT_Test2.html?datasetID=%d&modelID=%d" % (dataset_id, model_number)


#db = create_engine('sqlite:///tutorial.db')
#
db.echo = False  # Try changing this to True and see what happens
#
metadata = MetaData(db)
#
#users = Table('rgiuly_test_table_you_can_remove_this', metadata,
#    Column('user_id', Integer, primary_key=True),
#    Column('name', String(40)),
#    Column('age', Integer),
#    Column('password', String),
#)


def initializeSendContour():

    db.execute("insert into slash_annotation(annotation_id, dataset_id) values(%s, %d)" % (annotation_id, dataset_id))

    db.execute("update slash_annotation set geometry_type='polygon' where annotation_id=%s" % annotation_id)
    db.execute("update slash_annotation set object_name='rgiuly_object_%s' where annotation_id=%s" % (annotation_id, annotation_id))
    db.execute("update slash_annotation set object_name_ont_uri='rgiuly_ont_uri' where annotation_id=%s" % annotation_id)
    db.execute("update slash_annotation set version_number=%d where annotation_id=%s" % (model_number, annotation_id))




def sendContour(zIndex, points):

    pointString = ""

    for i in range(len(points)):
        point = points[i]
        pointString += "%f %f" % (point[0], point[1])
        if i != (len(points) - 1):
            pointString += ", "

    #print "pointString", pointString

    for row in db.execute("select nextval('general_sequence')"):
        geom_id = row[0]

    print "geom_id", geom_id

    query = "insert into slash_geometry(\
         geom_id,\
         polyline,\
         user_id,\
         z_index,\
         modified_time,\
         geometry_type)\
     values(\
         %d,\
         ST_GeomFromText('LINESTRING(%s)'),\
         20018,\
         %d,\
         '2011-05-16 15:36:38',\
         'polygon')" % (geom_id, pointString, zIndex)
    
    
    print "query", query
    db.execute(query)



    for row in db.execute("select nextval('general_sequence')"):
        map_id = row[0]
    
    print "map_id", map_id
    
    map_command = "insert into slash_annot_geom_map(map_id, annotation_id, geometry_id) values(%s, %s, %s)" % (map_id, annotation_id, geom_id)
    
    print map_command
    
    db.execute(map_command)


#sendContour([(10, 10), (100, 10), (100, 100), (10, 100)])





