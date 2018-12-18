# import the necessary packages
from threading import Thread
import cv2

class VideoStream:
    def __init__(self, isPi, resolution,
                 framerate):
        # initialize the video camera stream and read the first frame
        # from the stream
        if isPi:
            gst_str = ('nvcamerasrc !'
                       'video/x-raw(memory:NVMM), '
                       'width=(int)2592, height=(int)1944, '
                       'format=(string)I420, framerate=(fraction){}/1 ! '
                       'nvvidconv ! '
                       'video/x-raw, width=(int){}, height=(int){}, '
                       'format=(string)BGRx ! '
                       'videoconvert ! appsink').format(framerate, resolution[0], resolution[1])
            self.stream = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)
        else:
            self.stream = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.stream.read()
        self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

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
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()
            try:
                if self.frame is not None:
                    self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                else:
                    self.gray = None
            except Exception:
                self.gray=None


    def read(self):
        # return the frame most recently read
        return self.frame, self.gray

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
