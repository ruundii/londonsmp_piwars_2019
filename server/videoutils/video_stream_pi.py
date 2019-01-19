# import the necessary packages
import picamera.array
from picamera import PiCamera
from threading import Thread, Lock
import cv2
from videoutils.fps import FPS
from datetime import datetime

import config.constants_global as constants


class PiStreamOutput(picamera.array.PiAnalysisOutput):
    def __init__(self, camera):
        super(PiStreamOutput, self).__init__(camera)
        self.FPS = FPS()
        self.bytes = None

    def analyse(self, array):
        pass
    # def analyse(self, array):
    #     _, fps, frameNum = self.FPS.update()
    #     # grab the frame from the stream and clear the stream in
    #     # preparation for the next frame
    #     # self.frame = cv2.flip(f.array, 0)
    #     self.frame = array
    #     print("FPS:" + str(fps) + " Frame num:" + str(frameNum))

    def write(self, b):
        result = super(PiStreamOutput, self).write(b)
        self.bytes = b
        _, fps, frameNum = self.FPS.update()
        #print("FPS Analyser:" + str(fps) + " Frame num:" + str(frameNum))
        #self.analyze(bytes_to_rgb(b, self.size or self.camera.resolution))
        return result


class VideoStream:
    def __init__(self):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera_lock = Lock()
        self.camera.resolution = constants.resolution
        self.camera.framerate = constants.framerate
        self.camera.awb_mode='off'
        self.camera.awb_gains = (0.9, 2.5)
        self.camera.vflip=True
        self.camera.hflip = True
        self.last_read_frame_num =-1;
        self.camera.brightness = 65

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.gray = None

        self.stopped = False
        #self.FPS = FPS()

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.process_recording, args=())
        t.daemon = True
        t.start()
        return self

    def read(self):
        #dt = datetime.now()
        #_, fps, frameNum = self.FPS.update()
        #print("FPS Pi video stream:" + str(fps) + " Frame num:" + str(frameNum))
        if self.output.bytes is not None and self.last_read_frame_num!=self.output.FPS.frameidx:
            self.frame = picamera.array.bytes_to_rgb(self.output.bytes, self.camera.resolution)
            #pic = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            #cv2.imwrite("frame"+str(self.output.FPS.frameidx)+".jpg", pic)
            #print("gains:",self.camera.awb_gains)
            self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            #print("read ", (datetime.now()-dt).total_seconds())

        return self.frame, self.gray

    def stop(self):
        with self.camera_lock:
            # indicate that the thread should be stopped
            self.stopped = True

    def process_recording(self):
        self.output = PiStreamOutput(self.camera)
        self.camera.start_recording(self.output, 'rgb')
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