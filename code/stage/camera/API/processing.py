import numpy as np
import cv2 as cv

from PyQt5.QtCore import QObject

class QImageProcessor(QObject):

	def __init__(self, config):

		self.config = config
		super().__init__()

	def draw_rect(self, img, rect):
		# Draw a rectangle on image
		
		x1 = rect.left()
		x2 = rect.right()
		y1 = rect.top()
		y2 = rect.bottom()

		color = tuple(self.config["rectangle"]["color"])
		thickness = self.config["rectangle"]["thickness"]

		cv.rectangle(img, (x1, y1), (x2, y2), color=color, thickness=thickness)

	def draw_crosses(self, img, rect):
		# Draw crosses at the vortices of a rectangle on image
		
		x1 = rect.left()
		x2 = rect.right()
		y1 = rect.top()
		y2 = rect.bottom()

		color = tuple(self.config["cross"]["color"])
		thickness = self.config["cross"]["thickness"]
		half_length = self.config["cross"]["half_length"]

		for x in [x1, x2]:
			for y in [y1, y2]:
				cv.line(img, (x-half_length, y), (x+half_length, y),
					color=color, thickness=thickness)
				cv.line(img, (x, y-half_length), (x, y+half_length),
					color=color, thickness=thickness)

	def laplacian(self, img, rect):

		# Perform laplacian transformation on a rectangular region of the image
		x1 = rect.left()
		x2 = rect.right()
		y1 = rect.top()
		y2 = rect.bottom()

		return cv.Laplacian(img[y1:y2, x1:x2], cv.CV_64F)

	def crop(self, img):

		h, w = img.shape[:2]

		pts1 = np.float32([[432, 380], [432, 677], [1125, 382]])
		pts2 = np.float32([[0, 0], [0, h], [w, 0]])
		M = cv.getAffineTransform(pts1, pts2)

		for pt in pts1:
			cv.circle(img, (int(pt[0]), int(pt[1])), 5, (255, 0, 0))

		return cv.warpAffine(img, M, (w, h))