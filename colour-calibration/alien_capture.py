import time
import cv2
import io
import numpy as np

count = 27
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4,480)
green_lower_bound_hsv = (35,60,50)
green_higher_bound_hsv = (80,255,255)

while True:
    ret, frame = cap.read()
    # camera.framerate = 32

    time.sleep(0.3)
    frame_to_thresh = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    thresh = cv2.inRange(frame_to_thresh, green_lower_bound_hsv, green_higher_bound_hsv)
    preview = cv2.bitwise_and(frame, frame, mask=thresh)
    cv2.imshow("Original", frame)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Preview", preview)


    # Display the resulting frame64
    res = cv2.waitKey(20) & 0xFF
    if res == ord('q'):
        break
    elif res == 32:
        cv2.imwrite("frame%d.jpg" % count, frame)  # save frame as JPEG file
        count += 1



