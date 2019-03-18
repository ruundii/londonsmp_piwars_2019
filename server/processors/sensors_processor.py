try:
    import serial
except:
    print("Could not import serial")
from threading import Thread
import time

class SensorsProcessor:
    def __init__(self):
        self.distance_controller_live = False
        self.colour_sensors_live = False

        self.on_distance_update_handler = None
        self.on_line_sensors_update_handler = None

        self.serial_connection = None
        self.distance_thread = None

    def start_sensor(self):
        try:
            self.serial_connection = serial.Serial("/dev/ttyUSB0", 19200, timeout=1, parity=serial.PARITY_NONE,
                                             stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, )
            self.distance_controller_live = True
        except Exception as e:
            self.distance_controller_live = False
            print("Could not open serial at /dev/ttyUSB0",e)
            return
        if self.distance_thread is None or not self.distance_thread.isAlive():
            self.distance_thread = Thread(target=self.update_distance)
            self.distance_thread.start()

    def stop_sensor(self):
        self.distance_controller_live = False
        if self.serial_connection is not None:
            self.serial_connection.close()
            self.serial_connection = None

    def update_distance(self):
        #i = 0
        #t = time.time()
        while self.distance_controller_live:
            #i+=1
            try:
                readings = self.serial_connection.readline().decode().rstrip().split(',')
                #if(i%20==0): print("t",time.time()-t, "readings", readings)
                if(len(readings)>=3):
                    #print("readings",readings)
                    payload = \
                        {'message': 'updateDistanceSensorsReadings', 'readings': {
                            'L': float(readings[2]),
                            'C': float(readings[1]),
                            'R': float(readings[0])
                            }
                        }
                    if self.on_distance_update_handler is not None:
                        self.on_distance_update_handler(payload)
            except Exception as e:
                print("update distance exception",e)
                pass
            #time.sleep(0.01)
            #t = time.time()


    def set_distance_update_handler(self, handler):
        self.on_distance_update_handler=handler

    def set_line_sensors_update_handler(self, handler):
        self.on_line_sensors_update_handler=handler