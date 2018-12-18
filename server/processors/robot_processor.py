from processors.robot_processor_interface import RobotProcessorInterface
import cv2
from videoutils.robotcamera import RobotCamera
from threading import Thread
import math
import time
from videoutils.fps import FPS
from gtts import gTTS
import re
import hashlib
import os
import pygame
import platform

isWindows = platform.system() == 'Windows'

if isWindows:
    from videoutils import constantsWindows as c
    from processors.robot_stub_processor import RobotStubProcessor as RobotPlatformProcessor
else:
    from videoutils import constantsPi as c
    from processors.robot_rpi_processor import RobotRpiProcessor as RobotPlatformProcessor

class RobotProcessor(RobotProcessorInterface):
    processor = None

    def __init__(self):
        super(RobotProcessorInterface,self).__init__()
        self.onMarkerUpdateHandler = None

        self.processor = RobotPlatformProcessor()
        self.MarkersThread = None
        self.Camera = None
        self.cameraLive = False
        self.sendCameraUpdates = False
        self.FPS = FPS()
        self.isSimulation = False
        self.joystickLive = False
        self.processJoystickCommands= False
        self.JoystickThread = None



    def initialise(self):
        self.processor.initialise()
        #Camera initialisation
        try:
            self.Camera = RobotCamera()
            self.Camera.load(c.calibrationsPath, loadCameraMatrix=True, loadPerspective=False, loadHeight=False)
            print('loaded camera params')
            self.Camera.start();
            time.sleep(0.3)
            self.cameraLive = True
        except Exception as exc:
            print('Failed to initialise camera '+exc)
        if self.cameraLive:
            self.sendCameraUpdates = True
            if self.MarkersThread is None or not self.MarkersThread.isAlive():
                self.MarkersThread = Thread(target=self.updateMarkers)
                self.MarkersThread.start()

        #Joystick initialisation
        try:
            pygame.init()
            joystick_count = pygame.joystick.get_count()
            if joystick_count == 0:
                # No joysticks!
                print("No joystick found.")
            else:
                # Use joystick #0 and initialize it
                jst = pygame.joystick.Joystick(0)
                jst.init()
                if jst.get_init()==1:
                    self.joystick = jst
                    self.joystickLive = True
                    self.processJoystickCommands = True
        except Exception as exc:
            print('Failed to initialise joystick')

        if self.joystickLive:
            if self.JoystickThread is None or not self.JoystickThread.isAlive():
                self.JoystickThread = Thread(target=self.processJoystick)
                self.JoystickThread.start()


    def close(self):
        self.processor.close()
        self.sendCameraUpdates = False
        self.processJoystickCommands = False
        if self.cameraLive:
            self.Camera.stop()

    def drive(self, speedLeft, speedRight):
        if not self.isSimulation:
            self.processor.drive(speedLeft, speedRight)

    def onMarkerUpdate(self, handler):
        self.onMarkerUpdateHandler = handler

    def processJoystick(self):
        while self.processJoystickCommands:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.processJoystickCommands = False

            left_drive = self.joystick.get_axis(1)
            right_drive = self.joystick.get_axis(3)
            self.processor.drive(-round(left_drive*10), -round(right_drive*10))
            time.sleep(0.05)

    def updateMarkers(self):
        while self.sendCameraUpdates:
            time.sleep(0.1)
            payload = {'message': 'updateMarkerReadings', 'markers': []}

            try:
                if self.isSimulation:
                    if simulatedArucoMarkers is not None and len(simulatedArucoMarkers)>0:
                        payload['markers'] = simulatedArucoMarkers
                else:
                    self.Camera.update()
                    _, fps, frameNum = self.FPS.update()
                    #print("Update markers FPS:"+str(fps)+" frame number:"+str(frameNum)+" datetime:"+ str(datetime.now()))
                    markerCorners, markerIds = self.Camera.detectAruco()
                    if markerIds is not None and len(markerIds) > 0:
                        for id in markerIds[0]:
                            # rotation vectors, translation vectors, object points for all marker corners
                            poseRes = cv2.aruco.estimatePoseSingleMarkers(markerCorners, c.markerSizeM, self.Camera.cameraMatrix,
                                                                          self.Camera.distCoeffs)
                            x = poseRes[1][0][0][0]
                            y = poseRes[1][0][0][1]
                            z = poseRes[1][0][0][2]
                            r = math.sqrt(x ** 2 + y ** 2 + z ** 2)
                            xAngle = math.asin(x / r) * 180 / math.pi
                            yAngle = math.asin(y / r) * 180 / math.pi
                            payload['markers'].append({'id':int(id), 'distance':int(r*100), 'xAngle':int(xAngle), 'yAngle':int(yAngle)})
                if self.onMarkerUpdateHandler:
                    self.onMarkerUpdateHandler(payload)
            except Exception as exc:
                print(exc)
                pass

    def say(self, text, lang):
        try:
            if lang is None or lang=="":
                lang = "en-gb"
            chars = "".join(re.findall("[a-z]+", text.lower()))
            filename = os.path.join("sounds",chars[:20] + str(hashlib.md5(text.encode()).hexdigest())+lang+".mp3")
            if not os.path.exists(filename):
                tts = gTTS(text, lang=lang)
                tts.save(filename)

            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

        except Exception as exc:
            print("Exception in say:"+str(exc))

    def displayText(self, text, lines):
        self.processor.displayText(text, lines)

