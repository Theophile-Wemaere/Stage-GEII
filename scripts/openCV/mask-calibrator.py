#finding hsv range of target object(pen)
import cv2
import numpy as np
import time
# A required callback method that goes into the trackbar function.
def nothing(x):
    pass

img_l = [".jpg",".jpeg",".png"]
ftype = "vid"

file="data/salle1.jpg"

for i in img_l:
    if file.find(i) != -1:
        ftype = "img"
    
if ftype == "vid":
    cap = cv2.VideoCapture(file)
else:
    frame = cv2.imread(file)    
    h = int(frame.shape[0]/2)
    w = int(frame.shape[1]/2)
    dim = (w,h)
    frame = cv2.resize(frame,dim,interpolation=cv2.INTER_AREA)

cv2.namedWindow("mask-calibrator")
cv2.createTrackbar("Hue - min", "mask-calibrator", 0, 179, nothing)
cv2.createTrackbar("Sat - min", "mask-calibrator", 0, 255, nothing)
cv2.createTrackbar("Val - min", "mask-calibrator", 0, 255, nothing)
cv2.createTrackbar("Hue - max", "mask-calibrator", 179, 179, nothing)
cv2.createTrackbar("Sat - max", "mask-calibrator", 255, 255, nothing)
cv2.createTrackbar("Val - max", "mask-calibrator", 255, 255, nothing)
cv2.createTrackbar("Delay", "mask-calibrator", 0, 1000, nothing)

while True:

    if ftype == "vid":
        ret, frame = cap.read()
        if not ret:
            break   

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    h_min = cv2.getTrackbarPos("Hue - min", "mask-calibrator")
    s_min = cv2.getTrackbarPos("Sat - min", "mask-calibrator")
    v_min = cv2.getTrackbarPos("Val - min", "mask-calibrator")
    h_max = cv2.getTrackbarPos("Hue - max", "mask-calibrator")
    s_max = cv2.getTrackbarPos("Sat - max", "mask-calibrator")
    v_max = cv2.getTrackbarPos("Val - max", "mask-calibrator")

    lower_range = np.array([h_min,s_min,v_min])
    upper_range = np.array([h_max,s_max,v_max])

    mask = cv2.inRange(hsv, lower_range, upper_range)
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    stacked = np.hstack((frame,mask))
    cv2.imshow('mask-calibrator',stacked)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

    if key == ord('s'):

        calibration = [(h_min,s_min,v_min),(h_max,s_max,v_max)]
        print(calibration)
        name = input("choose a name to save the array : ")
        if name == '':
            pass
        else:
            f=open(name,"w")
            f.write(str(calibration))
            f.close()

    delay = cv2.getTrackbarPos("Delay", "mask-calibrator")
    time.sleep(delay/1000)

if ftype == "vid":
    cap.release()
cv2.destroyAllWindows()
