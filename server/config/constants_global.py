camera_calibrations_path = "videoutils\calibrations"


# open cv / aruco constants
import cv2
imgPPI = 72
inToM = 0.0254

posterMaxWidthIn = 8.1
posterMaxHeightIn = 11.5
posterMaxWidthM = posterMaxWidthIn * inToM
posterMaxHeightM = posterMaxHeightIn * inToM

charucoNSqVert = 10
charucoSqSizeM = float(posterMaxHeightM) / float(charucoNSqVert)
charucoMarkerSizeM = charucoSqSizeM * 0.7
charucoNSqHoriz = int(posterMaxWidthM / charucoSqSizeM)

charucoDictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
charucoBoard = cv2.aruco.CharucoBoard_create(charucoNSqHoriz, charucoNSqVert, charucoSqSizeM, charucoMarkerSizeM, charucoDictionary)
charucoDimsM = charucoImgDims = (charucoNSqHoriz * charucoSqSizeM / inToM, charucoNSqVert * charucoSqSizeM / inToM)
charucoImgDims = (int(charucoDimsM[0] * imgPPI), int(charucoDimsM[1] * imgPPI))

markerDictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
markerSizeIn = 3
markerSizeM = markerSizeIn * inToM

detectorParams = cv2.aruco.DetectorParameters_create()
detectorParams.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
detectorParams.cornerRefinementMaxIterations = 500
# detectorParams.cornerRefinementWinSize = 1
detectorParams.cornerRefinementMinAccuracy = 0.001
# detectorParams.minMarkerPerimeterRate = 0.05
# detectorParams.maxMarkerPerimeterRate = 0.2
detectorParams.adaptiveThreshWinSizeMin = 10
# detectorParams.adaptiveThreshWinSizeStep = 3
detectorParams.adaptiveThreshWinSizeMax = 10


#importing machine-specific constants
import importlib
from uuid import getnode as get_mac
constants_specific = importlib.import_module("config.constants_"+str(get_mac()))

module_dict = constants_specific.__dict__
try:
    to_import = constants_specific.__all__
except AttributeError:
    to_import = [name for name in module_dict if not name.startswith('_')]
globals().update({name: module_dict[name] for name in to_import})

