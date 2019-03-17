from videoutils import centroid_area_tracker
import cv2
import config.constants_global as constants
import math
import time
import json
import videoutils.image_display as display
from videoutils.util import get_in_range_mask

min_background_pixels_in_high_area_col = 10
min_background_pixels_in_zoom_area_col = 140
min_background_pixels_in_high_area_row = 30
column_stride = 40
background_high_area_pixels_number = int(0.8*column_stride)
min_alien_pixels_vertical = 6
min_alien_pixels_horizontal = 4


# https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
# https://github.com/llSourcell/Object_Detection_demo_LIVE/blob/master/demo.py
# https://pythonprogramming.net/morphological-transformation-python-opencv-tutorial/

class AlienDetector:
    def __init__(self):
        self.resolution = (100,100)
        self.fov = None
        with open(constants.colour_config_name) as json_config_file:
            config = json.load(json_config_file)
        self.colour_config = config["alien_hsv_ranges"]
        self.alien_tracker = centroid_area_tracker.CentroidAreaTracker()
        print("AlienDetector initialised")

    def set_image_params(self, actual_resolution, fov):
        self.resolution = actual_resolution
        self.fov = fov

    def detect_aliens(self, image, image_hsv):
        t = time.time()
        background_mask = get_in_range_mask(image_hsv, tuple(self.colour_config["background_min"]),
                                            tuple(self.colour_config["background_max"]))
        ff = background_mask.get().copy()
        cv2.floodFill(ff, None, (0, 0), 255)
        cv2.floodFill(ff, None, (0, self.resolution[1]-1), 255)
        cv2.floodFill(ff, None, (int(self.resolution[0]/2.0), 0), 255)
        cv2.floodFill(ff, None, (int(self.resolution[0]/2.0), self.resolution[1]-1), 255)
        cv2.floodFill(ff, None, (self.resolution[0]-1, 0), 255)
        cv2.floodFill(ff, None, (self.resolution[0]-1, self.resolution[1]-1), 255)

        green_mask_original = get_in_range_mask(image_hsv, tuple(self.colour_config["green_min"]), tuple(self.colour_config["green_max"]))

        green_mask = cv2.bitwise_and(green_mask_original, green_mask_original, mask=cv2.bitwise_not(ff))

        if constants.performance_tracing_alien_detector_details: print('alien_detector.detect_aliens.ff:',time.time()-t)
        aliens_list = []

        green_mask_col_aggr = cv2.reduce(green_mask, 0, cv2.REDUCE_SUM, dtype=cv2.CV_32S).get()[0, :] / 255
        alien_found = False
        alien_start_index = None
        for i in range(len(green_mask_col_aggr)):
            if not alien_found and green_mask_col_aggr[i]>=min_alien_pixels_vertical:
                alien_found = True
                alien_start_index = i
                alien_end_index = i
                prev_index = i - 1
                while prev_index>=0:
                    if green_mask_col_aggr[prev_index]>=2:
                        alien_start_index = prev_index
                        prev_index -= 1
                    else:
                        break
            if alien_found:
                if green_mask_col_aggr[i]>=2:
                    alien_end_index = i
                    if i == len(green_mask_col_aggr)-1:
                        alien_found = False
                else:
                    alien_found = False
                if not alien_found and alien_end_index>=(alien_start_index+min_alien_pixels_horizontal):
                    aliens_list.append((alien_start_index, alien_end_index))

        aliens = []
        if constants.image_processing_tracing_show_detected_objects or constants.image_processing_tracing_record_video:
            detected_image = image.get().copy()
        else:
            detected_image = None
        for (start,end) in aliens_list:
            w = end-start
            if constants.image_processing_tracing_show_detected_objects or constants.image_processing_tracing_record_video:
                cv2.rectangle(detected_image, (start, 0),(end, self.resolution[1]-1), (0,125,255), 2)
            distance = constants.alien_image_width_mm / w * constants.alien_distance_multiplier + constants.alien_distance_offset
            x_angle = (((start+end-self.resolution[0]) / 2.0) / self.resolution[0]) * self.fov[0]
            aliens.append((start, end, w, distance, x_angle))

        if constants.performance_tracing_alien_detector_details: print('alien_detector.detect_aliens.inside:',time.time()-t)
        if constants.image_processing_tracing_show_colour_mask:
            display.image_display.add_image_to_queue("ColourMask", green_mask_original)
            display.image_display.add_image_to_queue("ColourMask_FF", green_mask)
        if constants.image_processing_tracing_show_background_colour_mask:
            display.image_display.add_image_to_queue("BackColourMask", background_mask)
            display.image_display.add_image_to_queue("BackColourMask_FF", ff)

        display.image_display.add_image_to_queue("detected", detected_image) if constants.image_processing_tracing_show_detected_objects else None

        return self.alien_tracker.update(aliens), detected_image
