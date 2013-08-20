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

# ITK level set operation wrapper

import warnings

try:
    import itk
except ImportError:
    warnings.warn("itk module is not installed")

from sys import argv, stderr
#itk.auto_progress(2)


def shellActiveContour(inputImage, seedPoints, advectionScaling, propagationScaling=2,
                       curvatureScaling=1.0, gradientMagnitudeSigma=1, levelSetNodeValue=5,
                       dimensions=2):
    """Uses the GeodesicActiveContour filter from ITK to fill an object that's is a hollowed out shell."""
    """GeodesicActiveContour parameters are documented in ITK guide."""
    InternalPixelType = itk.F
    #Dimension = 2
    InternalImageType = itk.Image[InternalPixelType, dimensions]
    
    OutputPixelType = itk.UC
    OutputImageType = itk.Image[OutputPixelType, dimensions]



    #smoothing = itk.CurvatureAnisotropicDiffusionImageFilter[InternalImageType, InternalImageType].New(inputImage,
	#	        TimeStep=0.125,
	#		NumberOfIterations=5,
	#		ConductanceParameter=9.0)
    #
    #gradientMagnitude = itk.GradientMagnitudeRecursiveGaussianImageFilter[InternalImageType, InternalImageType].New(smoothing,
    #                    Sigma=float(gradientMagnitudeSigma))

    gradientMagnitude = itk.GradientMagnitudeRecursiveGaussianImageFilter[
                            InternalImageType, InternalImageType].New(inputImage,
                                Sigma=float(gradientMagnitudeSigma))

    invertedGradientMagnitude = itk.MultiplyByConstantImageFilter[InternalImageType, itk.F, InternalImageType].New()
    invertedGradientMagnitude.SetInput(gradientMagnitude.GetOutput())
    invertedGradientMagnitude.SetConstant(-1.0)
    
    invertedInputImage = itk.MultiplyByConstantImageFilter[InternalImageType, itk.F, InternalImageType].New()
    invertedInputImage.SetInput(inputImage)
    invertedInputImage.SetConstant(-1.0)
    
    rescaler = itk.RescaleIntensityImageFilter[InternalImageType, InternalImageType].New(inputImage,
                   OutputMinimum=0,
               OutputMaximum=1)
    
    #rescaler = itk.RescaleIntensityImageFilter[InternalImageType, InternalImageType].New(invertedInputImage,
    #               OutputMinimum=0,
    #           OutputMaximum=1)
    
    gradientMagnitudeRescaler = itk.RescaleIntensityImageFilter[InternalImageType, InternalImageType].New(invertedGradientMagnitude,
                   OutputMinimum=0,
               OutputMaximum=1)

    # make itk seed list

    seeds = itk.VectorContainer[itk.UI, itk.LevelSetNode[InternalPixelType, dimensions]].New()
    seeds.Initialize()

    for seedPointIndex in range(len(seedPoints)):

        seedPosition = itk.Index[dimensions]()
    
        for elementIndex in range(dimensions):
            seedPosition.SetElement(elementIndex,
                                    int(seedPoints[seedPointIndex][elementIndex]))
    	    
        node = itk.LevelSetNode[InternalPixelType, dimensions]()
        node.SetValue(-float(levelSetNodeValue))
        node.SetIndex(seedPosition)
        
        seeds.InsertElement(seedPointIndex, node)

    fastMarching = itk.FastMarchingImageFilter[InternalImageType, InternalImageType].New(rescaler,
                        TrialPoints=seeds,
			SpeedConstant=1.0,
            OutputSize=inputImage.GetBufferedRegion().GetSize() )
    
    
    geodesicActiveContour = itk.GeodesicActiveContourLevelSetImageFilter[InternalImageType, InternalImageType, InternalPixelType].New(fastMarching, gradientMagnitudeRescaler,
                        PropagationScaling=float(propagationScaling),
			CurvatureScaling = float(curvatureScaling),
            AdvectionScaling = float(advectionScaling),
			MaximumRMSError=0.02,
			NumberOfIterations=800
			)
        
    thresholder = itk.BinaryThresholdImageFilter[InternalImageType, OutputImageType].New(geodesicActiveContour,
                        LowerThreshold=-1000,
			UpperThreshold=0,
			OutsideValue=0,
			InsideValue=255)

    #return thresholder.GetOutput()
    geodesicActiveContour.Update()
    return geodesicActiveContour.GetOutput()
    
    
