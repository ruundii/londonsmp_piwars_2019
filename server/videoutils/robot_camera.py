import cv2
import time
from videoutils import util as u
import importlib
from videoutils import alien_detector, coloured_sheet_detector
from _thread import start_new_thread

import config.constants_global as constants


class RobotCamera:
    def __init__(self, resolution, framerate, region_of_interest = None, prepare_gray = False, prepare_hsv=False):
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

        self.original_frame = None
        self.image = None
        self.image_gray = None
        self.image_hsv = None
        self.prepare_gray = prepare_gray
        self.prepare_hsv=prepare_hsv
        self.region_of_interest = region_of_interest
        if region_of_interest is None:
            self.fov = constants.camera_fov
        else:
            self.fov = (int(constants.camera_fov[0] * (resolution[0]-region_of_interest[2]-region_of_interest[3])/resolution[0]) , int(constants.camera_fov[1] * (resolution[1]-region_of_interest[0]-region_of_interest[1])/resolution[1]))

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
        start_new_thread(self.process_frames,())

    def current_image(self):
        return self.image

    def current_image_gray(self):
        return self.image_gray

    def current_image_hsv(self):
        return self.image_hsv

    def stop(self):
        self.vs.stop()
        self.running = False

    def close(self):
        self.vs.stop()
        self.running = False
        self.vs.close()

    def is_running(self):
        return self.running

    def undistort(self, image):
        if image is None:
            return None

        if self.mapx is not None and self.mapy is not None:
            return cv2.remap(image, self.mapx, self.mapy, cv2.INTER_LINEAR)

        return image

    def process_frames(self):
        last_frame_num = -1
        while self.running:
            self.original_frame = self.vs.read()
            if(last_frame_num==self.vs.last_read_frame_num or self.original_frame is None):
                time.sleep(0.005)
                continue
            else:
                last_frame_num = self.vs.last_read_frame_num
            self.image = self.undistort(self.original_frame)
            if(self.region_of_interest is not None):
                self.image = self.image[self.region_of_interest[0]:len(self.image)-self.region_of_interest[1], self.region_of_interest[2]:len(self.image[0])-self.region_of_interest[3]]
            if self.prepare_hsv:
                self.image_hsv = cv2.cvtColor(self.image, cv2.COLOR_RGB2HSV if constants.is_rgb_not_bgr else cv2.COLOR_BGR2HSV)
            if self.prepare_gray:
                self.image_gray = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY if constants.is_rgb_not_bgr else cv2.COLOR_BGR2GRAY)

    def detect_aliens(self):
        t = time.time()
        if self.image is None and self.image_hsv is None:
            return None
        aliens = self.alien_detector.detect_aliens(self.image, self.image_hsv, self.fov)
        if constants.performance_tracing_robot_camera_detect_aliens: print('robot_camera.detect_aliens:',time.time()-t)
        return aliens

    def detect_coloured_sheets(self):
        t = time.time()
        if self.image is None and self.image_hsv is None:
            return None
        coloured_sheets = self.coloured_sheet_detector.detect_coloured_sheets(self.image, self.image_hsv, self.fov)
        if constants.performance_tracing_robot_camera_detect_coloured_sheets: print('robot_camera.detect_coloured_sheets:',time.time()-t)
        return coloured_sheets