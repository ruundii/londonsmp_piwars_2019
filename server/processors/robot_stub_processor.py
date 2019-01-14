from threading import Thread
from time import sleep
from processors.robot_processor_interface import RobotProcessorInterface
import random

class RobotPlatformProcessor(RobotProcessorInterface):
    def __init__(self):
        super(RobotPlatformProcessor, self).__init__()
        self.markersThread = None

    def initialise(self):
        print('initialise')
        self.sendUpdates = True

        return

    def close(self):
        print('close')
        self.sendUpdates = False
        return

    def drive(self, speedLeft, speedRight):
        print('drive speedLeft: ' + str(speedLeft) + ' speedRight: ' + str(speedRight))
        return


    def say(self, text, lang):
        pass

    def displayText(self, text, lines):
        print(text, lines)