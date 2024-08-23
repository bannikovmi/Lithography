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

	def laplacian(self, img, rect, transform_img = False):

		# Perform laplacian transformation on a rectangular region of the image
		x1 = rect.left()
		x2 = rect.right()
		y1 = rect.top()
		y2 = rect.bottom()

		laplacian = cv.Laplacian(img[y1:y2, x1:x2], cv.CV_64F)
		
		if transform_img:
			img[y1:y2, x1:x2] = laplacian

		return laplacian
