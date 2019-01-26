import cv2
import numpy as np
import json
import config.constants_global as constants


min_number_of_coloured_pixels_per_peak_column = 20
max_number_of_coloured_sheets_per_image = 2
high_colour_zone_threshold_factor_of_peak = 0.7
min_width_for_high_zone = 10
min_height_for_high_zone = 7

class ColouredSheetDetector:
    def __init__(self, console_mode):
        with open(constants.colour_config_name) as json_config_file:
            config = json.load(json_config_file)
        self.colour_config = config["colour_sheets_hsv_ranges"]
        self.console_mode = console_mode


    def detect_coloured_sheets(self, image, image_hsv, fov):
        colour_sets = []
        for colour in ["green", "blue", "red", "yellow"]:
            mask_column_aggr, mask = self.__get_colored_mask_sums(image_hsv, colour, self.colour_config[colour + "_min"], self.colour_config[colour + "_max"])
            sum = np.sum(mask_column_aggr)
            colour_sets.append((colour, sum, mask_column_aggr, mask))
        colour_sets.sort(key=lambda tup: tup[1], reverse=True)

        found_sheets = []
        for colour_index in range(max_number_of_coloured_sheets_per_image):
            colour, sum, mask_column_aggr, mask = colour_sets[colour_index]
            peak = np.max(mask_column_aggr)

            high_zone_column_start_index = self.__get_high_zone_start_index(mask_column_aggr, min_width_for_high_zone, peak=peak)
            if high_zone_column_start_index is None:
                continue
            high_zone_column_end_index = self.__get_high_zone_start_index(mask_column_aggr, min_width_for_high_zone, peak=peak, is_reverse=True)
            if high_zone_column_end_index is None:
                continue

            h = len(image_hsv)
            w = len(image_hsv[0])

            mask_high_zone_row_arrg = cv2.reduce(mask[0:h, high_zone_column_start_index:high_zone_column_end_index], 1, cv2.REDUCE_SUM, dtype=cv2.CV_32S)[:,0]
            peak = np.max(mask_high_zone_row_arrg)

            high_zone_row_start_index = self.__get_high_zone_start_index(mask_high_zone_row_arrg, min_height_for_high_zone, peak=peak)
            if high_zone_row_start_index is None:
                continue
            high_zone_row_end_index = self.__get_high_zone_start_index(mask_high_zone_row_arrg, min_height_for_high_zone, peak=peak, is_reverse=True)
            if high_zone_row_end_index is None:
                continue

            mid_column_index = int((high_zone_column_start_index + high_zone_column_end_index) / 2)
            pixel_height = high_zone_row_end_index - high_zone_row_start_index
            distance = constants.coloured_sheet_height_mm / pixel_height * constants.coloured_sheet_distance_multiplier + constants.coloured_sheet_distance_offset
            x_angle = int((mid_column_index - int(len(image_hsv[0]) / 2)) * fov[0] / len(image_hsv[0]))
            #print('top', colour_index + 1, 'colour:', colour, 'columns:', high_zone_start_index, ':', high_zone_end_index,'x angle:',x_angle)
            if(not self.console_mode and constants.image_processing_tracing_show_detected_objects):
                cv2.rectangle(image,(high_zone_column_start_index, high_zone_row_start_index),
                              (high_zone_column_end_index, high_zone_row_end_index), (0,255,0))
                cv2.imshow("DetectedObject_"+colour, image)
                cv2.waitKey(1)
            found_sheets.append((colour, distance, x_angle))
        return found_sheets

    def __get_high_zone_start_index(self, aggrerates, min_size_for_high_zone, peak = None, is_reverse=False):
        if(peak is None):
            peak = np.max(aggrerates)
        if peak < min_number_of_coloured_pixels_per_peak_column:
            # not enough coloured points even in top column
            return None

        high_zone_threshold = high_colour_zone_threshold_factor_of_peak * peak

        high_zone_start_index = None
        for i in range(len(aggrerates)):
            current_index = len(aggrerates)-i-1 if is_reverse else i
            if  high_zone_start_index is not None:
                if ((not is_reverse and high_zone_start_index + min_size_for_high_zone < current_index) or
                    (is_reverse and high_zone_start_index - min_size_for_high_zone > current_index)):
                    # we have certainly found high zone for the colour
                    return high_zone_start_index
            if aggrerates[current_index] >= high_zone_threshold:
                if high_zone_start_index is None:
                    if ((not is_reverse and current_index + min_size_for_high_zone <= len(aggrerates)) or
                        (is_reverse and current_index - min_size_for_high_zone >= 0)):
                        high_zone_start_index = current_index
                        continue
            else:
                if high_zone_start_index is not None:
                    # high zone did not sustain for a required number of columns - resetting
                    high_zone_start_index = None

        return high_zone_start_index

    def __get_colored_mask_sums(self, image_hsv, colour, hsv_min, hsv_max):
        if hsv_min[0] > hsv_max[0]:
            mask1 = cv2.inRange(image_hsv, (0, hsv_min[1], hsv_min[2]), (hsv_max[0], hsv_max[1], hsv_max[2]))
            mask2 = cv2.inRange(image_hsv, (hsv_min[0], hsv_min[1], hsv_min[2]), (180, hsv_max[1], hsv_max[2]))
            mask = mask1 + mask2
        else:
            mask = cv2.inRange(image_hsv, (hsv_min[0], hsv_min[1], hsv_min[2]), (hsv_max[0], hsv_max[1], hsv_max[2]))
        if(not self.console_mode and constants.image_processing_tracing_show_colour_mask):
            cv2.imshow("ColourMask_"+colour, mask)
            cv2.waitKey(1)
        return cv2.reduce(mask, 0, cv2.REDUCE_SUM, dtype=cv2.CV_32S)[0], mask
