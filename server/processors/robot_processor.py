import math
import time
from processors.camera_processor import CameraProcessor
from processors.sensors_processor import SensorsProcessor

import importlib
import config.constants_global as constants

class RobotProcessor:

    def __init__(self):
        motor_module = importlib.import_module(constants.motor_module)
        motor_class = getattr(motor_module, "Motor")
        self.motor = motor_class()
        self.camera_processor = CameraProcessor()
        self.sensors_processor = SensorsProcessor()
        self.client_server_time_difference = 0

    def initialise(self):
        print('Processor initialised')

    def close(self):
        self.stop_run()
        print('Processor closed')

    def stop_run(self):
        self.motor.drive(0,0)
        self.camera_processor.set_camera_mode(-1)
        print('Run stopped')

    def set_alien_update_handler(self, handler):
        self.camera_processor.set_alien_update_handler(handler)

    def set_coloured_sheet_update_handler(self, handler):
        self.camera_processor.set_coloured_sheet_update_handler(handler)

    def set_white_line_update_handler(self, handler):
        self.camera_processor.set_white_line_update_handler(handler)

    def set_distance_update_handler(self, handler):
        self.sensors_processor.set_distance_update_handler(handler)

    def set_line_sensors_update_handler(self, handler):
        self.sensors_processor.set_line_sensors_update_handler(handler)

    def drive(self, speed_left, speed_right):
        self.motor.drive(speed_left, speed_right)
        self.camera_processor.set_last_drive_params(speed_left, speed_right)

    def set_camera_mode(self, mode):
        self.camera_processor.set_camera_mode(mode)

    def set_client_server_time_difference(self, time_diff):
        self.client_server_time_difference = time_diff
        self.camera_processor.set_client_server_time_difference(time_diff)