#!/usr/bin/env python

from PIL import Image, ImageSequence
import sys, os, cv
from image_util import *


if 0:
    filename = sys.argv[1]
    im = Image.open(filename)
    original_duration = im.info['duration']
    frames = [frame.copy() for frame in ImageSequence.Iterator(im)]    
    frames.reverse()
else:
    original_duration = 500


cv_im = cv.CreateImage((320,200), cv.IPL_DEPTH_8U, 3)
cv.SetZero(cv_im)
cv.Circle(cv_im, (100, 100), 15, (255, 255, 0, 0))
pi1 = CVToPIL(cv_im, color=True)

cv_im = cv.CreateImage((320,200), cv.IPL_DEPTH_8U, 3)
cv.SetZero(cv_im)
cv.Circle(cv_im, (100, 100), 25, (255, 255, 0, 0))
pi2 = CVToPIL(cv_im, color=True)


frames1 = [pi1, pi2]

for im in frames1:
    print im
    print isinstance(im, Image.Image)

from images2gif import writeGif
#writeGif("reverse_" + os.path.basename(filename), frames1, duration=original_duration/1000.0, dither=0)
filename = r"o:\temp\output\animation_test.gif"
writeGif(filename, frames1, duration=original_duration/1000.0, dither=0)
print filename

