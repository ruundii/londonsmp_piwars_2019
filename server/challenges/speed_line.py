import time, math

try:
    from processors.robot_processor import RobotProcessor
except:
    import sys, os

    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from processors.robot_processor import RobotProcessor

current_orientation = None
current_vector = None
last_line_timestamp = None
orientation_update_num=0


def white_line_update(line):
    global current_vector,last_line_timestamp
    current_vector = line['vector'] if 'vector' in line else None
    last_line_timestamp = line['frame_timestamp']

def orientation_update(orientation):
    global current_orientation,orientation_update_num
    current_orientation = orientation['angle']
    orientation_update_num+=1
    if orientation_update_num %50==0: print("t", time.time(), "current_orientation", current_orientation)

def drive_robot(speed_left, speed_right):
    global last_drive_params
    last_drive_params = (speed_left,speed_right)
    processor.drive(speed_left,speed_right)

def wait_until_next_camera_reading():
    current_camera_timestamp = last_line_timestamp
    while current_camera_timestamp +0.0001>=last_line_timestamp:
        time.sleep(0.001)


def get_direction_offset():
    if current_vector is None or current_vector[0] ==-1000:
        return 0
    if current_vector[0] > -17 and current_vector[0] < 17:
        return 0.3 * current_vector[0] + 0.7*current_vector[1]
    else:
        return 0.7 * current_vector[0] + 0.3*current_vector[1]

def turn(angle):
    start_orientation = current_orientation
    print("turn - near",current_vector[0]," far",current_vector[1], " angle",angle)
    angle = angle/2
    if angle>0:
        drive_robot(50, -50)
    else:
        drive_robot(-50, 50)
    print("t", time.time(), "ts", time.time()- processor.camera_processor.camera_mode_set_time if processor.camera_processor.camera_mode_set_time is not None else 0, "turn angle",angle)
    while True:
        if angle>0 and current_orientation - start_orientation < -angle + 2:
            break
        if angle<0 and current_orientation - start_orientation > -angle -2:
            break
        time.sleep(0.01)

def main():
    try:
        global processor
        processor = RobotProcessor()
        processor.initialise()
        processor.set_white_line_update_handler(white_line_update)
        processor.set_orientation_update_handler(orientation_update)
        processor.set_camera_mode(2)
        while current_orientation is None or current_vector is None:
            print("Waiting for sensor data")
            time.sleep(0.5)
        input("Ready to go. Press Enter to start")
        while True:
            offset = get_direction_offset()
            if offset <10 and offset>-10:
                drive_robot(20,20)
            else:
                turn(offset)
                drive_robot(35, 35)
                wait_until_next_camera_reading()
                wait_until_next_camera_reading()
                # wait_until_next_camera_reading()
                # wait_until_next_camera_reading()
                #drive_robot(10+1.5*offset,10-1.5*offset)
            time.sleep(0.001)
        drive_robot(0,0)
        processor.close()
        time.sleep(0.5)
    except KeyboardInterrupt:
        processor.close()

if __name__ == '__main__':
    main()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()