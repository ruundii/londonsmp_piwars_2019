import cv2

from videoutils import util as u
import platform
from datetime import datetime
import importlib

import config.constants_global as constants

class RobotCamera:
    def __init__(self):
        video_stream_module = importlib.import_module(constants.video_stream_module)
        video_stream_class = getattr(video_stream_module, "VideoStream")
        self.vs = video_stream_class()
        self.running = False

        self.cameraMatrix = None
        self.distCoeffs = None
        self.perspectiveTransform = None
        self.newCameraMatrix = None
        self.validPixROI = None
        self.mapx = None
        self.mapy = None
        self.heightTransform = None

        self.frame = None
        self.gray = None
        self.grayUndistorted = None
        self.isPreundistored = False

    def load(self, loadCameraMatrix=True, loadPerspective=False, loadHeight=False):
        if loadCameraMatrix:
            cameraMatrix, distCoeffs = u.loadCalibration()
            self.setCameraMatrix(cameraMatrix, distCoeffs)

        if loadPerspective and self.cameraMatrix is not None and self.distCoeffs is not None:
            perspectiveTransform = u.loadPerspective()
            self.setPerspective(perspectiveTransform)

        if loadHeight:
            heightTransform = u.loadHeight()
            self.setHeight(heightTransform)
        print('loaded camera params')


    def setCameraMatrix(self, cameraMatrix, distCoeffs):
        if cameraMatrix is None or distCoeffs is None:
            self.cameraMatrix = None
            self.distCoeffs = None
            self.newCameraMatrix = None
            self.validPixROI = None
            self.mapx = None
            self.mapy = None
            return

        self.cameraMatrix = cameraMatrix
        self.distCoeffs = distCoeffs

        self.newCameraMatrix, self.validPixROI = cv2.getOptimalNewCameraMatrix(self.cameraMatrix, self.distCoeffs,
                                                                               constants.resolution, 0)
        self.mapx, self.mapy = cv2.initUndistortRectifyMap(self.cameraMatrix, self.distCoeffs, None,
                                                           self.newCameraMatrix, constants.resolution, 5)

    def setPerspective(self, perspectiveTransform):
        self.perspectiveTransform = perspectiveTransform

    def setHeight(self, heightTransform):
        self.heightTransform = heightTransform

    def start(self):
        self.vs.start()
        self.running = True

    def update(self):
        self.frame, self.gray = self.vs.read()
        return self.frame, self.gray

    def lastFrame(self):
        return self.frame, self.gray

    def stop(self):
        self.vs.stop()
        self.running = False

    def isRunning(self):
        return self.running

    def undistort(self, gray=False):
        if gray:
            frame = self.gray
        else:
            frame = self.frame

        if frame is None:
            return None

        if self.mapx is not None and self.mapy is not None:
            frame = cv2.remap(frame, self.mapx, self.mapy, cv2.INTER_LINEAR)
        # if self.perspectiveTransform is not None:
        #   frame = cv2.warpPerspective(frame, self.perspectiveTransform, constants.mappedImageResolution)

        return frame

    def detectAruco(self):
        if self.gray is None:
            return [], None

        try:
            markerCorners, markerIds, rejected = cv2.aruco.detectMarkers(self.gray,
                                                                         constants.markerDictionary,
                                                                         parameters=constants.detectorParams,
                                                                         cameraMatrix=self.cameraMatrix,
                                                                         distCoeff=self.distCoeffs
                                                                          )
        except Exception as exc:
            print(exc)
            pass
        return markerCorners, markerIds

    # def transformMarkers(self, markerCorners, markerIds, imgCenter=constants.mappedImageCenter, imgScale=constants.outImageMappedHeight):
    #   if markerCorners is None or markerIds is None:
    #     return []
    #
    #   positions = {}
    #   imgCenterPx = np.divide(np.array(constants.mappedImageResolution), 2.0)
    #
    #   for i in range(len(markerCorners)):
    #     markerId = int(markerIds[i])
    #     markerCornerSet = markerCorners[i]
    #
    #     # Undistort
    #     if self.cameraMatrix is not None and self.distCoeffs is not None:
    #       markerCornerSet = cv2.undistortPoints(markerCornerSet, self.cameraMatrix, self.distCoeffs, P=self.newCameraMatrix)
    #
    #     # calculate the center and up direction for the markers
    #     rawMarkerCenterPx, rawMarkerUpPx = u.centerAndUp(markerCornerSet)
    #     if self.heightTransform is not None:
    #       markerCenterPx, markerUpPx = u.transformPixels([rawMarkerCenterPx, rawMarkerUpPx], self.heightTransform)
    #     else:
    #       markerCenterPx, markerUpPx = rawMarkerCenterPx, rawMarkerUpPx
    #
    #     if self.perspectiveTransform is not None:
    #       markerCenterPx, markerUpPx = u.transformPixels([markerCenterPx, markerUpPx], self.perspectiveTransform)
    #       rawMarkerCenterPx, rawMarkerUpPx = u.transformPixels([rawMarkerCenterPx, rawMarkerUpPx], self.perspectiveTransform)
    #
    #     rawDistPx, rawDistNorm, rawUpPx, rawUpNorm = u.normalizePtUp(rawMarkerCenterPx, rawMarkerUpPx, imgCenter, imgScale)
    #     distPx, distNorm, upPx, upNorm = u.normalizePtUp(markerCenterPx, markerUpPx, imgCenter, imgScale)
    #
    #     positions[markerId] = {
    #       'pos': distNorm,
    #       'up': upNorm,
    #       'rawPos': rawDistNorm,
    #       'rawUp': rawUpNorm,
    #
    #       'markerCenterPx': markerCenterPx,
    #       'markerUpPx': markerUpPx,
    #       'rawMarkerCenterPx': rawMarkerCenterPx,
    #       'rawMarkerUpPx': rawMarkerUpPx
    #     }
    #
    #   return positions
