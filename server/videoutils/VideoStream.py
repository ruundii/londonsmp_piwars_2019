# import the necessary packages
from videoutils.WebcamVideoStream import WebcamVideoStream
import config.constants_global as constants


class VideoStream:
    def __init__(self):
        # check to see if the picamera module should be used
        if constants.use_pi_camera:
            # only import the picamera packages unless we are
            # explicity told to do so -- this helps remove the
            # requirement of `picamera[array]` from desktops or
            # laptops that still want to use the `imutils` package
            from videoutils.PiVideoStream import PiVideoStream

            # initialize the picamera stream and allow the camera
            # sensor to warmup
            self.stream = PiVideoStream()

        # otherwise, we are using OpenCV so initialize the webcam
        # stream
        else:
            self.stream = WebcamVideoStream()

    def start(self):
        # start the threaded video stream
        return self.stream.start()

    def read(self):
        # return the current frame
        return self.stream.read()

    def stop(self):
        # stop the thread and release any resources
        self.stream.stop()
