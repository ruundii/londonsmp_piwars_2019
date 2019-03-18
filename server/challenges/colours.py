import time, math

try:
    from processors.robot_processor import RobotProcessor
except:
    import sys, os

    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from processors.robot_processor import RobotProcessor

current_aliens = None

def colour_update(aliens):
    pass
    # global current_aliens
    # if aliens is not None and 'aliens' in aliens:
    #     current_aliens = aliens['aliens']

try:
    processor = RobotProcessor()
    processor.initialise()
    processor.set_coloured_sheet_update_handler(colour_update)
    processor.set_camera_mode(1)
    processor.drive(-60, 60)
    time.sleep(10)
    processor.drive(0, 0)
except KeyboardInterrupt:
    processor.close()
