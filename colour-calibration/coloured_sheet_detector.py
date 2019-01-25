import cv2
import numpy as np
import json

resolution = (320, 240)
fov = 120
min_number_of_coloured_pixels_per_peak_column = 20
max_number_of_coloured_sheets_per_image = 2
high_colour_zone_threshold_factor_of_peak = 0.7
min_width_for_high_zone = 10

colour_config = None


def read_colour_config():
    global colour_config
    with open('colour_config.json') as json_config_file:
        config = json.load(json_config_file)
    colour_config = config["colour_sheets_hsv_ranges"]


def detect_coloured_sheet(image, is_rgb):
    global colour_config
    read_colour_config()
    image_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV if is_rgb else cv2.COLOR_BGR2HSV)

    colour_sets = []
    for colour in ["green", "blue", "red", "yellow"]:
        mask_aggr = __get_colored_mask_sums(image_hsv, colour_config[colour + "_min"], colour_config[colour + "_max"])
        sum = np.sum(mask_aggr)
        colour_sets.append((colour, sum, mask_aggr))
    colour_sets.sort(key=lambda tup: tup[1], reverse=True)

    found_sheets = []
    for colour_index in range(max_number_of_coloured_sheets_per_image):
        colour, sum, mask_aggr = colour_sets[colour_index]
        peak = np.max(mask_aggr)

        if peak < min_number_of_coloured_pixels_per_peak_column:
            # not enough coloured points even in top column
            continue

        high_zone_threshold = high_colour_zone_threshold_factor_of_peak * peak

        high_zone_start_index = None
        for i in range(len(mask_aggr)):
            if (high_zone_start_index is not None and high_zone_start_index + min_width_for_high_zone < i):
                # we have certainly found high zone for the colour
                break
            if mask_aggr[i] >= high_zone_threshold:
                if high_zone_start_index is None and i + min_width_for_high_zone <= len(mask_aggr):
                    high_zone_start_index = i
                    continue
            else:
                if high_zone_start_index is not None:
                    # high zone did not sustain for a required number of columns - resetting
                    high_zone_start_index = None

        if (high_zone_start_index is None):
            # did not find a high zone
            continue

        high_zone_end_index = None
        for i in range(len(mask_aggr) - 1, 0, -1):
            if (high_zone_end_index is not None and high_zone_end_index - min_width_for_high_zone > i):
                # we have certainly found high zone for the colour
                break
            if mask_aggr[i] >= high_zone_threshold:
                if high_zone_end_index is None and i - min_width_for_high_zone >= 0:
                    high_zone_end_index = i
                    continue
            else:
                if high_zone_end_index is not None:
                    # high zone did not sustain for a required number of columns - resetting
                    high_zone_end_index = None

        if (high_zone_end_index is None):
            # did not find a high zone
            continue

        mid_index = int((high_zone_start_index + high_zone_end_index) / 2)
        x_angle = int((mid_index - int(len(image_hsv[0]) / 2)) * fov / len(image_hsv[0]))
        #print('top', colour_index + 1, 'colour:', colour, 'columns:', high_zone_start_index, ':', high_zone_end_index,'x angle:',x_angle)
        found_sheets.append((colour, x_angle))
    return found_sheets


def __get_colored_mask_sums(image_hsv, hsv_min, hsv_max):
    if hsv_min[0] > hsv_max[0]:
        mask1 = cv2.inRange(image_hsv, (0, hsv_min[1], hsv_min[2]), (hsv_max[0], hsv_max[1], hsv_max[2]))
        mask2 = cv2.inRange(image_hsv, (hsv_min[0], hsv_min[1], hsv_min[2]), (180, hsv_max[1], hsv_max[2]))
        mask = mask1 + mask2
    else:
        mask = cv2.inRange(image_hsv, (hsv_min[0], hsv_min[1], hsv_min[2]), (hsv_max[0], hsv_max[1], hsv_max[2]))
    return cv2.reduce(mask, 0, cv2.REDUCE_SUM, dtype=cv2.CV_32S)[0]
