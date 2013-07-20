
import watershed
import scipy
import scipy.misc
import cPickle
result = watershed.watershed2DNumpyRaw(scipy.misc.imread("5faee807-9798-4ce8-8727-2eff8e14b03a.png"), 0.000150, 0.350000, useGradientMagnitude=False)
#for i in range(result.shape[0]):
#    for j in range(result.shape[1]):
#        print result[i, j]
#scipy.misc.imsave("<percent was here>s", result)
pickleFile = open("2bede355-ec38-45e9-9e07-e922779bb5a7.pickle", 'wb')
cPickle.dump(result, pickleFile)
pickleFile.close()
    