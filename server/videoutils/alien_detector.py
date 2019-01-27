from videoutils import centroid_area_tracker
import cv2
import config.constants_global as constants
import numpy as np
import time
alien_template_contour = None
import json


# https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
# https://github.com/llSourcell/Object_Detection_demo_LIVE/blob/master/demo.py
# https://pythonprogramming.net/morphological-transformation-python-opencv-tutorial/

class AlienDetector:
    def __init__(self, console_mode):
        self.counter = 0
        self.console_mode = console_mode
        self.resolution = (100,100)
        self.fov = None
        global alien_template_contour
        with open(constants.colour_config_name) as json_config_file:
            config = json.load(json_config_file)
        self.colour_config = config["alien_hsv_ranges"]
        if alien_template_contour is None:
            alien_template_contour = self.__get_template_contour()
        self.alien_template_contour = alien_template_contour
        self.alien_tracker = centroid_area_tracker.CentroidAreaTracker()
        print("AlienDetector initialised")

    def set_image_params(self, actual_resolution, fov):
        self.resolution = actual_resolution
        self.fov = fov

    def __is_alien_contour(self, contour, image_hsv, green_mask):
        try:
            ellipse = cv2.fitEllipse(contour)
        except:
            #print('killing by ellipse constr')
            return (False, None, None)
        ellipseRatio = ellipse[1][1] / ellipse[1][0]

        # check ellipse radius ratio and hieght
        if ellipseRatio < 1.1 or ellipseRatio > 3 or ellipse[1][1] < 3:
            #print('killing by ellipse', ellipse)
            return (False, None, None)

        # check area
        area = cv2.contourArea(contour)
        if area < 15:
            #print('killing by area', ellipse)
            return (False, None, None)

        # compare shapes
        difference_factor = cv2.matchShapes(contour, self.alien_template_contour, 1, 0)
        if difference_factor > 0.4:
            #print('killing by shape', ellipse)
            return (False, None, None)

        # check background
        r = cv2.boundingRect(contour)
        y_border = max(int(r[3] / 2), 15)
        x_border = max(int(r[2] / 2), 15)
        y1 = max(int(r[1]) - y_border, 0)
        y2 = min(int(r[1]+r[3]) + y_border, self.resolution[1])
        x1 = max(int(r[0]) - x_border, 0)
        x2 = min(int(r[0]+r[2]) + x_border, self.resolution[0])
        extended_rectange = image_hsv.get()[y1:y2, x1:x2].copy()
        extended_rectange_mask = green_mask.get()[y1:y2, x1:x2]
        _, contours, _ = cv2.findContours(extended_rectange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
        black_img = np.zeros([y2 - y1, x2 - x1, 1], dtype=np.uint8)
        drawn_contour = cv2.drawContours(black_img, contours, -1, 255, -1)
        # cv2.imshow("drawn_contour", drawn_contour)
        kernel = np.ones((7, 7), np.uint8)
        drawn_contour_dilated = cv2.dilate(drawn_contour, kernel, iterations=1)
        #cv2.imshow("drawn_contour_dilated", drawn_contour_dilated)

        background = cv2.bitwise_and(extended_rectange, extended_rectange, mask=cv2.bitwise_not(extended_rectange_mask))
        #cv2.imshow("background", background)
        matching_background = cv2.inRange(background, tuple(self.colour_config["background_min"]), tuple(self.colour_config["background_max"]))
        #cv2.imshow("matching_background", matching_background)
        # matching_background_plus_mask = cv2.drawContours(matching_background, contours, -1, 255, -1)
        matching_background_plus_mask = cv2.bitwise_or(matching_background, drawn_contour_dilated)
        #cv2.imshow("Crop mask", matching_background_plus_mask)
        mean = cv2.mean(matching_background_plus_mask)
        if (mean[0] < 230):
            #print('killing by background', ellipse, mean)
            return (False, None, None)

        # print('likelihood: ', likelihood, ' area:', area, ' height:', ellipse[1][1], ' ellipse ratio:', ellipseRatio, ' mean:',mean[0])
        return (True, ellipse, area)

    def detect_aliens(self, image, image_hsv):
        t = time.time()
        contours, mask = self.__get_alien_contours(image_hsv)
        if constants.performance_tracing_alien_detector_details: print('alien_detector.detect_aliens.__get_alien_contours:',time.time()-t)
        if not self.console_mode and constants.image_processing_tracing_show_colour_mask:
            cv2.imshow("ColourMask", mask)
            cv2.waitKey(1)
        if not self.console_mode and constants.image_processing_tracing_show_background_colour_mask:
            back_mask = cv2.inRange(image_hsv, tuple(self.colour_config["background_min"]), tuple(self.colour_config["background_max"]))
            cv2.imshow("BackColourMask", back_mask)
            cv2.waitKey(1)

        real_contours_num = 0
        aliens = []
        for contour in contours:
            is_alien_contour, ellipse, area = self.__is_alien_contour(contour, image_hsv, mask)
            if not is_alien_contour:
                continue
            w = self.resolution[0]
            h = self.resolution[1]
            alien_height = ellipse[1][1]
            distance = constants.alien_image_height_mm / alien_height * constants.alien_distance_multiplier + constants.alien_distance_offset
            x = min(max(ellipse[0][0], 0), w)
            y = min(max(ellipse[0][1], 0), h)
            x_angle = ((x - w / 2.0) / w) * self.fov[0]
            y_angle = ((h / 2.0 - y) / h) * self.fov[1]
            aliens.append((x, y, area, distance, x_angle, y_angle))
            if constants.image_processing_tracing_show_detected_objects:
                image = cv2.ellipse(image, ellipse, (0,125,255), 2)
            real_contours_num = real_contours_num + 1
        if not self.console_mode and constants.image_processing_tracing_show_detected_objects:
            cv2.imshow("DetectedObject", image)
            cv2.waitKey(1)
        self.counter += 1
        #print(real_contours_num, ":", len(contours))
        return self.alien_tracker.update(aliens)

    def __get_alien_contours(self, image_hsv):
        #frame = imutils.resize(frame, width=600)
        #image_hsv = cv2.medianBlur(image_hsv, 15)
        #image_hsv = cv2.GaussianBlur(image_hsv, (11, 11), 0)
        t = time.time()
        mask = cv2.inRange(image_hsv, tuple(self.colour_config["green_min"]), tuple(self.colour_config["green_max"]))
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

        _, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
        if constants.performance_tracing_alien_detector_details and self.resolution[0]>400:
            print('alien_detector.__get_alien_contours.find_contours:', time.time() - t)
            t=time.time()

        #im3 = cv2.drawContours(image_hsv, contours, -1, 255, -1)
        #cv2.imshow("Contours", im3)
        #preview = cv2.bitwise_and(image_hsv, image_hsv, mask=mask)
        #cv2.imshow("Preview", preview)
        return contours, mask

    def __get_template_contour(self):
        alien_template = cv2.imread(constants.alien_template)
        alien_template_hsv = cv2.cvtColor(alien_template, cv2.COLOR_RGB2HSV)
        alien_template_contours, _ = self.__get_alien_contours(alien_template_hsv)
        return alien_template_contours[0]
