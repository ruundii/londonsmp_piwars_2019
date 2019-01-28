import json
import subprocess
from os import path

import cv2
import numpy as np

import config.constants_global as constants

def get_in_range_mask(image, hsv_min, hsv_max):
  if hsv_min[0] > hsv_max[0]:
    mask1 = cv2.inRange(image, (0, hsv_min[1], hsv_min[2]), (hsv_max[0], hsv_max[1], hsv_max[2]))
    mask2 = cv2.inRange(image, (hsv_min[0], hsv_min[1], hsv_min[2]), (180, hsv_max[1], hsv_max[2]))
    return cv2.bitwise_or(mask1, mask2)
  else:
    return cv2.inRange(image, (hsv_min[0], hsv_min[1], hsv_min[2]), (hsv_max[0], hsv_max[1], hsv_max[2]))


def load_calibration():
  data = load_JSON(constants.camera_calibrations_path, video_filename(''))
  cameraMatrix = np.array(data['cameraMatrix'])
  distCoeffs = np.array(data['distCoeffs'])
  return cameraMatrix, distCoeffs

def video_filename(postfix):
  return str(constants.camera_id)+postfix+'.json'

def load_JSON(dir, filename):
  filename = path.join(dir, filename)
  print('Loading from file:', filename)
  with open(filename, 'r') as f:
    data = json.loads(f.read())
    return data
