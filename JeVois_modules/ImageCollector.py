import pyjevois
if pyjevois.pro: import libjevoispro as jevois
else: import libjevois as jevois
import cv2
import numpy as np
import os.path
import datetime

class ImageCollector:
    # ###################################################################################################
    ## Constructor
    def __init__(self):
        # Instantiate a JeVois Timer to measure our processing framerate:
        self.timer = jevois.Timer("timer", 100, jevois.LOG_INFO)

        # Create an ArUco marker detector:
        self.dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.params = cv2.aruco.DetectorParameters_create()
        self.newsecond = 0 

    # ###################################################################################################
    ## Process function with GUI output (JeVois-Pro mode):
    def processGUI(self, inframe, helper):
        # Start a new display frame, gets its size and also whether mouse/keyboard are idle:
        idle, winw, winh = helper.startFrame()

        # Draw full-resolution color input frame from camera. It will be automatically centered and scaled to fill the
        # display without stretching it. The position and size are returned, but often it is not needed as JeVois
        # drawing functions will also automatically scale and center. So, when drawing overlays, just use image
        # coordinates and JeVois will convert them to display coordinates automatically:
        x, y, iw, ih = helper.drawInputFrame("c", inframe, False, False)
        
        # Get the next camera image for processing (may block until it is captured), as greyscale:
        inimg = inframe.getCvBGRp()

        # Start measuring image processing time (NOTE: does not account for input conversion time):
        self.timer.start()

        date = datetime.datetime.now()
        file_exist = True
        c=0
        
        if not date.second % 2 and self.newsecond != date.second:
            
            self.newsecond = date.second
            filename = "/home/jevois/robocup_img/capture-{}-{}-{}".format(str(date.hour),str(date.minute),str(date.second))
            temp_name = filename
            while file_exist:
                if os.path.exists(temp_name+".jpg"):
                    c+=1
                    temp_name=filename+"_"+str(c)
                else:
                    file_exist = False
                    filename = temp_name + ".jpg"
            
            cv2.imwrite(filename,inimg)
            jevois.sendSerial("writing " + filename)
            
        # Write frames/s info from our timer:
        fps = self.timer.stop()
        helper.iinfo(inframe, fps, winw, winh);        

        # End of frame:
        helper.endFrame()
