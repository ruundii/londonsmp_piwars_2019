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

isPi = True
cameraId = "surface"
calibrationsPath = "videoutils\calibrations"
#resolution_pi = (640, 480)
#framerate_pi = 20

resolution = (640, 480)
framerate = 10

STATE_TRACKING = 0
STATE_FLASHLIGHT = 1