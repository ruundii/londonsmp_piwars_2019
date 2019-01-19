import cv2

from videoutils import util as u
from videoutils import centroid_area_tracker
import importlib

import config.constants_global as constants


class RobotCamera:
    def __init__(self):
        video_stream_module = importlib.import_module(constants.video_stream_module)
        video_stream_class = getattr(video_stream_module, "VideoStream")
        self.vs = video_stream_class()
        self.running = False

        self.camera_matrix = None
        self.distortion_coeffs = None
        self.new_camera_matrix = None
        self.valid_pix_ROI = None
        self.mapx = None
        self.mapy = None

        self.frame = None
        self.gray = None

        self.alien_tracker = centroid_area_tracker.CentroidAreaTracker()

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
                                                                                   constants.resolution, 0)
        self.mapx, self.mapy = cv2.initUndistortRectifyMap(self.camera_matrix, self.distortion_coeffs, None,
                                                           self.new_camera_matrix, constants.resolution, 5)

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
        # https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
        # https://github.com/llSourcell/Object_Detection_demo_LIVE/blob/master/demo.py
        # https://pythonprogramming.net/morphological-transformation-python-opencv-tutorial/
        aliens = []
        image_hsv = cv2.cvtColor(self.undistort(), cv2.COLOR_BGR2HSV)
        # frame = imutils.resize(frame, width=600)
        # image_hsv = cv2.medianBlur(image_hsv, 15)
        # image_hsv = cv2.GaussianBlur(image_hsv, (11, 11), 0)
        mask = cv2.inRange(image_hsv, constants.green_lower_bound_hsv, constants.green_higher_bound_hsv)
        # mask = cv2.erode(mask, None, iterations=2)
        # mask = cv2.dilate(mask, None, iterations=2)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        _, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                                    cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if (len(cnt) < 5): continue
            ellipse = cv2.fitEllipse(cnt)
            area = cv2.contourArea(cnt)
            ellipseRatio = ellipse[1][1] / ellipse[1][0]
            #print('size:',ellipse[1], ' ratio:',ellipseRatio, ' area:',area)
            if ellipseRatio > 1.3 and ellipseRatio < 3 and ellipse[1][1] > 3 and area>15:
                aliens.append(
                    (ellipse[0][0], #x
                     ellipse[0][1], #y
                     area,
                     ellipse[1][1])) #height
        return self.alien_tracker.update(aliens)
