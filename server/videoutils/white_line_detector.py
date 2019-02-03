import cv2
import numpy as np
import json
import config.constants_global as constants
import videoutils.image_display as display
from videoutils.util import get_in_range_mask

NUMBER_OF_CROSS_LINES = 3

class WhiteLineDetector:
    def __init__(self):
        self.resolution = None
        self.fov = None
        with open(constants.regions_config_name) as json_config_file:
            self.regions_config = json.load(json_config_file)["speed_line"]
        print("WhiteLineDetector initialised")

    def set_image_params(self, actual_resolution, fov):
        self.resolution = actual_resolution
        self.fov = fov

    def detect_white_line(self, image_gray):
        # cv2.imwrite("white_line.png",image)
        # cv2.imwrite("white_line_gray.png",image_gray)

        white_line_x_angles = [-1000] * NUMBER_OF_CROSS_LINES
        ret, threshold = cv2.threshold(image_gray, 127, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
        threshold = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel)
        threshold = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
        if(constants.image_processing_tracing_show_colour_mask):
            display.image_display.add_image_to_queue("threshold", threshold.get())
        threshold_image = threshold.get()[:, :] > 127
        for cross_line_index in range(0, NUMBER_OF_CROSS_LINES):
            cross_line_from_bottom =  int(self.regions_config["cross_line_"+str(cross_line_index+1)])
            expected_line_width = int(self.regions_config["line_width_"+str(cross_line_index+1)])
            line = threshold_image[len(threshold_image) - cross_line_from_bottom - 1, :]
            black_to_white_indices, = np.where((line[:-1] ^ line[1:]) & line[1:])  # last black index
            white_to_black_indices, = np.where((line[:-1] ^ line[1:]) & line[:-1])  # last white index
            if (len(white_to_black_indices) == 0 or len(black_to_white_indices) == 0):
                continue
            # todo: check that the road is not over
            current_black_to_white_index = 0
            current_white_to_black_index = 0
            white_lines = []
            if (line[0]):  # if we start with white
                white_lines.append((0, white_to_black_indices[current_white_to_black_index]))
                current_white_to_black_index += 1
            while current_black_to_white_index < len(black_to_white_indices):
                if current_white_to_black_index < len(white_to_black_indices):
                    # white will change to black
                    white_lines.append((black_to_white_indices[current_black_to_white_index] + 1,
                                        white_to_black_indices[current_white_to_black_index]))
                    current_white_to_black_index += 1
                else:
                    # line ands with white
                    white_lines.append((black_to_white_indices[current_black_to_white_index] + 1, len(line) - 1))
                current_black_to_white_index += 1
            best_line_index = -1
            closest_width_difference = 10000
            for i in range(0, len(white_lines)):
                actual_line_width = white_lines[i][1] - white_lines[i][0]
                width_diff = actual_line_width - expected_line_width
                if (width_diff > 4 and max(actual_line_width, expected_line_width) / float(
                        min(actual_line_width, expected_line_width)) > 2.0):
                    # line is not what we expect at all
                    continue
                if (closest_width_difference > width_diff):
                    closest_width_difference = width_diff
                    best_line_index = i
            # print("black_to_white_indices", black_to_white_indices)
            # print("white_to_black_indices", white_to_black_indices)
            # print("white_lines", white_lines)
            if best_line_index >= 0:
                # print("winning line", white_lines[best_line_index])
                middle_pixel = int(round((white_lines[best_line_index][1] + white_lines[best_line_index][0]) / 2.0))
                x_angle = int(round((middle_pixel - int(self.resolution[0] / 2)) * self.fov[0] / self.resolution[0]))
                white_line_x_angles[cross_line_index] = x_angle

        return white_line_x_angles
