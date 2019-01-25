#!/usr/bin/env python
# -*- coding: utf-8 -*-

# USAGE: You need to specify a filter and "only one" image source
#
# (python) range-detector --filter RGB --image /path/to/image.png
# or
# (python) range-detector --filter HSV --webcam

import cv2
import argparse
from operator import xor
import time
from piwars import alien_detector, coloured_sheet_detector
import numpy as np

print (cv2.__version__)

def callback(value):
    pass


def normalise_colours(image, is_rgb):
    return image
    image[..., 1] = np.clip(image[..., 1] * 0.8,0, 255)
    return image
    # image_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV if is_rgb else cv2.COLOR_BGR2HSV)
    # # multiple by a factor to change the saturation
    # image_hsv[..., 1] = np.clip(image_hsv[..., 1] * 1.2,0, 255)
    #
    # # multiple by a factor of less than 1 to reduce the brightness
    # image_hsv[..., 2] = image_hsv[..., 2] * 0.8
    # return cv2.cvtColor(image_hsv, cv2.COLOR_HSV2RGB if is_rgb else cv2.COLOR_HSV2BGR)

    # (h, s, v) = cv2.split(image_hsv)
    # s = s * 5
    # s = np.clip(s, 0, 255)
    # imghsv = cv2.merge((h, s, v))
    # return cv2.cvtColor(imghsv.astype("uint8"), cv2.COLOR_HSV2RGB if is_rgb else cv2.COLOR_HSV2BGR)
    #
    # return image
    # return cv2.pow(image.astype(np.float32)/255.0, 0.8)

    clahe = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
    # image_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV if is_rgb else cv2.COLOR_BGR2HSV)
    # h, s, v = cv2.split(image_hsv)
    # out_h = h#cv2.equalizeHist(h)
    # out_s = s#cv2.equalizeHist(s)
    # out_v = v#cv2.equalizeHist(v)
    # result = cv2.merge((out_h,out_s,out_v))
    # return cv2.cvtColor(result, cv2.COLOR_HSV2RGB if is_rgb else cv2.COLOR_HSV2BGR)

    # r,g,b = cv2.split(image)
    # # r = cv2.pow(r/255.0, 0.6)
    # # g = cv2.pow(g / 255.0, 0.6)
    # # b = cv2.pow(b / 255.0, 0.6)
    #
    # # r = cv2.adaptiveThreshold(r, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
    # # g = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
    # # b = cv2.adaptiveThreshold(b, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
    #
    # out_r = r#clahe.apply(r) #cv2.equalizeHist(r)
    # out_g = g#clahe.apply(g) #cv2.equalizeHist(g)
    # out_b = b#clahe.apply(b) #cv2.equalizeHist(b)
    # out_r = cv2.equalizeHist(r)
    # out_g = cv2.equalizeHist(g)
    # out_b = cv2.equalizeHist(b)
    # return cv2.merge((out_r,out_g,out_b))


def adjust_gamma(image):
    return image
    # mean = cv2.mean(image)
    # avgIntensity = (mean[0] + mean[1] + mean[2]) / 3
    # if(avgIntensity<=150 and avgIntensity>=100):
    #     return image
    # elif(avgIntensity>150 and avgIntensity<190):
    #     gamma = 0.7
    # elif(avgIntensity>=190 and avgIntensity<220):
    #     gamma = 0.5
    # elif(avgIntensity>=220):
    #     gamma = 0.3
    # elif (avgIntensity<100 and avgIntensity>=70):
    #     gamma = 1.3
    # else:
    #     gamma = 2.0
    gamma =0.5

    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")

    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)

def setup_trackbars():
    cv2.namedWindow("Trackbars", 0)

    #green_lower_bound_hsv = (40, 100, 20)
    #green_higher_bound_hsv = (90, 255, 255)
    green_lower_bound_hsv = (165,120,70)
    green_higher_bound_hsv = (13,255,255)

    cv2.createTrackbar("H_MIN", "Trackbars", green_lower_bound_hsv[0], 255, callback)
    cv2.createTrackbar("H_MAX", "Trackbars", green_higher_bound_hsv[0], 255, callback)
    cv2.createTrackbar("S_MIN", "Trackbars", green_lower_bound_hsv[1], 255, callback)
    cv2.createTrackbar("S_MAX", "Trackbars", green_higher_bound_hsv[1], 255, callback)
    cv2.createTrackbar("V_MIN", "Trackbars", green_lower_bound_hsv[2], 255, callback)
    cv2.createTrackbar("V_MAX", "Trackbars", green_higher_bound_hsv[2], 255, callback)

def get_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('-a', '--aliens', required=False,
                    help='Use aliens', action='store_true')
    ap.add_argument('-i', '--image', required=False,
                    help='Path to the image')
    ap.add_argument('-w', '--webcam', required=False,
                    help='Use webcam', action='store_true')
    ap.add_argument('-p', '--preview', required=False,
                    help='Show a preview of the image after applying the mask',
                    action='store_true')
    args = vars(ap.parse_args())

    if not(bool(args['aliens'])) and not xor(bool(args['image']), bool(args['webcam'])):
        ap.error("Please specify only one image source")

    return args


def get_trackbar_values():
    values = []
    values.append(cv2.getTrackbarPos("H_MIN", "Trackbars"))
    values.append(cv2.getTrackbarPos("S_MIN", "Trackbars"))
    values.append(cv2.getTrackbarPos("V_MIN", "Trackbars"))
    values.append(cv2.getTrackbarPos("H_MAX", "Trackbars"))
    values.append(cv2.getTrackbarPos("S_MAX", "Trackbars"))
    values.append(cv2.getTrackbarPos("V_MAX", "Trackbars"))
    return values


def main():
    args = get_arguments()

    if args['image']:
        image = cv2.imread(args['image'])

        frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    else:
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        #camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, False)
        #camera.set(cv2.CAP_PROP_EXPOSURE, -4)
        #camera.set(cv2.CAP_PROP_GAMMA, -2)
        #camera.set(cv2.CAP_PROP_GAIN  ,-3)
        #camera.set(cv2.CAP_PROP_TEMPERATURE, 3000)
        #camera.set(44, False)
        #camera.set(44, False)

    setup_trackbars()
    count = 0
    while True:
        image=None
        isBgr = True
        if args['webcam']:
            ret, image = camera.read()
            print(len(image))
            print(len(image[0]))
            coloured_sheet_detector.detect_coloured_sheet(image, False)
            #image = adjust_gamma(image)
            #image = normalise_colours(image, False)
            #alien_detector.detect_aliens(image, True)

            if not ret:
                break
        elif args['aliens']:

            res = cv2.waitKey(20) & 0xFF
            if res == 32:
                print(count)
                count = (count + 1) % 17
            #image = cv2.imread("alienpi\\alien_template.png")
            #image = cv2.imread("alienpi\\frame"+str(count)+".jpg")
            image = cv2.imread("alienpi\\frame18.jpg")
            image = normalise_colours(image, True)
            isBgr = False
            alien_detector.detect_aliens(image, True)
            time.sleep(0.1)

        #image = adjust_gamma(image)
        if isBgr:
            frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        else:
            frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

        h_min, s_min, v_min, h_max, s_max, v_max = get_trackbar_values()

        if(h_min>h_max):
            #hue
            frame_to_thresh = cv2.medianBlur(frame_to_thresh, 25)

            thresh1 = cv2.inRange(frame_to_thresh, (0, 25, 120), (10, 255, 255))
            thresh2 = cv2.inRange(frame_to_thresh, (134, 25, 120), (190, 255, 255))
            thresh = thresh1+thresh2
        else:
            thresh = cv2.inRange(frame_to_thresh, (h_min, s_min, v_min), (h_max, s_max, v_max))

        if args['preview']:
            preview = cv2.bitwise_and(image, image, mask=thresh)
            cv2.imshow("Preview", preview)
            cv2.imshow("Original", image)
        else:
            cv2.imshow("Original", image)
            cv2.imshow("Thresh", thresh)

        if cv2.waitKey(1) & 0xFF is ord('q'):
            break


if __name__ == '__main__':
    main()