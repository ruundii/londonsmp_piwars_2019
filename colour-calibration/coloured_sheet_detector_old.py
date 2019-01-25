import cv2
import numpy as np

resolution = (320,240)

green_sheet_lower_bound_hsv = (40,105,50)
green_sheet_higher_bound_hsv = (95,255,255)

blue_sheet_lower_bound_hsv = (96,105,50)
blue_sheet_higher_bound_hsv = (125,255,255)

red_sheet_lower_bound_hsv1 = (0,105,50)
red_sheet_higher_bound_hsv1 = (20,255,255)
red_sheet_lower_bound_hsv2 = (165,105,50)
red_sheet_higher_bound_hsv2 = (180,255,255)

yellow_sheet_lower_bound_hsv = (23,105,50)
yellow_sheet_higher_bound_hsv = (39,255,255)



def detect_coloured_sheet(image, is_rgb):
    image_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV if is_rgb else cv2.COLOR_BGR2HSV)

    (green, blue, red, yellow) = __get_coloured_masks(image_hsv)
    __detect_specific_coloured_sheet(yellow, image_hsv)

def __get_coloured_masks(image_hsv):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    green = cv2.inRange(image_hsv, green_sheet_lower_bound_hsv, green_sheet_higher_bound_hsv)
    green = cv2.morphologyEx(green, cv2.MORPH_CLOSE, kernel)
    green = cv2.morphologyEx(green, cv2.MORPH_OPEN, kernel)

    blue = cv2.inRange(image_hsv, blue_sheet_lower_bound_hsv, blue_sheet_higher_bound_hsv)
    blue = cv2.morphologyEx(blue, cv2.MORPH_CLOSE, kernel)
    blue = cv2.morphologyEx(blue, cv2.MORPH_OPEN, kernel)

    red1 = cv2.inRange(image_hsv, red_sheet_lower_bound_hsv1, red_sheet_higher_bound_hsv1)
    red2 = cv2.inRange(image_hsv, red_sheet_lower_bound_hsv2, red_sheet_higher_bound_hsv2)
    red = red1+red2
    red = cv2.morphologyEx(red, cv2.MORPH_CLOSE, kernel)
    red = cv2.morphologyEx(red, cv2.MORPH_OPEN, kernel)

    yellow = cv2.inRange(image_hsv, yellow_sheet_lower_bound_hsv, yellow_sheet_higher_bound_hsv)
    yellow = cv2.morphologyEx(yellow, cv2.MORPH_CLOSE, kernel)
    yellow = cv2.morphologyEx(yellow, cv2.MORPH_OPEN, kernel)

    return green, blue, red, yellow


def __detect_specific_coloured_sheet(coloured_mask, image_hsv):
    #cv2.imshow("Contours", coloured_mask)
    #cv2.waitKey(10)
    _, contours, _ = cv2.findContours(coloured_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if(contours is None or len(contours)==0):
        return
    black_img = np.zeros([480, 640, 1], dtype=np.uint8)

    for contour in contours:
        if(len(contour)<3): continue
        hull = cv2.convexHull(contour)
        contour_area = cv2.contourArea(contour)
        hull_area = cv2.contourArea(hull)
        if(contour_area < 2000 or hull_area < 2000):
            #too small
            continue
        ratio = contour_area / hull_area
        if(ratio < 0.9):
            #not a convex contour
            continue
        rect = cv2.minAreaRect(hull)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        im3 = cv2.drawContours(black_img, [box], -1, 255, -1)
        mean = cv2.mean(coloured_mask,mask=black_img)
        if(contour_area > 5000 and mean[0]<180) or (mean[0]<220):
            continue

        #im3 = cv2.drawContours(black_img, hull, -1, 255, -1)
        cv2.imshow("Contours", im3)
        print('area:',contour_area)
        print('hull area:',hull_area)
        print('mean:', mean)
