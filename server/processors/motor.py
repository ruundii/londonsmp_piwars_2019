################################################
# Class for motor using XY-160D motor shield
################################################

import RPi.GPIO as GPIO
# from time import sleep
# import curses

class Motor:

    last_drive_params = None

    # correct pin settings on 24.12.2018 for XY-160D
    # in1 = 27
    # in2 = 22
    # en1 = 16
    # in3 = 17
    # in4 = 4
    # en2 = 19

    def __init__(self, motor_left_in1 = 27, motor_left_in2 = 22, motor_left_en = 16,
                 motor_right_in1 = 17, motor_right_in2 = 4, motor_right_en = 19):
        GPIO.setmode(GPIO.BCM)
        #
        GPIO.setup(motor_left_in1, GPIO.OUT)
        GPIO.setup(motor_left_in2, GPIO.OUT)
        GPIO.setup(motor_left_en, GPIO.OUT)
        #
        GPIO.setup(motor_right_in1, GPIO.OUT)
        GPIO.setup(motor_right_in2, GPIO.OUT)
        GPIO.setup(motor_right_en, GPIO.OUT)
        #
        self.motor_left = {'pwm': GPIO.PWM(motor_left_en, 1000),
                           'in1': motor_left_in1,
                           'in2': motor_left_in2}

        self.motor_right = {'pwm': GPIO.PWM(motor_right_en, 1000),
                           'in1': motor_right_in1,
                           'in2': motor_right_in2}

        self.motor_left['pwm'].start(25)
        self.motor_right['pwm'].start(25)


    def drive(self, speed_left, speed_right):
        #convert speed to pwm
        speed_left=self.__get_pwm_from_motor_speed(speed_left)
        speed_right = self.__get_pwm_from_motor_speed(speed_right)

        #check if nothing has changed since the last call
        if self.last_drive_params is not None and self.last_drive_params['speed_left'] == speed_left \
                and self.last_drive_params['speed_right'] == speed_right:
            return
        else:
            self.__drive_single_motor(speed_left,
                                    0 if self.last_drive_params is None else self.last_drive_params['speed_left'], self.motor_left)
            self.__drive_single_motor(speed_right,
                                    0 if self.last_drive_params is None else self.last_drive_params['speed_right'],
                                    self.motor_right)
            self.last_drive_params = {'speed_left': speed_left, 'speed_right' :speed_right}


    def __drive_single_motor(self, set_pwm, last_pwm, motor):
        if (set_pwm * last_pwm <0 or set_pwm == 0):
            #direction has changed or motor stopped. change PWM via stop
            GPIO.output(motor['in1'], GPIO.LOW)
            GPIO.output(motor['in2'], GPIO.LOW)
        motor['pwm'].ChangeDutyCycle(abs(set_pwm))
        if (set_pwm * last_pwm <=0 and set_pwm != 0):
            #direction has changed or motor started - setting in1 or in2 high
            if(set_pwm > 0):
                #drive forward
                GPIO.output(motor['in1'], GPIO.HIGH)
            elif(set_pwm < 0):
                #drive backward
                GPIO.output(motor['in2'], GPIO.HIGH)

    def __get_pwm_from_motor_speed(self, speed):
        if speed == 0:
            return 0
        elif speed <0:
            return max(-20 + speed*0.8, -100)
        else:
            return min(20 + speed*0.8, 100)


    def cleanup(self):
        GPIO.cleanup()

    def __del__(self):
        GPIO.cleanup()
