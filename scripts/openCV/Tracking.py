import cv2
import numpy as np
import time

def nothing(x):
    pass

yellowLower, yellowHigher = (24, 105, 38), (51, 255, 255)

img_l = [".jpg",".jpeg",".png"]
ftype = "vid"

file="data/video2.webm"

for i in img_l:
    if file.find(i) != -1:
        ftype = "img"
    
if ftype == "vid":
    cap = cv2.VideoCapture(file)
else:
    inimg = cv2.imread(file)    
    h = int(inimg.shape[0]/2)
    w = int(inimg.shape[1]/2)
    dim = (w,h)
    inimg = cv2.resize(inimg,dim,interpolation=cv2.INTER_AREA)


cv2.namedWindow("output")
cv2.createTrackbar("Delay", "output", 0, 100,nothing)

while True:

    if ftype == "vid":
        ret, inimg = cap.read()
        if not ret:
            print("error reading video")
            break

    blurred = cv2.GaussianBlur(inimg,(11,11),0)
    hsv = cv2.cvtColor(inimg,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,yellowLower,yellowHigher)
    mask = cv2.erode(mask,None,iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        if radius > 1 :
            cv2.circle(inimg, (int(x), int(y)), int(radius),(0, 255, 255,255), 2)
            cv2.circle(inimg, (int(x), int(y)), 5, (0, 0, 255,255), -1)
    
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    stacked = np.hstack((mask,inimg))
    cv2.imshow("output",cv2.resize(stacked,None,fx=0.8,fy=0.8))

    delay = cv2.getTrackbarPos("Delay", "output")
    time.sleep(delay/100)

    # type q to leave the video or space to play/pause the video 

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

    if key == 32:
        cv2.waitKey()

cap.release()
cv2.destroyAllWindows()