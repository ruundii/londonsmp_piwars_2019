import cv2
import time
from videoutils import util as u
import importlib
from videoutils import alien_detector, coloured_sheet_detector

import config.constants_global as constants


class RobotCamera:
    def __init__(self, resolution, framerate):
        video_stream_module = importlib.import_module(constants.video_stream_module)
        video_stream_class = getattr(video_stream_module, "VideoStream")
        self.vs = video_stream_class(resolution, framerate)
        self.running = False
        self.resolution = resolution
        self.framerate = framerate
        self.camera_matrix = None
        self.distortion_coeffs = None
        self.new_camera_matrix = None
        self.valid_pix_ROI = None
        self.mapx = None
        self.mapy = None

        self.frame = None
        self.gray = None

        self.alien_detector = alien_detector.AlienDetector()
        self.coloured_sheet_detector = coloured_sheet_detector.ColouredSheetDetector()

    def load(self, load_camera_matrix=True):
        if load_camera_matrix:
            camera_matrix, distortion_coeffs = u.load_calibration()
            self.set_camera_matrix(camera_matrix, distortion_coeffs)


    def set_camera_matrix(self, camera_matrix, distortion_coeffs):
        if camera_matrix is None or distortion_coeffs is None:
            self.camera_matrix = None
            self.distortion_coeffs = None
            self.new_camera_matrix = None
            self.valid_pix_ROI = None
            self.mapx = None
            self.mapy = None
            return

        self.camera_matrix = camera_matrix
        self.distortion_coeffs = distortion_coeffs

        self.new_camera_matrix, self.valid_pix_ROI = cv2.getOptimalNewCameraMatrix(self.camera_matrix, self.distortion_coeffs,
                                                                                   self.resolution, 0)
        self.mapx, self.mapy = cv2.initUndistortRectifyMap(self.camera_matrix, self.distortion_coeffs, None,
                                                           self.new_camera_matrix, self.resolution, 5)

    def start(self):
        self.vs.start()
        self.running = True

    def update(self):
        self.frame, self.gray = self.vs.read()
        return self.frame, self.gray

    def last_frame(self):
        return self.frame, self.gray

    def stop(self):
        self.vs.stop()
        self.running = False

    def close(self):
        self.vs.stop()
        self.running = False
        self.vs.close()

    def is_running(self):
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

        return frame

    def detect_aruco(self):
        if self.gray is None:
            return [], None

        try:
            marker_corners, marker_ids, rejected = cv2.aruco.detectMarkers(self.gray,
                                                                         constants.marker_dictionary,
                                                                         parameters=constants.detector_params,
                                                                         cameraMatrix=self.camera_matrix,
                                                                         distCoeff=self.distortion_coeffs
                                                                         )
        except Exception as exc:
            print(exc)
            pass
        return marker_corners, marker_ids


    def detect_aliens(self):
        t = time.time()
        image = self.undistort()
        if image is None:
            return None
        aliens = self.alien_detector.detect_aliens(image, constants.is_rgb_not_bgr)
        if constants.performance_tracing_robot_camera_detect_aliens: print('robot_camera.detect_aliens:',time.time()-t)
        return aliens

    def detect_coloured_sheets(self):
        t = time.time()
        image = self.undistort()
        if image is None:
            return None
        coloured_sheets = self.coloured_sheet_detector.detect_coloured_sheets(image, constants.is_rgb_not_bgr)
        if constants.performance_tracing_robot_camera_detect_coloured_sheets: print('robot_camera.detect_coloured_sheets:',time.time()-t)
        return coloured_sheets