from asyncserial import Serial
import asyncio
import time
import os
is_raspberry = os.name != 'nt'


class SensorsProcessor:
    def __init__(self):
        self.distance_controller_live = False
        self.colour_sensors_live = False

        self.on_distance_update_handler = None
        self.on_line_sensors_update_handler = None

        self.serial_connection = None
        self.distance_thread = None

    def start_sensor(self):
        loop = asyncio.get_event_loop()
        try:
            if is_raspberry:
                self.serial_connection = Serial(loop, "/dev/ttyUSB0", baudrate=19200)
            else:
                self.serial_connection = Serial(loop, "COM3", baudrate=19200)
            self.distance_controller_live = True
        except Exception as e:
            self.distance_controller_live = False
            print("Could not open serial at /dev/ttyUSB0",e)
            return
        loop.create_task(self.__process_sensor_messages())

    def stop_sensor(self):
        self.distance_controller_live = False
        if self.serial_connection is not None:
            self.serial_connection.close()
            self.serial_connection = None

    async def __process_sensor_messages(self):
        await self.serial_connection.read()
        # i = 0
        # orig_time = time.time()
        # t = time.time()
        while self.distance_controller_live:
            # i +=1
            try:
                readings = await self.serial_connection.readline()
                readings = readings.decode().rstrip().split(',')
                # if(i%20==0):
                #     print("t",time.time()-t, "i", i, "diff", (time.time()-orig_time), "fps",float(i)/(time.time()-orig_time), "readings", readings)
                # t = time.time()
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
                #await asyncio.sleep(0.01)
            except Exception as e:
                print("update distance exception",e)
                pass

    def set_distance_update_handler(self, handler):
        self.on_distance_update_handler=handler

    def set_line_sensors_update_handler(self, handler):
        self.on_line_sensors_update_handler=handler