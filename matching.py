import time
import cv2 as cv
import numpy as np
from Commands import Commands
from Item import Item
from Cords import Cords
from matplotlib import pyplot as plt

from mss import mss

class Matcher:
	'''
	This class should be able to detect objects in Minecraft.
	This is a really hard-coded/alpha implementation of what is expected.
	As it is, it can only match icons if they have the exact same proportions.

	Please, someone help with multi-scale template matching :(
	'''
	def __init__(self):
		pass

	def detect_item(self, item: Item) -> list[Cords]:
		'''
		Uses template match to get the location of an item on the screen.
		'''
		img_rgb = self._take_screenshot()
		img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
		#img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGRA2BGR)
		template = cv.imread(item.value, 0)


		w, h = template.shape[::-1]

		res = cv.matchTemplate(img_gray,template,cv.TM_CCOEFF_NORMED)
		threshold = 0.9
		loc = np.where( res >= threshold)

		cords_array = []

		for pt in zip(*loc[::-1]):
			cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
			cords_array.append(Cords(pt[0] + w // 2, pt[1] + h // 2))

		cv.imwrite('res.png',img_rgb)
		return cords_array

	def _take_screenshot(self):
		'''
		Takes an screenshot of your monitor [or minecraft] and returns the 
		loaded image as a cv2 retval.
		'''
		with mss() as sct:
		# Part of the screen to capture
			monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
			img = np.array(sct.grab(monitor))
			return img


	def detect_mob(self):
		pass

if __name__ == '__main__':
	m = Matcher()
	time.sleep(3)
	m.detect_item(Item.BLAZEROD)