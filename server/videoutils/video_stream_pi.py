# import the necessary packages
import picamera.array
from picamera import PiCamera
from threading import Thread, Lock
import cv2
from videoutils.fps import FPS


class PiStreamOutput(picamera.array.PiAnalysisOutput):
    def __init__(self, camera):
        super(PiStreamOutput, self).__init__(camera)
        self.FPS = FPS()
        self.bytes = None

    def analyse(self, array):
        pass

    def write(self, b):
        result = super(PiStreamOutput, self).write(b)
        self.bytes = b
        _, fps, frame_num = self.FPS.update()
        return result


class VideoStream:
    def __init__(self, resolution, framerate):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera_lock = Lock()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.camera.awb_mode='off'
        self.camera.awb_gains = (1.0, 2.6)
        self.camera.iso = 800
        self.camera.vflip=True
        self.camera.hflip = True
        self.last_read_frame_num =-1
        self.camera.brightness = 55
        self.camera.saturation = 40

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None

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
            self.frame = picamera.array.bytes_to_rgb(self.output.bytes, self.camera.resolution)

        return self.frame

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