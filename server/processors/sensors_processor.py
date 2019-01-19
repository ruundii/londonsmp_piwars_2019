class SensorsProcessor:
    def __init__(self):
        self.distanceSensorControllerLive = False
        self.colourSensorLive = False

        self.on_distance_update_handler = None
        self.on_line_sensors_update_handler = None

    def set_distance_update_handler(self, handler):
        self.on_distance_update_handler=handler

    def set_line_sensors_update_handler(self, handler):
        self.on_line_sensors_update_handler=handler