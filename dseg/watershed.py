import itk
import sys
import scipy
import uuid
import os
import cPickle
itk.auto_progress(2)


def watershed2DITK(input, threshold, level, useGradientMagnitude):


    if useGradientMagnitude:
        diffusion = itk.GradientAnisotropicDiffusionImageFilter.IF2IF2.New()

        #diffusion.SetInput(reader.GetOutput())
        diffusion.SetInput(input)

        diffusion.SetTimeStep(0.0625)
        diffusion.SetConductanceParameter(9.0) # use for cells separated by thin boundaries
        diffusion.SetNumberOfIterations( 5 );
        
        gradient = itk.GradientMagnitudeImageFilter.IF2IF2.New()
        gradient.SetInput(diffusion.GetOutput())
        input = gradient.GetOutput()


    # gaussian0 sigma was 5, gaussian1 segma was 3

    if 0:
        gaussian0 = itk.RecursiveGaussianImageFilter.IF2IF2.New()
        gaussian0.SetSigma(1.0)
        gaussian0.SetDirection(0)
        #gaussian0.SetInput(reader.GetOutput())
        gaussian0.SetInput(input)
        
        gaussian1 = itk.RecursiveGaussianImageFilter.IF2IF2.New()
        gaussian1.SetSigma(1.0)
        gaussian1.SetDirection(1)
        gaussian1.SetInput(gaussian0.GetOutput())
        
        cast1 = itk.CastImageFilter.IF2IUC2.New()
        cast1.SetInput(gaussian1.GetOutput())
        writerGaussian = itk.ImageFileWriter.IUC2.New()
        writerGaussian.SetFileName("gaussian.png")
        writerGaussian.SetInput(cast1.GetOutput())
        writerGaussian.Update()

    gaussianImage = gaussian2DITK(input)

    invert = itk.InvertIntensityImageFilter.IF2IF2.New()
    invert.SetMaximum(1.0)
    invert.SetInput(gaussianImage)

    watershed = itk.WatershedImageFilter.IF2.New()

    # testing with this
    # use this for Christine's data with axons
    #watershed.SetInput(gradient.GetOutput())


    if useGradientMagnitude:
        watershed.SetInput(gaussianImage)
        #watershed.SetInput(reader.GetOutput())
        #watershed.SetInput(gaussian1.GetOutput())
    else:
        # use this for neuropil with thin cell boundaries
        watershed.SetInput(invert.GetOutput())

    # use this for neuropil with thin cell boundaries
    #watershed.SetThreshold(0.00015)

    #watershed.SetThreshold(0.00015) # was using this for test in DP2 paper
    watershed.SetThreshold(threshold)

    # option:
    #watershed.SetLevel(0.45) # for gradient
    #watershed.SetLevel(0.30) # for gradient, was using this for test in DP2 paper
    #watershed.SetLevel(0.25) # for raw image, "c:\Python26\python.exe" watershed.py out0002_blur_inv.png out_raw.png
    watershed.SetLevel(level)
    
    relabel = itk.RelabelComponentImageFilter.IUL2IUS2.New()
    relabel.SetInput( watershed.GetOutput() )
    
    cast = itk.CastImageFilter.IUS2IUC2.New()
    cast.SetInput( relabel.GetOutput() )

    cast2 = itk.CastImageFilter.IUS2IF2.New()
    cast2.SetInput( relabel.GetOutput() )
    cast2.Update()
    
    #cast.SetInput(gaussian.GetOutput())
    
    writer = itk.ImageFileWriter.IUC2.New()
    #writer.SetFileName( sys.argv[2] )
    writer.SetFileName("watershed_test.png")
    writer.SetInput( cast.GetOutput()  )
    writer.Update()

    return cast2.GetOutput()


def gaussian2DITK(input):

    gaussian0 = itk.RecursiveGaussianImageFilter.IF2IF2.New()
    gaussian0.SetSigma(1.0)
    gaussian0.SetDirection(0)
    gaussian0.SetInput(input)
    
    gaussian1 = itk.RecursiveGaussianImageFilter.IF2IF2.New()
    gaussian1.SetSigma(1.0)
    gaussian1.SetDirection(1)
    gaussian1.SetInput(gaussian0.GetOutput())

    return gaussian1.GetOutput()


# good default values: threshold=0.00015, level=0.25
def watershed2DNumpy(array, threshold, level, useGradientMagnitude=True):

    inputFilename = "temp_" + str(uuid.uuid4()) + ".png"
    outputFilename = "temp_" + str(uuid.uuid4()) + ".pickle"
    pythonFilename = "temp_" + str(uuid.uuid4()) + ".py_temp"
    scipy.misc.imsave(inputFilename, array)

    string = """
import watershed
import scipy
import scipy.misc
import cPickle
result = watershed.watershed2DNumpyRaw(scipy.misc.imread("%s"), %f, %f, useGradientMagnitude=%s)
#for i in range(result.shape[0]):
#    for j in range(result.shape[1]):
#        print result[i, j]
#scipy.misc.imsave("<percent was here>s", result)
pickleFile = open("%s", 'wb')
cPickle.dump(result, pickleFile)
pickleFile.close()
    """ % (inputFilename, threshold, level, useGradientMagnitude, outputFilename)
    print string

    file = open(pythonFilename, 'w')
    file.write(string)
    file.close()

    #execfile(pythonFilename)
    os.system("python" + " " + pythonFilename)

    #result = scipy.misc.imread(outputFilename)
    fileForPickle = open(outputFilename, 'rb')
    result = cPickle.load(fileForPickle)
    fileForPickle.close()

    os.remove(inputFilename)
    os.remove(outputFilename)
    os.remove(pythonFilename)

    return result


# this leaks memory
def watershed2DNumpyRaw(array, threshold, level, useGradientMagnitude=True):

    image_type = itk.Image[itk.F, 2]
    itk_py_converter = itk.PyBuffer[image_type]

    image_type_long = itk.Image[itk.F, 2]
    itk_py_converter_long = itk.PyBuffer[image_type_long]

    itk_image = itk_py_converter.GetImageFromArray(array.tolist())

    result = watershed2DITK(itk_image, threshold, level, useGradientMagnitude)

    image_array = itk_py_converter_long.GetArrayFromImage(result)

    return image_array


#def gaussian2DNumpy(array):
#
#    image_type = itk.Image[itk.F, 2]
#    itk_py_converter = itk.PyBuffer[image_type]
#
#    image_type_long = itk.Image[itk.F, 2]
#    itk_py_converter_long = itk.PyBuffer[image_type_long]
#
#    itk_image = itk_py_converter.GetImageFromArray(array.tolist())
#
#    result = gaussian2DITK(itk_image)
#
#    image_array = itk_py_converter_long.GetArrayFromImage(result)
#
#    return image_array



def gaussian2DNumpy(array, sigma):

    print "array", array
    print "sigma", sigma
    return scipy.ndimage.filters.gaussian_filter(array, sigma)





#reader = itk.ImageFileReader.IF2.New()
#reader.SetFileName(sys.argv[1])
#watershed2DITK(reader.GetOutput())
