import serial
from time import sleep
from processors.robot_processor_interface import RobotProcessorInterface
import importlib

import config.constants_global as constants

class RobotPlatformProcessor(RobotProcessorInterface):
    def __init__(self):
        super(RobotPlatformProcessor, self).__init__()
        motor_module = importlib.import_module(constants.motor_module)
        motor_class = getattr(motor_module, "Motor")
        self.motor = motor_class()

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

