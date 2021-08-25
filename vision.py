# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

from mss import mss

class Vision:
    def __init__(self):
        self.monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}

    def get_mob_position(self, lower_bound, upper_bound, sct):
        frame = self._get_frame(sct)
        mask = self._apply_mask(frame, lower_bound, upper_bound)
        cnts = self._generate_contours(mask)
        if len(cnts) == 0:
            return None
        return self._get_track_center(cnts)


    def _get_track_center(self, cnts):
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        return (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

    def _generate_contours(self, mask):
        # Unifies all the close borders so it is detected as one.
        #mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        return imutils.grab_contours(cnts)

    def _get_frame(self, sct):
        # sct is being passed here so we can use the syntax
        # with/as
        return np.array(sct.grab(self.monitor))

    def _apply_mask(self, frame, lower_bound, upper_bound):
        '''
        Applies a mask to a frame based on lower/upper bounds
        based on a HSV converted frame. It is used to isolate
        an object on a frame.
        '''
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        return cv2.dilate(mask, None, iterations=2)

    def display_debug(self, lower_bound, upper_bound):
        start = time.time()
        with mss() as sct:

            while True:
                frame = self._get_frame(sct)
                mask = self._apply_mask(frame, lower_bound, upper_bound)
                cnts = self._generate_contours(mask)

                if len(cnts) > 2:
                            # find the largest contour in the mask, then use
                            # it to compute the minimum enclosing circle and
                            # centroid
                    c = max(cnts, key=cv2.contourArea)
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    M = cv2.moments(c)
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                            # only proceed if the radius meets a minimum size
                    if radius > 2:
                                    # draw the circle and centroid on the frame,
                                    # then update the list of tracked points
                        cv2.circle(frame, (int(x), int(y)), int(radius),
                                            (0, 255, 255), 2)
                        #cv2.circle(frame, center, 5, (0, 0, 255), -1)

                cv2.drawContours(frame, cnts, -1, (255, 255, 255), 1)

                cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
                cv2.imshow("Frame", frame)
                cv2.resizeWindow("Frame", 400, 400)

                key = cv2.waitKey(1) & 0xFF
                    # if the 'q' key is pressed, stop the loop
                if key == ord("q"):
                    break

                end = time.time()
                print(1 / (end - start))
                start = end

                time_elapsed = end - start

if __name__ == '__main__':
    vision = Vision()
    lower_bound = (0, 255, 72)
    upper_bound = (35, 255, 154)

    with mss() as sct:
        while True:
            init = time.time()
            print(vision.get_mob_position(lower_bound, upper_bound, sct))
            print(1 / (time.time() - init))

    #vision.display_debug(greenLower, greenUpper)
    #vision.get_mob_position(lower_bound, upper_bound, sct)
