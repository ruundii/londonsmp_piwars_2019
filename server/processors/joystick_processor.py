import pygame
from threading import Thread
import time

import config.constants_global as constants


class JoystickProcessor:

    def __init__(self, robot_processor):
        self.robot_processor = robot_processor
        self.joystickLive = False
        self.JoystickThread = None
        self.is_active = True

        #Joystick initialisation
        print('joystick init')
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
                    print('joystick init finished')
        except Exception as exc:
            print('Failed to initialise joystick')

        if self.joystickLive:
            if self.JoystickThread is None or not self.JoystickThread.isAlive():
                self.JoystickThread = Thread(target=self.processJoystick)
                self.JoystickThread.start()

    def processJoystick(self):
        while self.processJoystickCommands:
            if not self.is_active:
                time.sleep(0.5)
                continue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.processJoystickCommands = False

            left_drive = self.joystick.get_axis(constants.joystick_left_axis)

            right_drive = self.joystick.get_axis(constants.joystick_right_axis)
            self.robot_processor.drive(-round(left_drive*10)*10, -round(right_drive*10)*10)
            time.sleep(0.05)

    def set_state(self, is_active):
        self.is_active = is_active

    def close(self):
        self.processJoystickCommands = False
        self.robot_processor.close()