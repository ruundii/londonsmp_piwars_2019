import pygame
from _thread import start_new_thread
import time
import serial

import config.constants_global as constants

BUTTON_A=0
BUTTON_B=1
BUTTON_X=2
BUTTON_Y=3
BUTTON_L=4
BUTTON_R=5

MODE_CONTROL_ROBOT = 0
MODE_PROCESS_BUTTONS = 1

class JoystickProcessor:

    def __init__(self, robot_processor, mode=MODE_CONTROL_ROBOT):
        self.robot_processor = robot_processor
        self.joystick_live = False
        self.joystick_thread = None
        self.is_active = True
        self.speed_gear = 0.3
        self.pressed_buttons = {BUTTON_A:False,BUTTON_B:False,BUTTON_X:False,BUTTON_Y:False}
        try:
            self.serial_connection = serial.Serial("/dev/ttyUSB0", 9600, timeout=1, parity=serial.PARITY_NONE,
                                             stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, )
            self.serial_present = True
        except:
            self.serial_present = False
            print("no serial found at /dev/ttyUSB0")
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
                    self.joystick_live = True
                    self.process_joystick_commands = True
                    print('joystick init finished')
        except Exception as exc:
            print('Failed to initialise joystick')

        if self.joystick_live:
            if self.joystick_thread is None or not self.joystick_thread.isAlive():
                if mode == MODE_CONTROL_ROBOT:
                    self.joystick_thread = start_new_thread(self.process_joystick_robot_control,())
                else:
                    self.joystick_thread = start_new_thread(self.process_joystick_buttons,())

    def speed_control(self, increase=True):  # Speed control
        if(increase):
            self.speed_gear += 0.3
            if(self.speed_gear>=0.9): self.speed_gear=0.9
        else:
            self.speed_gear -= 0.3
            if(self.speed_gear<=0.3): self.speed_gear=0.3

    def process_joystick_robot_control(self):
        while self.process_joystick_commands:
            if not self.is_active:
                time.sleep(0.5)
                continue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.process_joystick_commands = False

                if self.serial_present and self.joystick.get_button(BUTTON_B):
                    print("B pressed")
                    self.serial_connection.write("1".encode())
                    self.serial_connection.flush()

                if self.joystick.get_button(BUTTON_L):
                    self.speed_control(True)
                    print("Speed UP. Gear: {}.".format(self.speed_gear))

                if self.joystick.get_button(BUTTON_R):
                    self.speed_control(False)
                    print("Speed DOWN. Gear: {}.".format(self.speed_gear))

            left_drive = self.joystick.get_axis(constants.joystick_left_axis)*self.speed_gear

            right_drive = self.joystick.get_axis(constants.joystick_right_axis)*self.speed_gear

            self.robot_processor.drive(-round(left_drive*10)*10, -round(right_drive*10)*10)
            time.sleep(0.01)

    def process_joystick_buttons(self):
        while self.process_joystick_commands:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.process_joystick_commands = False
                for i in [BUTTON_A,BUTTON_B,BUTTON_X,BUTTON_Y]:
                    if self.joystick.get_button(i):
                        self.pressed_buttons[i]=True
                        print(i," pressed")
            time.sleep(0.01)

    def set_state(self, is_active):
        self.is_active = is_active

    def wait_till_button(self, button):
        for i in [BUTTON_A, BUTTON_B, BUTTON_X, BUTTON_Y]:
            self.pressed_buttons[i] = False
        while True:
            if self.pressed_buttons[button]:
                self.pressed_buttons[button] = False
                print(i, " received")
                return
            time.sleep(0.01)

    def close(self):
        self.process_joystick_commands = False
        if self.serial_present: self.serial_connection.close()
        self.robot_processor.close()