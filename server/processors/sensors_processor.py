import serial
import time
import os
is_raspberry = os.name != 'nt'
from _thread import start_new_thread
from processors.gyro import Gyro

class SensorsProcessor:
    def __init__(self):
        self.distance_controller_live = False
        self.gyro_live = False
        self.colour_sensors_live = False

        self.on_distance_update_handler = None
        self.on_orientation_update_handler = None
        self.on_line_sensors_update_handler = None

        self.serial_connection = None
        self.distance_thread = None
        self.gyro = None
        self.gyro_thread = None


    def start_sensor(self):
        try:
            if is_raspberry:
                self.serial_connection = serial.Serial("/dev/ttyUSB0", 19200, timeout=1, parity=serial.PARITY_NONE,
                                                       stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, )
            else:
                self.serial_connection = serial.Serial("COM3", 19200, timeout=1, parity=serial.PARITY_NONE,
                                                       stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, )
            self.distance_controller_live = True
        except Exception as e:
            self.distance_controller_live = False
            print("Could not open serial at /dev/ttyUSB0",e)
            return
        start_new_thread(self.__process_sensor_messages,())
        try:
            self.gyro = Gyro(0x68)
            self.gyro_live = True
        except Exception as e:
            self.gyro_live = False
            print("Could not start gyroscope",e)
            return
        start_new_thread(self.__process_gyro,())



    def stop_sensor(self):
        self.distance_controller_live = False
        if self.serial_connection is not None:
            self.serial_connection.close()
            self.serial_connection = None
        self.gyro_live = False
        self.gyro = None

    def __process_sensor_messages(self):
        self.serial_connection.reset_input_buffer()
        # i = 0
        # orig_time = time.time()
        # t = time.time()
        while True:
            # i +=1
            try:
                while self.distance_controller_live and self.serial_connection.in_waiting==0:
                    time.sleep(0.001)
                if not self.distance_controller_live:
                    break
                readings = self.serial_connection.readline().decode().rstrip().split(',')
                # if(i%20==0):
                #     print("t",time.time()-t, "i", i, "diff", (time.time()-orig_time), "fps",float(i)/(time.time()-orig_time), "readings", readings)
                # t = time.time()
                if(len(readings)>=3):
                    #print("readings",readings)
                    payload = \
                        {'message': 'updateDistanceSensorsReadings', 'readings': {
                            'L': float(readings[2])/10.0,
                            'C': float(readings[1])/10.0,
                            'R': float(readings[0])/10.0
                            }
                        }
                    if self.on_distance_update_handler is not None:
                        self.on_distance_update_handler(payload)
                #await asyncio.sleep(0.01)
            except Exception as e:
                print("update distance exception",e)
                pass

    def __process_gyro(self):
        x_offset = 4.936341463414674
        y_offset = -0.847804878048786
        z_offset = -2.32609756097562
        to_degrees_factor =  360 / 26000
        z_sum = 0.0
        while self.gyro_live:
            gyro_data = self.gyro.get_gyro_data()
            z_sum += (gyro_data['z'] - z_offset)*to_degrees_factor
            if self.on_orientation_update_handler is not None:
                #print("z_sum", z_sum)
                self.on_orientation_update_handler({'message': 'updateOrientation', 'angle': z_sum})
            time.sleep(0.01)

    def set_distance_update_handler(self, handler):
        self.on_distance_update_handler=handler

    def set_line_sensors_update_handler(self, handler):
        self.on_line_sensors_update_handler=handler

    def set_orientation_update_handler(self, handler):
        self.on_orientation_update_handler=handler
