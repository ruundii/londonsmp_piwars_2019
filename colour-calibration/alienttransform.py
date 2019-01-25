green_lower_bound_hsv = (40,150,150)
green_higher_bound_hsv = (85,255,255)


import cv2
image = cv2.imread("alienpi\\Alien.png")
frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
thresh = cv2.inRange(frame_to_thresh, green_lower_bound_hsv, green_higher_bound_hsv)
preview = cv2.bitwise_and(image, image, mask=thresh)
cv2.imshow("Preview", preview)
cv2.imwrite("alien_template.png", preview)
while True:
    if cv2.waitKey(1) & 0xFF is ord('q'):
        break
