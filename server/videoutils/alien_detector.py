from videoutils import centroid_area_tracker
import cv2
import config.constants_global as constants
import numpy as np

alien_template_contour = None


# https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
# https://github.com/llSourcell/Object_Detection_demo_LIVE/blob/master/demo.py
# https://pythonprogramming.net/morphological-transformation-python-opencv-tutorial/

class AlienDetector:
    def __init__(self):
        #self.counter = 0
        global alien_template_contour
        if alien_template_contour is None:
            alien_template_contour = self.__get_template_contour()
        self.alien_template_contour = alien_template_contour
        self.alien_tracker = centroid_area_tracker.CentroidAreaTracker()

    def __is_alien_contour(self, contour, image_hsv):
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
        likelihood = cv2.matchShapes(contour, self.alien_template_contour, 1, 0)
        if likelihood > 0.4:
            #print('killing by shape', ellipse)
            return (False, None, None)

        # check background
        r = cv2.boundingRect(contour)
        y_border = max(int(r[3] / 2), 15)
        x_border = max(int(r[2] / 2), 15)
        y1 = max(int(r[1]) - y_border, 0)
        y2 = min(int(r[1]) + y_border, constants.resolution[1])
        x1 = max(int(r[0]) - x_border, 0)
        x2 = min(int(r[0]) + x_border, constants.resolution[0])
        extended_rectange = image_hsv[y1:y2, x1:x2]
        contours, mask = self.__get_alien_contours(extended_rectange)
        black_img = np.zeros([y2 - y1, x2 - x1, 1], dtype=np.uint8)
        drawn_contour = cv2.drawContours(black_img, contours, -1, 255, -1)
        # cv2.imshow("drawn_contour", drawn_contour)
        kernel = np.ones((7, 7), np.uint8)
        drawn_contour_dilated = cv2.dilate(drawn_contour, kernel, iterations=1)
        #cv2.imshow("drawn_contour_dilated", drawn_contour_dilated)

        background = cv2.bitwise_and(extended_rectange, extended_rectange, mask=cv2.bitwise_not(mask))
        #cv2.imshow("background", background)
        matching_background = cv2.inRange(background, constants.background_lower_bound_hsv, constants.background_higher_bound_hsv)
        #cv2.imshow("matching_background", matching_background)
        # matching_background_plus_mask = cv2.drawContours(matching_background, contours, -1, 255, -1)
        matching_background_plus_mask = cv2.bitwise_or(matching_background, drawn_contour_dilated)
        #cv2.imshow("Crop mask", matching_background_plus_mask)
        mean = cv2.mean(matching_background_plus_mask)
        if (mean[0] < 225):
            #print('killing by background', ellipse, mean)
            return (False, None, None)

        # print('likelihood: ', likelihood, ' area:', area, ' height:', ellipse[1][1], ' ellipse ratio:', ellipseRatio, ' mean:',mean[0])
        return (True, ellipse, area)

    def detect_aliens(self, image, is_rgb):
        image_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV if is_rgb else cv2.COLOR_BGR2HSV)
        contours, _ = self.__get_alien_contours(image_hsv)
        #real_contours_num = 0
        aliens = []
        for contour in contours:
            is_alien_contour, ellipse, area = self.__is_alien_contour(contour, image_hsv)
            if not is_alien_contour:
                continue
            aliens.append(
                (ellipse[0][0],  # x
                 ellipse[0][1],  # y
                 area,
                 ellipse[1][1]))  # height
            #image = cv2.ellipse(image, ellipse, (0,125,255), 2)
            #real_contours_num = real_contours_num + 1
        #cv2.imwrite("frame"+str(self.counter)+'.png',image)
        #self.counter += 1
        #print(real_contours_num, ":", len(contours))
        return self.alien_tracker.update(aliens)

    def __get_alien_contours(self, image_hsv):
        #frame = imutils.resize(frame, width=600)
        #image_hsv = cv2.medianBlur(image_hsv, 15)
        #image_hsv = cv2.GaussianBlur(image_hsv, (11, 11), 0)
        mask = cv2.inRange(image_hsv, constants.green_lower_bound_hsv, constants.green_higher_bound_hsv)
        #mask = cv2.erode(mask, None, iterations=2)
        #mask = cv2.dilate(mask, None, iterations=2)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        _, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_TC89_L1)
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