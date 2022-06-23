import pyjevois
if pyjevois.pro: import libjevoispro as jevois
else: import libjevois as jevois
import cv2
import numpy as np

import time
import math

yellowLower=(25,160,55)
yellowHigher=(30,255,255)

class BallTracking:
    # ###################################################################################################
    ## Constructor
    def __init__(self):
        # Instantiate a JeVois Timer to measure our processing framerate:
        self.timer = jevois.Timer("timer", 100, jevois.LOG_INFO)

    # ###################################################################################################
    ## Process function with GUI output (JeVois-Pro mode):
    def processGUI(self, inframe, helper):
        # Start a new display frame, gets its size and also whether mouse/keyboard are idle:
        idle, winw, winh = helper.startFrame()

        # Start measuring image processing time (NOTE: does not account for input conversion time):
        self.timer.start()

        inimg = inframe.getCvRGBA()
        h = int(inimg.shape[0]/2)
        w = int(inimg.shape[1]/2)
        dim = (w,h)
        inimg = cv2.resize(inimg,dim,interpolation=cv2.INTER_AREA)
        
        blurred = cv2.GaussianBlur(inimg,(11,11),0)
        hsv = cv2.cvtColor(inimg,cv2.COLOR_RGB2HSV)

        #apply mask
        mask = cv2.inRange(hsv,yellowLower,yellowHigher)
        mask = cv2.erode(mask,None,iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        cnts, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        center = None
        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            if radius > 0:
                cv2.circle(inimg, (int(x), int(y)), int(radius),(255, 255, 0,255), 2)
                cv2.circle(inimg, (int(x), int(y)), 5, (255, 0, 0,255), -1)
        
                jevois.sendSerial("B {} {} {}".format(int(x), int(y), int(radius)))
        
        helper.drawImage("out",inimg,True,False,True)
        
        fps = self.timer.stop()
        helper.iinfo(inframe,fps,winw,winh)
        
        # End of frame:
        helper.endFrame()
