# import the necessary packages
import picamera.array
from picamera import PiCamera
from threading import Thread, Lock
import cv2
from videoutils.fps import FPS
import time
from fractions import Fraction

class PiStreamOutput(picamera.array.PiAnalysisOutput):
    def __init__(self, camera):
        super(PiStreamOutput, self).__init__(camera)
        self.FPS = FPS()
        self.bytes = None
        self.frame_time_stamp = None

    def analyse(self, array):
        pass

    def write(self, b):
        result = super(PiStreamOutput, self).write(b)
        self.frame_time_stamp = time.time()
        self.bytes = b
        _, fps, frame_num = self.FPS.update()
        return result


class VideoStream:
    def __init__(self, camera_settings):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera_lock = Lock()
        self.camera.resolution = camera_settings['resolution']
        self.camera.framerate = camera_settings['framerate']
        self.camera.vflip=True
        self.camera.hflip = True
        self.last_read_frame_num =-1
        if 'awb_mode' in camera_settings.keys(): self.camera.iso = camera_settings['awb_mode']
        if 'awb_gains' in camera_settings.keys(): self.camera.iso = camera_settings['awb_gains']
        if 'iso' in camera_settings.keys(): self.camera.iso = camera_settings['iso']
        if 'brightness' in camera_settings.keys(): self.camera.iso = camera_settings['brightness']
        if 'contrast' in camera_settings.keys(): self.camera.iso = camera_settings['contrast']
        if 'saturation' in camera_settings.keys(): self.camera.iso = camera_settings['saturation']
        if 'video_denoise' in camera_settings.keys(): self.camera.iso = camera_settings['video_denoise']
        if 'shutter_speed' in camera_settings.keys(): self.camera.iso = camera_settings['shutter_speed']

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.frame_time_stamp = None

        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.process_recording, args=())
        t.daemon = True
        t.start()
        return self

    def read(self):
        if self.output.bytes is not None and self.last_read_frame_num!=self.output.FPS.frameidx:
            self.last_read_frame_num = self.output.FPS.frameidx
            self.frame_time_stamp = self.output.frame_time_stamp
            self.frame = picamera.array.bytes_to_rgb(self.output.bytes, self.camera.resolution)
            # print("digital_gain",self.camera.digital_gain)
            # print("analog_gain",self.camera.analog_gain)
            #print("exposure_speed", self.camera.exposure_speed)

        return self.frame, self.frame_time_stamp

    def stop(self):
        with self.camera_lock:
            # indicate that the thread should be stopped
            self.stopped = True

    def process_recording(self):
        self.output = PiStreamOutput(self.camera)
        self.camera.start_recording(self.output, 'bgr')
        while True:
            with self.camera_lock:
                if self.camera is None:
                    return
                self.camera.wait_recording()
                if self.stopped:
                    self.camera.stop_recording()
                    self.camera.close()
                    return

    def close(self):
        with self.camera_lock:
            self.stopped = True
            self.camera.close()
            self.camera = None