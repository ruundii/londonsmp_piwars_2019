import cv2
import numpy as np
import json
import config.constants_global as constants
import videoutils.image_display as display
from videoutils.util import get_in_range_mask
import math

class WhiteLineDetector:
    def __init__(self):
        self.resolution = None
        self.fov = None
        with open(constants.regions_config_name) as json_config_file:
            self.regions_config = json.load(json_config_file)["speed_line"]
        self.cross_lines = []
        for i in range(0,self.regions_config["cross_line_top"]):
            self.cross_lines.append((self.regions_config["line_width_bottom"]+5*i,
                                     self.regions_config["cross_line_bottom"] -
                                      int(i/self.regions_config["cross_line_top"]*(self.regions_config["line_width_bottom"]
                                                                                   -self.regions_config["line_width_top"]))))
        self.number_of_cross_lines = self.regions_config["cross_line_top"]
        print("WhiteLineDetector initialised")


    def set_image_params(self, actual_resolution, fov):
        self.resolution = actual_resolution
        self.fov = fov

    def detect_white_line(self, image, image_gray):
        if (constants.image_processing_tracing_show_detected_objects):
            image = image.get()

        white_line_x_angles = [-1000] * self.number_of_cross_lines

        #prepare image
        ret, threshold = cv2.threshold(image_gray, 127, 1, cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
        threshold = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel)
        threshold = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
        threshold_mat = threshold.get()

        if(constants.image_processing_tracing_show_colour_mask):
            display.image_display.add_image_to_queue("threshold", threshold_mat*255)

        last_white_line_found = None
        last_white_line_found_row_index = -1

        for cross_line_index in range(0, self.number_of_cross_lines):
            cross_line_from_bottom =  self.cross_lines[cross_line_index][0]
            expected_line_width = self.cross_lines[cross_line_index][1]
            line = threshold_mat[len(threshold_mat) - cross_line_from_bottom - 1, :] > 0
            black_to_white_indices, = np.where((line[:-1] ^ line[1:]) & line[1:])  # last black index
            white_to_black_indices, = np.where((line[:-1] ^ line[1:]) & line[:-1])  # last white index
            if (len(white_to_black_indices) == 0 or len(black_to_white_indices) == 0):
                continue

            white_lines = self.find_white_line_candidates(black_to_white_indices, line, white_to_black_indices)
            best_line_index, end_of_the_road_found = self.find_best_white_line_match(expected_line_width, last_white_line_found, white_lines)
            if end_of_the_road_found:
                break
            if best_line_index >= 0:
                last_white_line_found_row_index = cross_line_index
                last_white_line_found = (white_lines[best_line_index][0], white_lines[best_line_index][1])
                middle_pixel = int(round((white_lines[best_line_index][1] + white_lines[best_line_index][0]) / 2.0))
                x_angle = int(round((middle_pixel - int(self.resolution[0] / 2)) * self.fov[0] / self.resolution[0]))
                white_line_x_angles[cross_line_index] = x_angle
                if(constants.image_processing_tracing_show_detected_objects):
                    image = cv2.line(image,(white_lines[best_line_index][0],len(image) - cross_line_from_bottom - 1),
                                               (white_lines[best_line_index][1],len(image) - cross_line_from_bottom - 1),(0,255,0), 2)
            elif last_white_line_found_row_index>=0 and cross_line_index>last_white_line_found_row_index+3:
                #end of the road
                break

        vector = self.convert_to_line_direction_vector(white_line_x_angles)

        if(constants.image_processing_tracing_show_detected_objects):
            image = cv2.line(image,
                (int(vector[1] * self.resolution[0]/self.fov[0] + self.resolution[0]/2), len(threshold_mat)-self.cross_lines[self.number_of_cross_lines-1][0]),
                (int(vector[0] * self.resolution[0]/self.fov[0] + self.resolution[0] / 2), len(threshold_mat) - self.cross_lines[0][0]),(255,0,0),2)
            display.image_display.add_image_to_queue("detected", image)

        return vector

    def convert_to_line_direction_vector(self, white_line_x_angles):
        #if white_line_x_angles.count(-1000) > 12:
        #    return (0,0) #treat as end of line and return straight vector

        first_line_index = None
        last_line_index = None
        current_sequence_size = 0
        max_sequence_size = 0
        for i in range(0, len(white_line_x_angles)):
            if(white_line_x_angles[i]==-1000):
                current_sequence_size = 0
                continue
            current_sequence_size += 1
            max_sequence_size = max(max_sequence_size, current_sequence_size)
            if(first_line_index is None): first_line_index = i
            last_line_index = i

        if max_sequence_size<4:
            return (0, 0)  # treat as end of line and return straight vector

        vector_start = white_line_x_angles[first_line_index]
        vector_end = white_line_x_angles[last_line_index]

        if first_line_index ==0 and last_line_index==self.number_of_cross_lines-1:
            return (vector_start, vector_end)

        slope = (white_line_x_angles[last_line_index]-white_line_x_angles[first_line_index])/(last_line_index-first_line_index)
        if(first_line_index>0):
            vector_start -= slope*first_line_index
        if (last_line_index <  self.number_of_cross_lines-1):
            vector_end += slope * (self.number_of_cross_lines-1-last_line_index)
        vector_start = max(min(vector_start,int(self.fov[0]/2)), -int(self.fov[0]/2))
        vector_end = max(min(vector_end, int(self.fov[0] / 2)), -int(self.fov[0] / 2))
        return (vector_start, vector_end)

    def find_best_white_line_match(self, expected_line_width, last_white_line_found, white_lines):
        best_line_index = -1
        min_difference = 10000000
        for i in range(0, len(white_lines)):
            white_line_start_index, white_line_end_index, preceding_black_line_width, following_black_line_width = white_lines[i]
            actual_line_width = white_line_end_index - white_line_start_index

            if (last_white_line_found is not None
                and white_line_start_index<last_white_line_found[0] #current white line starts earlier than last found white line
                and white_line_end_index>last_white_line_found[1] #current white line ends later than last found white line
                and last_white_line_found[1]-last_white_line_found[0]<0.4*actual_line_width): #and current line is much wider than previous one
                # treat it as the end of the road
                return -1, True

            width_diff = abs(actual_line_width - expected_line_width)
            if (actual_line_width > 4 and expected_line_width > 4 and max(actual_line_width,
                                                                          expected_line_width) / float(
                    min(actual_line_width, expected_line_width)) > 2.0):
                # line is not what we expect at all
                continue
            if (
                    preceding_black_line_width < expected_line_width * 0.5 or following_black_line_width < expected_line_width * 0.5):
                # surrounding black lines are too small
                continue
            current_difference = math.log(width_diff + 3) / (
                        math.log(following_black_line_width + 3) * math.log(preceding_black_line_width + 3))
            if (min_difference > current_difference):
                min_difference = current_difference
                best_line_index = i

        if(last_white_line_found is not None and best_line_index>=0):
            #check that this white line is plausible given the previous white line
            current_white_line = white_lines[best_line_index]
            if current_white_line[1]-current_white_line[0] > 1.3*(last_white_line_found[1]-last_white_line_found[0]):
                #if this line is much wider than last line - discard
                return -1, False
            if(abs(current_white_line[0]-last_white_line_found[0])>30 or abs(current_white_line[1]-last_white_line_found[1])>30):
                #if the position is too far away
                return -1, False
        return best_line_index, False

    def find_white_line_candidates(self, black_to_white_indices, line, white_to_black_indices):
        current_black_to_white_index = 0
        current_white_to_black_index = 0
        white_lines = []
        if (line[0]):  # if we start with white - skip first white block as we must start from black
            current_white_to_black_index += 1
        while current_black_to_white_index < len(black_to_white_indices):  # get next start of white line
            if current_white_to_black_index < len(white_to_black_indices):  # get next end of white line
                # white will change to black
                # calculate preceding black width
                if (current_white_to_black_index - 1 >= 0):
                    preceding_black_width = black_to_white_indices[current_black_to_white_index] - \
                                            white_to_black_indices[current_white_to_black_index - 1]
                else:
                    preceding_black_width = black_to_white_indices[current_black_to_white_index]
                # calculate following black width
                if (current_black_to_white_index + 1 < len(black_to_white_indices)):
                    following_black_width = black_to_white_indices[current_black_to_white_index + 1] - \
                                            white_to_black_indices[current_white_to_black_index]
                else:
                    following_black_width = self.resolution[0] - white_to_black_indices[current_white_to_black_index]

                white_lines.append((black_to_white_indices[current_black_to_white_index] + 1,
                                    white_to_black_indices[current_white_to_black_index], preceding_black_width,
                                    following_black_width))
                current_white_to_black_index += 1
            else:
                # image line ends with white - skip. (was white_lines.append((black_to_white_indices[current_black_to_white_index] + 1, len(line) - 1))
                pass
            current_black_to_white_index += 1
        return white_lines
