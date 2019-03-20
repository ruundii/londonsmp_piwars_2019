import cv2
import time
from videoutils import util as u
import importlib
from videoutils import alien_detector, coloured_sheet_detector, white_line_detector
from _thread import start_new_thread
from threading import Lock

import config.constants_global as constants


class RobotCamera:
    def __init__(self, camera_settings, region_of_interest = None, prepare_gray = False, prepare_hsv=False):
        video_stream_module = importlib.import_module(constants.video_stream_module)
        video_stream_class = getattr(video_stream_module, "VideoStream")
        self.vs = video_stream_class(camera_settings)
        self.running = False
        self.resolution = camera_settings['resolution']
        self.framerate = camera_settings['framerate']
        self.resize_resolution = None if 'resolution_resized' not in camera_settings else camera_settings['resolution_resized']
        self.camera_matrix = None
        self.distortion_coeffs = None
        self.new_camera_matrix = None
        self.valid_pix_ROI = None
        self.mapx = None
        self.mapy = None
        self.image_lock = Lock()

        self.original_frame = None
        self.image = None
        self.image_gray = None
        self.image_hsv = None
        self.frame_timestamp = None
        self.prepare_gray = prepare_gray
        self.prepare_hsv=prepare_hsv
        self.region_of_interest = region_of_interest
        self.actual_resolution = None
        if region_of_interest is None:
            self.fov = constants.camera_fov
        else:
            self.fov = (int(constants.camera_fov[0] * (self.resolution[0]-region_of_interest[2]-region_of_interest[3])/self.resolution[0]) , int(constants.camera_fov[1] * (self.resolution[1]-region_of_interest[0]-region_of_interest[1])/self.resolution[1]))

        self.alien_detector = alien_detector.AlienDetector()
        self.coloured_sheet_detector = coloured_sheet_detector.ColouredSheetDetector()
        self.white_line_detector = white_line_detector.WhiteLineDetector()
        print("RobotCamera init finished")


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
        self.original_frame, self.frame_timestamp = self.vs.read()
        while self.original_frame is None:
            time.sleep(0.005)
            self.original_frame, self.frame_timestamp = self.vs.read()
        if self.resize_resolution is not None:
            self.original_frame = cv2.resize(self.original_frame, self.resize_resolution)
        if self.actual_resolution is None:
            if(self.region_of_interest is not None):
                self.actual_resolution = (len(self.original_frame[0])-self.region_of_interest[2]-self.region_of_interest[3], len(self.original_frame)-self.region_of_interest[0]-self.region_of_interest[1])
            else:
                self.actual_resolution = (len(self.original_frame[0]), len(self.original_frame))
        print('actual_resolution',self.actual_resolution)

        self.alien_detector.set_image_params(self.actual_resolution, self.fov)
        self.coloured_sheet_detector.set_image_params(self.actual_resolution, self.fov)
        self.white_line_detector.set_image_params(self.actual_resolution, self.fov)

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
            self.original_frame, timestamp = self.vs.read()
            if(last_frame_num==self.vs.last_read_frame_num or self.original_frame is None):
                time.sleep(0.005)
                continue
            else:
                last_frame_num = self.vs.last_read_frame_num
            t = time.time()
            if self.resize_resolution is not None:
                self.original_frame = cv2.resize(self.original_frame, self.resize_resolution)
            #cv2.imwrite("image_files/pic" + str(last_frame_num)+".png", self.original_frame)

            im = self.original_frame# self.undistort(self.original_frame)
            if(self.region_of_interest is not None and (self.region_of_interest[0]>0 or self.region_of_interest[1]>0 or self.region_of_interest[2]>0 or self.region_of_interest[3]>0)):
                im = im[self.region_of_interest[0]:len(im)-self.region_of_interest[1], self.region_of_interest[2]:len(im[0])-self.region_of_interest[3]]
            umat_im = cv2.UMat(im)
            umat_im_hsv = None
            umat_im_gray = None
            if self.prepare_hsv:
                #umat_im_hsv = cv2.cvtColor(umat_im, cv2.COLOR_RGB2HSV if constants.is_rgb_not_bgr else cv2.COLOR_BGR2HSV)
                umat_im_hsv = cv2.cvtColor(umat_im, cv2.COLOR_BGR2HSV)
            if self.prepare_gray:
                #umat_im_gray = cv2.cvtColor(umat_im, cv2.COLOR_RGB2GRAY if constants.is_rgb_not_bgr else cv2.COLOR_BGR2GRAY)
                umat_im_gray = cv2.cvtColor(umat_im, cv2.COLOR_BGR2GRAY)
            with(self.image_lock):
                self.image = umat_im
                self.image_hsv = umat_im_hsv
                self.image_gray = umat_im_gray
                self.frame_timestamp = timestamp
            if constants.performance_tracing_robot_camera_image_preparation: print('robot_camera.process_frames:',time.time()-t, 'lag:',time.time()-timestamp)

    def is_image_ready(self, expect_hsv, expect_gray):
        if self.image is None:
            return False
        if expect_hsv and self.image_hsv is None:
            return False
        if expect_gray and self.image_gray is None:
            return False
        return True

    def detect_aliens(self):
        t = time.time()
        frame_timestamp = self.frame_timestamp
        aliens, detected_image = self.alien_detector.detect_aliens(self.image, self.image_hsv)
        if constants.performance_tracing_robot_camera_detect_aliens: print('robot_camera.detect_aliens:',time.time()-t)
        return aliens, frame_timestamp, detected_image

    def detect_coloured_sheets(self):
        t = time.time()
        frame_timestamp = self.frame_timestamp
        coloured_sheets, detected_image = self.coloured_sheet_detector.detect_coloured_sheets(self.image, self.image_hsv)
        if constants.performance_tracing_robot_camera_detect_coloured_sheets: print('robot_camera.detect_coloured_sheets:',time.time()-t)
        return coloured_sheets, frame_timestamp, detected_image

    def detect_white_line(self):
        t = time.time()
        frame_timestamp = self.frame_timestamp
        vector, detected_image = self.white_line_detector.detect_white_line(self.image, self.image_gray)
        if constants.performance_tracing_robot_camera_detect_white_line: print('robot_camera.detect_white_line:', time.time() - t)
        return vector, frame_timestamp, detected_image
