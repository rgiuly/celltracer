import itk
import sys
itk.auto_progress(2)

test = itk.MetaImageIO.New()
print test.CanReadFile("/home/rgiuly/images/overseg/init000.mhd")
