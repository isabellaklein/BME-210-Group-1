#!/usr/bin/python3
# To make this work:
# sudo apt install -y python3-picamera2

import cv2
from picamera2 import Picamera2
from grip import WhiteBall

from pynput.keyboard import Listener
import meArm
import time

arm = meArm.meArm() # takes inserted data from meArm.py aka calibration data
arm.begin(0,0x6f)

cv2.startWindowThread()

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

process = WhiteBall()


font = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 0.25
color = (0, 255, 0)
thickness = 1

# Main Loop
stop = False

while (not stop):
    global x, y
    img = picam2.capture_array()
    display_img = cv2.resize(img, ((int)(320), (int)(240)), 0, 0)
    
    process.process(img)

    if len(process.ball) > 0:
        x = process.ball[1] + process.startX
        y = process.ball[2] + process.startY
        hsv = cv2.cvtColor(display_img, cv2.COLOR_BGR2HSV)
        cv2.drawMarker(display_img, (x, y),  (0, 0, 255), cv2.MARKER_CROSS, 10, 1)
        txt = "{},{},{}".format(hsv[y,x,0], hsv[y,x,1], hsv[y,x,2])
        cv2.putText(display_img, txt, (x,y), font, fontScale, color, thickness, cv2.LINE_AA)
        
    if len(process.filter_contours_output) > 0:
        # fix the offset of the region of interest
        x_offset, y_offset = process.startX, process.startY
        for contour in process.filter_contours_output:
            # contour with new offset is created
            contour += (x_offset, y_offset)
        cv2.drawContours(display_img, process.filter_contours_output, -1, (0,255,0), 1)

    x1=process.startX
    y1=process.startY
    x2=process.endX
    y2=process.endY
    cv2.rectangle(display_img, (x1, y1), (x2, y2), (255,0,0), 2)
    cv2.imshow("Camera", display_img)
    try:
        if (cv2.waitKey(1) & 0xFF == ord('q')) or (cv2.getWindowProperty("Camera", 0) < 0): stop = True
    except: stop = True
    #based on the x values the code finds, the code finds one of four squares that the arm should move to to defend
    if (x < 78):
        xf = -44
    elif (x < 155):
        xf = -16
    elif (x < 233):
        xf = 16
    else:
        xf = 44
    #after being sorted into one of 4 positions, the arm moves there immediately
    arm.goDirectlyTo(xf,165,-10)

cv2.destroyAllWindows()
