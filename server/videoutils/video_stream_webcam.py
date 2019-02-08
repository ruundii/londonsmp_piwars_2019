# import the necessary packages
from threading import Thread, Lock
import cv2
import time


class VideoStream:
    def __init__(self, camera_settings):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(0)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH , camera_settings['resolution'][0])
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_settings['resolution'][1])
        self.stream.set(cv2.CAP_PROP_FPS, camera_settings['framerate'])
        self.camera_lock = Lock()
        (self.grabbed, self.frame) = self.stream.read()
        self.last_read_frame_num = 0
        self.frame_time_stamp = None

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            with self.camera_lock:
                # if the thread indicator variable is set, stop the thread
                if self.stopped:
                    return

                # otherwise, read the next frame from the stream
                (self.grabbed, self.frame) = self.stream.read()
                self.frame_time_stamp = time.time()
                self.last_read_frame_num += 1

    def read(self):
        # return the frame most recently read
        return self.frame, self.frame_time_stamp

    def stop(self):
        with self.camera_lock:
            # indicate that the thread should be stopped
            self.stopped = True

    def close(self):
        with self.camera_lock:
            self.stopped = True
            self.stream.release()
            self.stream = None
