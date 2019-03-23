import time, math

try:
    from processors.robot_processor import RobotProcessor
except:
    import sys, os

    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from processors.robot_processor import RobotProcessor

current_distances = None
current_orientation = None
last_drive_params = (0,0)
last_sensor_reading_timestamp = None
processor = None
LEFT = 0
RIGHT = 1

def distance_update(distances):
    global current_distances,last_sensor_reading_timestamp
    if distances is not None and 'readings' in distances:
        current_distances = distances['readings']
        last_sensor_reading_timestamp = time.time()
        #print("t", last_sensor_reading_timestamp, "sensor distance", current_distances)

orientation_update_num=0

def orientation_update(orientation):
    global current_orientation,orientation_update_num
    current_orientation = orientation['angle']
    orientation_update_num+=1
    if orientation_update_num %50==0: print("t", time.time(), "current_orientation", current_orientation)

def drive_robot(speed_left, speed_right):
    global last_drive_params
    last_drive_params = (speed_left,speed_right)
    processor.drive(speed_left,speed_right)

def turn(direction, stop=False):
    start_orientation = current_orientation
    if direction==RIGHT:
        drive_robot(70, -70)
    else:
        drive_robot(-70, 70)

    while True:
        if direction==RIGHT and current_orientation - start_orientation < -88:
            break
        if direction==LEFT and current_orientation - start_orientation > 88:
            break
        time.sleep(0.01)
    if stop:
        drive_robot(0, 0)

def wait_until_next_sensor_reading():
    current_sensor_timestamp = last_sensor_reading_timestamp
    while current_sensor_timestamp+0.0001>=last_sensor_reading_timestamp:
        time.sleep(0.001)

def main():
    try:
        global processor
        processor = RobotProcessor()
        processor.initialise()
        processor.set_distance_update_handler(distance_update)
        processor.set_orientation_update_handler(orientation_update)
        processor.set_camera_mode(1)
        while current_distances is None or current_orientation is None:
            time.sleep(0.005)
        turn(direction=RIGHT, stop=True)
        time.sleep(0.005)
        turn(direction=RIGHT, stop=True)
        time.sleep(0.005)
        turn(direction=RIGHT, stop=True)
        time.sleep(0.005)
        turn(direction=RIGHT, stop=True)
        time.sleep(0.005)

        # for turn in [True, True, False, False, True, True, True]:
        #     alien = await turn_to_next_alien(turn, alien)
        #     await follow_alien(alien)
        processor.close()
        time.sleep(0.5)
    except KeyboardInterrupt:
        processor.close()

if __name__ == '__main__':
    main()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()