import json
import subprocess
from os import path

import cv2
import numpy as np

import config.constants_global as constants


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
