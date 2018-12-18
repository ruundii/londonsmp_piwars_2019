import serial
from time import sleep
from processors.robot_processor_interface import RobotProcessorInterface
from threading import Thread
from collections import deque
from numpy import average

class RobotRpiProcessor(RobotProcessorInterface):
    def __init__(self):
        super(RobotRpiProcessor, self).__init__()
        self.lastDriveParams = None
        self.lastTurnParams = None

    motorControllerLive = False
    distanceSensorControllerLive = False
    colourSensorLive = False

    def connectToMotors(self, usbPath):
        try:
            print('Trying Motors '+usbPath)
            serialConnection = serial.Serial(usbPath, 19200, timeout=1,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,)
            sleep(0.7)

            serialConnection.write(b'ID\n')
            sleep(0.1)
            serialConnection.write(b'ID\n')
            sleep(0.2)
            response = serialConnection.readline().decode().rstrip()
            print(response)
            if response == "MotorsController":
                print('Found Motors ' + usbPath)
                self.MotorsSerialConnection = serialConnection
                self.motorControllerLive = True
                return True
            else:
                print('Not motors at ' + usbPath)
                serialConnection.close()
                return False
        except Exception as e:
            print('Unavailable' + usbPath, e)
            return False

    def initialise(self):
        motor_usb=-1
        if self.connectToMotors('/dev/ttyUSB0'):
            motor_usb = 0
        elif self.connectToMotors('/dev/ttyUSB1'):
            motor_usb = 1

        # if motor_usb == 0:
        #     try:
        #         print('Trying Sensor Serial Connection /dev/ttyUSB1')
        #         self.SerialConnection = serial.Serial('/dev/ttyUSB1', 19200)
        #         self.distanceSensorControllerLive = True
        #     except Exception:
        #         print('Failed Sensor Serial Connection /dev/ttyUSB1')
        # else:
        #     try:
        #         print('Trying Sensor Serial Connection /dev/ttyUSB0')
        #         self.SerialConnection = serial.Serial('/dev/ttyUSB0', 19200)
        #         self.distanceSensorControllerLive = True
        #     except Exception:
        #         print('Failed Sensor Serial Connection /dev/ttyUSB0')
        #

        print('Rpi Processor initialised')

    def close(self):
        print('Rpi Processor closed')

    def drive(self, speedLeft, speedRight):
        if not self.motorControllerLive:
            return
        if self.lastDriveParams is not None and self.lastDriveParams['speedLeft'] == speedLeft and self.lastDriveParams['speedRight'] == speedRight:
            return
        else:
            self.lastDriveParams = {'speedLeft': speedLeft, 'speedRight' :speedRight}
        if speedLeft==speedRight:
            self.MotorsSerialConnection.write(("B " + str(self.getMotorSpeed(speedLeft)) + "\n").encode())
        else:
            self.MotorsSerialConnection.write(("L "+str(self.getMotorSpeed(speedLeft))+"\n").encode())
            self.MotorsSerialConnection.write(("R " + str(self.getMotorSpeed(speedRight)) + "\n").encode())
        self.MotorsSerialConnection.flush()

    def getMotorSpeed(self, signalSpeed):
        if signalSpeed == 0:
            return 0
        elif signalSpeed <0:
            return max(-55 + signalSpeed*2, -255)
        else:
            return min(55 + signalSpeed*2, 255)

    def say(self, text, lang):
        pass

