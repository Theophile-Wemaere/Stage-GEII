import cv2
import numpy as np
import time

yellowLower, yellowHigher = (24, 105, 38), (51, 255, 255)

def isclose(a,b,maxi):
    if a <= b+maxi and a>=b-maxi:
        return True
    else:
        return False

def nothing(x):
    pass

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

x,y=0,0

while True:

    if ftype == "vid":
        ret, inimg = cap.read()
        if not ret:
            print("error reading video")
            break

    circle_img = np.copy(inimg)
    mask_img = np.copy(inimg)

    ######################################################## Mask detection

    blurred = cv2.GaussianBlur(inimg,(11,11),0)
    hsv = cv2.cvtColor(inimg,cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv,yellowLower,yellowHigher)
    mask = cv2.erode(mask,None,iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    center = None
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        if radius > 5 and radius < 140 : 
            print(radius)
            cv2.circle(mask_img, (int(x), int(y)), int(radius),(0, 0, 255,255), 2)
           
    ######################################################## Circles detection

    gray = cv2.cvtColor(inimg, cv2.COLOR_BGR2GRAY)
    gray_blurred = cv2.blur(gray, (3, 3))
    detected_circles = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, 1, 20, param1 = 50, param2 = 30, minRadius = 1, maxRadius = 40)
    #circles = []

    if detected_circles is not None:
        detected_circles = np.uint16(np.around(detected_circles))
        # store the circles in an array for later
        new_frame = 1
        for pt in detected_circles[0, :]:
            a, b, r = pt[0], pt[1], pt[2]
            #circles.append((a,b,r))
            cv2.circle(circle_img, (a, b), r, (0, 255, 0), 2)

            if isclose(x, a, 5) and isclose(y,b,5) and isclose(radius, r, 1) and new_frame == 1:
                cv2.circle(inimg, (int(x), int(y)), int(radius),(0, 255, 255,255), 2)
                cv2.circle(inimg, (a, b), r, (0, 255, 0), 2)
                new_frame = 0
 
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    gray_blurred = cv2.cvtColor(gray_blurred, cv2.COLOR_GRAY2BGR)
    stacked1 = np.hstack((mask,circle_img))
    stacked2 = np.hstack((mask_img,inimg))
    stacked = np.vstack((stacked1,stacked2))
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