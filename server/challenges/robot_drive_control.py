import time, math

try:
    from processors.robot_processor import RobotProcessor
    from processors.joystick_processor import JoystickProcessor
except:
    import sys, os

    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from processors.robot_processor import RobotProcessor
    from processors.joystick_processor import JoystickProcessor, MODE_CONTROL_ROBOT


def main():
    try:
        global processor
        processor = RobotProcessor()
        processor.initialise()
        joystick_processor = JoystickProcessor(processor, mode=MODE_CONTROL_ROBOT)
        print("ok")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        processor.close()

if __name__ == '__main__':
    main()