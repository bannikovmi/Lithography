import cv2 as cv
import os
import matplotlib.pyplot as plt
 
print(os.listdir("../../../data"))

img = cv.imread("../../../data/proj_scans/(0_720_45)_(0_1280_80)_(0_255_10)/full_0.png")
 
plt.imshow(img)
plt.show()
