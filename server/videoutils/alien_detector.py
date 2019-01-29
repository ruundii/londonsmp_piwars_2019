from videoutils import centroid_area_tracker
import cv2
import config.constants_global as constants
import numpy as np
import time
alien_template_contour = None
import json
import videoutils.image_display as display
from videoutils.util import get_in_range_mask



# https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
# https://github.com/llSourcell/Object_Detection_demo_LIVE/blob/master/demo.py
# https://pythonprogramming.net/morphological-transformation-python-opencv-tutorial/

class AlienDetector:
    def __init__(self):
        self.counter = 0
        self.resolution = (100,100)
        self.fov = None
        self.kernel = np.ones((7, 7), np.uint8)
        with open(constants.colour_config_name) as json_config_file:
            config = json.load(json_config_file)
        self.colour_config = config["alien_hsv_ranges"]
        self.alien_tracker = centroid_area_tracker.CentroidAreaTracker()
        print("AlienDetector initialised")

    def set_image_params(self, actual_resolution, fov):
        self.resolution = actual_resolution
        self.fov = fov

    def __is_alien_contour(self, contour, image_hsv, green_mask):
        x, y, w, h = cv2.boundingRect(contour)
        sideRatio = h / w

        # check ellipse radius ratio and height
        if sideRatio < 1.1 or sideRatio > 3 or h < 3:
            #print('killing by weird rect', ellipse)
            return (False, None, None, None, None, None)

        # check area
        if w*h < 50:
            #print('killing by area', ellipse)
            return (False, None, None, None, None, None)

        # check background
        y_border = max(int(h / 2), 15)
        x_border = max(int(w / 2), 15)
        y1 = max(int(y) - y_border, 0)
        y2 = min(int(y+h) + y_border, self.resolution[1])
        x1 = max(int(x) - x_border, 0)
        x2 = min(int(x+w) + x_border, self.resolution[0])
        extended_rectange = image_hsv.get()[y1:y2, x1:x2].copy()
        #extended_rectange_mask = green_mask.get()[y1:y2, x1:x2]
        t = time.time()
        #_, contours, _ = cv2.findContours(extended_rectange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
        # contour -= [x1,y1]
        # if (constants.performance_tracing_alien_detector_details):
        #     print('alien_detector.detect_aliens.__is_alien_contour.cv2.findContours:', time.time() - t)
        # black_img = np.zeros([y2 - y1, x2 - x1, 1], dtype=np.uint8)
        # #drawn_contour = cv2.drawContours(black_img, contour, -1, 255, thickness=-1)
        # drawn_contour = cv2.fillPoly(black_img, contour, 255)
        # display.image_display.add_image_to_queue("drawn_contour", drawn_contour)
        # drawn_contour_dilated = cv2.dilate(drawn_contour, self.kernel, iterations=1)
        # display.image_display.add_image_to_queue("drawn_contour_dilated", drawn_contour_dilated)

        #background = cv2.bitwise_and(extended_rectange, extended_rectange, mask=cv2.bitwise_not(extended_rectange_mask))
        #display.image_display.add_image_to_queue("background", background)
        matching_background  = get_in_range_mask(extended_rectange,tuple(self.colour_config["background_min"]), tuple(self.colour_config["background_max"]))
        #display.image_display.add_image_to_queue("matching_background", matching_background)
        #matching_background_plus_mask = cv2.drawContours(matching_background, contours, -1, 255, -1)
        #matching_background_plus_mask = cv2.bitwise_or(matching_background, drawn_contour_dilated)
        #display.image_display.add_image_to_queue("Crop mask", matching_background_plus_mask)
        mean = cv2.mean(matching_background)[0]+255*cv2.contourArea(contour)/((x2-x1)*(y2-y1))
        if (mean < 220):
            #print('killing by background', ellipse, mean)
            return (False, None, None, None, None, None)

        # print('likelihood: ', likelihood, ' area:', area, ' height:', ellipse[1][1], ' ellipse ratio:', ellipseRatio, ' mean:',mean[0])
        return (True, x, y, w, h, w*h)

    def detect_aliens(self, image, image_hsv):
        t = time.time()
        contours, mask = self.__get_alien_contours(image_hsv)
        if constants.performance_tracing_alien_detector_details: print('alien_detector.detect_aliens.__get_alien_contours:',time.time()-t)
        if constants.image_processing_tracing_show_colour_mask:
            display.image_display.add_image_to_queue("ColourMask", mask)
        if constants.image_processing_tracing_show_background_colour_mask:
            back_mask = get_in_range_mask(image_hsv, tuple(self.colour_config["background_min"]), tuple(self.colour_config["background_max"]))
            display.image_display.add_image_to_queue("BackColourMask", back_mask)

        real_contours_num = 0
        aliens = []
        for contour in contours:
            is_alien_contour, alien_x, alien_y, alien_w, alien_h, alien_area = self.__is_alien_contour(contour, image_hsv, mask)
            if not is_alien_contour:
                continue
            w = self.resolution[0]
            h = self.resolution[1]
            distance = constants.alien_image_height_mm / alien_h * constants.alien_distance_multiplier + constants.alien_distance_offset
            x = min(max(alien_x, 0), w)
            y = min(max(alien_y, 0), h)
            x_angle = ((x - w / 2.0) / w) * self.fov[0]
            y_angle = ((h / 2.0 - y) / h) * self.fov[1]
            aliens.append((x, y, alien_area, distance, x_angle, y_angle))
            if constants.image_processing_tracing_show_detected_objects:
                image = cv2.rectangle(image, (alien_x, alien_y),(alien_x+alien_w, alien_y+alien_h), (0,125,255), 2)
            real_contours_num = real_contours_num + 1
        if constants.image_processing_tracing_show_detected_objects:
            display.image_display.add_image_to_queue("DetectedObject", image)
        self.counter += 1
        #print(real_contours_num, ":", len(contours))
        return self.alien_tracker.update(aliens)

    def __get_alien_contours(self, image_hsv):
        #frame = imutils.resize(frame, width=600)
        #image_hsv = cv2.medianBlur(image_hsv, 15)
        #image_hsv = cv2.GaussianBlur(image_hsv, (11, 11), 0)
        t = time.time()
        mask = get_in_range_mask(image_hsv, tuple(self.colour_config["green_min"]), tuple(self.colour_config["green_max"]))
        if constants.performance_tracing_alien_detector_details and self.resolution[0]>400:
            print('alien_detector.__get_alien_contours.apply_green_mask:', time.time() - t)
            t=time.time()

        #mask = cv2.erode(mask, None, iterations=2)
        #mask = cv2.dilate(mask, None, iterations=2)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        if constants.performance_tracing_alien_detector_details and self.resolution[0]>400:
            print('alien_detector.__get_alien_contours.morphology:', time.time() - t)
            t=time.time()

        _, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if constants.performance_tracing_alien_detector_details and self.resolution[0]>400:
            print('alien_detector.__get_alien_contours.find_contours:', time.time() - t)
            t=time.time()

        #im3 = cv2.drawContours(image_hsv, contours, -1, 255, -1)
        #cv2.imshow("Contours", im3)
        #preview = cv2.bitwise_and(image_hsv, image_hsv, mask=mask)
        #cv2.imshow("Preview", preview)
        return contours, mask

