from videoutils import centroid_area_tracker
import cv2
import config.constants_global as constants
import math
import time
import json
import videoutils.image_display as display
from videoutils.util import get_in_range_mask

min_background_pixels_in_high_area_col = 10
min_background_pixels_in_zoom_area_col = 160
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

    def __find_roi(self, image_hsv):
        t = time.time()
        background_mask = get_in_range_mask(image_hsv, tuple(self.colour_config["background_min"]), tuple(self.colour_config["background_max"]))
        t = time.time()
        background_mask_col_aggr = cv2.reduce(background_mask, 0, cv2.REDUCE_SUM, dtype=cv2.CV_32S).get()[0, :]/255
        background_start_col_index = -1
        background_end_col_index = -1
        is_picture_zoomed_on_a_wall = max(background_mask_col_aggr)>min_background_pixels_in_zoom_area_col
        if is_picture_zoomed_on_a_wall:
            #picture is zoomed on wall, don't cut from the sides
            background_start_col_index=0
            background_end_col_index = len(background_mask_col_aggr)-1
        else:
            for i in range(len(background_mask_col_aggr)):
                if background_mask_col_aggr[i] > min_background_pixels_in_high_area_col:
                    background_start_col_index = i
                    break
            for i in range(len(background_mask_col_aggr)):
                if background_mask_col_aggr[len(background_mask_col_aggr)-i-1] > min_background_pixels_in_high_area_col:
                    background_end_col_index = len(background_mask_col_aggr)-i-1
                    break
            if background_start_col_index < 0 or background_end_col_index <0:
                return None, None, 0, 0, 0, 0, 0  # return_no_alien
        background_mask_row_aggr = cv2.reduce(background_mask, 1, cv2.REDUCE_SUM, dtype=cv2.CV_32S).get()[:, 0]/255

        background_start_row_index = -1
        background_end_row_index = -1
        for i in range(len(background_mask_row_aggr)):
            if background_mask_row_aggr[i] > min_background_pixels_in_high_area_row:
                background_start_row_index = i
                break
        for i in range(len(background_mask_row_aggr)):
            if background_mask_row_aggr[len(background_mask_row_aggr)-i-1] > min_background_pixels_in_high_area_row:
                background_end_row_index = len(background_mask_row_aggr)-i-1
                break
        if background_start_row_index < 0 or background_end_row_index <0:
            return None, None, 0, 0, 0, 0, 0 #return_no_alien
        t = time.time()
        #cut the roi
        image_hsv_cut = cv2.UMat(image_hsv, (background_start_row_index, background_end_row_index), (background_start_col_index, background_end_col_index)).get()
        t = time.time()

        #fill surroundings of the red area
        if not is_picture_zoomed_on_a_wall:
            background_mask_cut = cv2.UMat(background_mask, (background_start_row_index, background_end_row_index),
                                     (background_start_col_index, background_end_col_index))
            w = background_end_col_index-background_start_col_index
            for stride_index in range(math.ceil(w/float(column_stride))):
                if((stride_index+1)*column_stride>w):
                    if w > column_stride:
                        stride_start_index = w-column_stride
                        stride_end_index = w
                    else:
                        stride_start_index = 0
                        stride_end_index = w
                else:
                    stride_start_index = stride_index*column_stride
                    stride_end_index = (stride_index+1)*column_stride
                stride_window = cv2.UMat(background_mask, (background_start_row_index, background_end_row_index),
                                               (background_start_col_index+stride_start_index, background_start_col_index+stride_end_index))
                t = time.time()
                stride_background_row_aggr = cv2.reduce(stride_window, 1, cv2.REDUCE_SUM, dtype=cv2.CV_32S).get()[:,0] / 255
                for stride_row_index in range(len(stride_background_row_aggr)):
                    if stride_background_row_aggr[stride_row_index] > background_high_area_pixels_number:
                        #make all above black
                        t = time.time()
                        image_hsv_cut[0:stride_row_index,stride_start_index:stride_end_index]=0
                        break
                for stride_row_index in range(len(stride_background_row_aggr)):
                    if stride_background_row_aggr[
                        len(stride_background_row_aggr) - stride_row_index - 1] > background_high_area_pixels_number:
                        #make all below black
                        t = time.time()
                        image_hsv_cut[len(stride_background_row_aggr) - stride_row_index - 1:len(stride_background_row_aggr)-1,stride_start_index:stride_end_index]=0
                        break
                #display.image_display.add_image_to_queue("stride"+str(stride_index), stride_window)

        return cv2.UMat(image_hsv_cut), background_mask, len(background_mask_row_aggr), background_start_row_index,background_end_row_index,background_start_col_index,background_end_col_index



    def detect_aliens(self, image, image_hsv):
        t = time.time()
        try:
            image_hsv, background_mask, h, row_start, row_end, col_start, col_end = self.__find_roi(image_hsv)
        except Exception as e:
            print("alient_detector 2", e)
        if constants.performance_tracing_alien_detector_details: print('alien_detector.detect_aliens.roi:',time.time()-t)
        aliens_list = []
        if image_hsv is not None:
            green_mask = cv2.UMat(get_in_range_mask(image_hsv, tuple(self.colour_config["green_min"]),tuple(self.colour_config["green_max"])))
            try:
                green_mask_col_aggr = cv2.reduce(green_mask, 0, cv2.REDUCE_SUM, dtype=cv2.CV_32S).get()[0, :] / 255
            except Exception as e:
                print("alient_detector 1", e)
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
                    if not alien_found and alien_end_index>=alien_start_index-min_alien_pixels_horizontal:
                        aliens_list.append((alien_start_index, alien_end_index))

        aliens = []
        if constants.image_processing_tracing_show_detected_objects or constants.image_processing_tracing_record_video:
            detected_image = image.get().copy()
        else:
            detected_image = None
        for (start,end) in aliens_list:
            w = end-start
            if constants.image_processing_tracing_show_detected_objects or constants.image_processing_tracing_record_video:
                cv2.rectangle(detected_image, (col_start+start, 0),(col_start+end, h), (0,125,255), 2)
            distance = constants.alien_image_width_mm / w * constants.alien_distance_multiplier + constants.alien_distance_offset
            x_angle = (((start+end-self.resolution[0]) / 2.0) / self.resolution[0]) * self.fov[0]
            aliens.append((start, end, w, distance, x_angle))

        if constants.performance_tracing_alien_detector_details: print('alien_detector.detect_aliens.inside:',time.time()-t)
        if constants.image_processing_tracing_show_colour_mask:
            display.image_display.add_image_to_queue("ColourMask", green_mask)
        if constants.image_processing_tracing_show_background_colour_mask:
            display.image_display.add_image_to_queue("BackColourMask", background_mask)

        display.image_display.add_image_to_queue("detected", detected_image) if constants.image_processing_tracing_show_detected_objects else None

        return self.alien_tracker.update(aliens), detected_image

