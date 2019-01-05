import serial
from time import sleep
from processors.robot_processor_interface import RobotProcessorInterface
from processors.motor import Motor

class RobotRpiProcessor(RobotProcessorInterface):
    def __init__(self):
        super(RobotRpiProcessor, self).__init__()
        self.motor = Motor()


    distanceSensorControllerLive = False
    colourSensorLive = False

    def initialise(self):
        print('Rpi Processor initialised')

    def close(self):
        self.motor.cleanup()
        print('Rpi Processor closed')

    def drive(self, speed_left, speed_right):
        self.motor.drive(speed_left, speed_right)

    def say(self, text, lang):
        pass

