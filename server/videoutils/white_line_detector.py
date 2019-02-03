import cv2
import numpy as np
import json
import config.constants_global as constants
import videoutils.image_display as display
from videoutils.util import get_in_range_mask

class WhiteLineDetector:
    def __init__(self):
        self.resolution = None
        self.fov = None
        print("WhiteLineDetector initialised")

    def set_image_params(self, actual_resolution, fov):
        self.resolution = actual_resolution
        self.fov = fov

    def detect_white_line(self, image, image_gray):

        pass

