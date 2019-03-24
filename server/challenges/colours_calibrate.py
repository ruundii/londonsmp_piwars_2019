import time, math

try:
    from processors.robot_processor import RobotProcessor
except:
    import sys, os

    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from processors.robot_processor import RobotProcessor

current_distances = None
current_orientation = None
current_sheets = None
prev_sheets = None
last_drive_params = (0,0)
last_sensor_reading_timestamp = None
last_coloured_sheet_timestamp = None
processor = None
LEFT = 0
RIGHT = 1
ROUTE_FOLLOW_LEFT_WALL = 0
ROUTE_DIAGONAL = 1
ROUTE_FOLLOW_RIGHT_WALL = 2

def colour_sheet_update(colour_sheets):
    global current_sheets,prev_sheets,last_coloured_sheet_timestamp
    prev_sheets = current_sheets
    current_sheets = colour_sheets['sheets']
    last_coloured_sheet_timestamp = colour_sheets['frame_timestamp']

def get_sheet_x_angle(colour):
    if current_sheets is None:
        return None
    for sheet in current_sheets:
        if sheet['colour']==colour:
            return sheet['xAngle']
    if prev_sheets is None:
        return None
    for sheet in prev_sheets:
        if sheet['colour'] == colour:
            return sheet['xAngle']
    return None


def distance_update(distances):
    global current_distances,last_sensor_reading_timestamp
    if distances is not None and 'readings' in distances:
        current_distances = distances['readings']
        last_sensor_reading_timestamp = time.time()
        #   print("t", last_sensor_reading_timestamp, "sensor distance", current_distances)

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

def turn(direction, angle=88, stop=False):
    start_orientation = current_orientation
    if direction==RIGHT:
        drive_robot(70, -70)
    else:
        drive_robot(-70, 70)
    print("turn dir",direction,"angle",angle)
    while True:
        if direction==RIGHT and current_orientation - start_orientation < -angle:
            break
        if direction==LEFT and current_orientation - start_orientation > angle:
            break
        time.sleep(0.01)
    if stop:
        drive_robot(0, 0)

def wait_until_next_sensor_reading():
    current_sensor_timestamp = last_sensor_reading_timestamp
    while current_sensor_timestamp+0.0001>=last_sensor_reading_timestamp:
        time.sleep(0.001)

def wait_until_next_camera_reading():
    current_coloured_sheet_timestamp = last_coloured_sheet_timestamp
    while current_coloured_sheet_timestamp+0.0001>=last_coloured_sheet_timestamp:
        time.sleep(0.001)

def turn_until_colour(colour):
    x_angle = get_sheet_x_angle(colour)
    while x_angle is None:
        drive_robot(70, -70)
        wait_until_next_camera_reading()
        x_angle = get_sheet_x_angle(colour)
    drive_robot(0, 0)
    print("last xangle", x_angle)
    wait_until_next_camera_reading()
    x_angle = get_sheet_x_angle(colour)
    print("new xangle", x_angle)
    wait_until_next_camera_reading()
    x_angle = get_sheet_x_angle(colour)
    print("new new xangle", x_angle)
    wait_until_next_camera_reading()
    x_angle = get_sheet_x_angle(colour)
    print("new new new xangle", x_angle)
    if x_angle is None:
        turn_until_colour(colour)
    if x_angle > 0:
        turn(RIGHT, angle=x_angle, stop=True)
    else :
        turn(LEFT, angle=-x_angle, stop=True)

def get_route_type():
    while current_distances is None or current_distances['R']<=0 or current_distances['R']>=140 or current_distances['L']<=0 or current_distances['L']>=140:
        wait_until_next_sensor_reading()
    right = current_distances['R']
    left = current_distances['L']
    if right>2.5*left:
        return ROUTE_FOLLOW_LEFT_WALL
    elif left>2.5*right:
        return ROUTE_FOLLOW_RIGHT_WALL
    else:
        return ROUTE_DIAGONAL

def drive_diagonal():
    pass

def drive_by_the_to_wall(wall=RIGHT):
    pass

def main():
    try:
        visit_order = ['red', 'blue', 'yellow', 'green']
        global processor
        processor = RobotProcessor()
        processor.initialise()
        processor.set_coloured_sheet_update_handler(colour_sheet_update)
        processor.set_distance_update_handler(distance_update)
        processor.set_orientation_update_handler(orientation_update)
        processor.set_camera_mode(1)
        while current_distances is None or current_orientation is None or current_sheets is None:
            time.sleep(0.005)
        turn(direction=RIGHT)
        turn(direction=RIGHT)
        turn(direction=RIGHT)
        turn(direction=RIGHT)
        #
        # for target_colour in visit_order:
        #     turn_until_colour(target_colour)
        #     route = get_route_type()
        #     print(route)
        #     if route == ROUTE_DIAGONAL:
        #         drive_diagonal()
        #     elif route == ROUTE_FOLLOW_LEFT_WALL:
        #         drive_by_the_to_wall(wall=LEFT)
        #     else:
        #         drive_by_the_to_wall(wall=RIGHT)
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