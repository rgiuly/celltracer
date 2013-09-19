
import graph_util


# element of a region dictionary should be True or nonexistant
def union(pointDict1, pointDict2):

    union = {}

    for key, value in pointDict1.items():
        union[key] = value
    for key, value in pointDict2.items():
        union[key] = value

    return union


def intersection(pointDict1, pointDict2):

    count = {}
    intersection = {}

    for key, value in pointDict1.items():
        if key in count:
            count[key] += 1
        else:
            count[key] = 1

    for key, value in pointDict2.items():
        if key in count:
            count[key] += 1
        else:
            count[key] = 1

    for key, value in count.items():
        if value == 2:
            intersection[key] = True
 
    return intersection
 
 
def setSubtraction(pointDict1, pointDict2):
 
    result = dict(pointDict1)
    for key in pointDict2:
        if key in result:
            del result[key]
        #print result
 
    return result
 

def listToDict(region):

    dict = {}
    #print "region", region
    for point in region:
        dict[point] = True
    return dict


def linkProbability(region1, region2):

    pointDict1 = listToDict(region1)
    pointDict2 = listToDict(region2)
    return len(intersection(pointDict1, pointDict2))


def linkProbability_old(region1, region2):

    #if abs(region1.z - region2.z) != 1:
    #    return None

    pointDict1 = listToDict(region1)
    pointDict2 = listToDict(region2)
    u = union(pointDict1, pointDict2)
    i = intersection(pointDict1, pointDict2)
    sub1 = setSubtraction(pointDict1, pointDict2)
    sub2 = setSubtraction(pointDict2, pointDict1)

    uSize = len(u)
    iSize = len(i)
    sub1Size = len(sub1)
    sub2Size = len(sub2)

    fraction1 = float(iSize + sub1Size) / float(uSize)
    fraction2 = float(iSize + sub2Size) / float(uSize)

    error1 = abs(1.0 - fraction1)
    error2 = abs(1.0 - fraction2)

    totalError = error1 + error2

    if 0:
        print "uSize", uSize
        print "iSize", iSize
        print "sub1Size", sub1Size
        print "sub2Size", sub2Size
        print "fraction1", fraction1
        print "fraction2", fraction2
        print "error1", error1
        print "error2", error2
        print "totalError", totalError

    maximumError = 2.0

    probability = 1.0 - (totalError / maximumError)

    return probability


if __name__ == "__main__":

    a = graph_util.Region2D()
    a += [(1, 1), (2, 2), (3, 3), (4, 4)]
    #a += [(0, 0), (1, 1), (2, 2)]
    a.z = 1
    b = graph_util.Region2D()
    b += [(0, 0), (1, 1), (2, 2)]
    b.z = 2
    print "a:", a
    print "b:", b

    print linkProbability(a, b)




