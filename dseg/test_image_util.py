from image_util import *

cv_im = cv.CreateImage((320,200), cv.IPL_DEPTH_8U, 1)
cv.SetZero(cv_im)
cv.Circle(cv_im, (100, 100), 15, (255, 255, 0, 0))
pi = CVToPIL(cv_im)
pi.save(r"o:\temp\output\test_image.jpg", "JPEG")

cv_im = cv.CreateImage((320,200), cv.IPL_DEPTH_8U, 3)
cv.SetZero(cv_im)
cv.Circle(cv_im, (100, 100), 15, (255, 255, 0, 0))
pi = CVToPIL(cv_im, color=True)
pi.save(r"o:\temp\output\test_image_color.jpg", "JPEG")
