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
last_sensor_reading_timestamp_original = None
processor = None
LEFT = 0
RIGHT = 1
ROUTE_FOLLOW_LEFT_WALL = 0
ROUTE_DIAGONAL = 1
ROUTE_FOLLOW_RIGHT_WALL = 2
TARGET_WALL_FOLLOWING_DISTANCE = 15

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
    global current_distances,last_sensor_reading_timestamp,last_sensor_reading_timestamp_original
    if distances is not None and 'readings' in distances:
        current_distances = distances['readings']
        last_sensor_reading_timestamp = time.time()
        last_sensor_reading_timestamp_original = distances['ts']
        #print("t", last_sensor_reading_timestamp, last_sensor_reading_timestamp - processor.camera_processor.camera_mode_set_time if processor.camera_processor.camera_mode_set_time is not None else 0, "sensor distance", current_distances)

orientation_update_num=0

def orientation_update(orientation):
    global current_orientation,orientation_update_num
    current_orientation = orientation['angle']
    orientation_update_num+=1
    #if orientation_update_num %50==0: print("t", time.time(), "current_orientation", current_orientation)

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
        drive_robot(60, -60)
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
        return
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

# def drive_diagonal():
#     drive_robot(15, 15)
#     loop_number = 0
#     last_turn_loop_number = -10
#     while current_distances['C'] > 24:
#         loop_number+=1
#         if last_turn_loop_number<loop_number-10 and (current_distances['L'] > current_distances['R']*1.3):
#             drive_robot(0, 0)
#             wait_until_next_sensor_reading()
#             if(current_distances['L'] > current_distances['R']*1.3):
#                 #turn left
#                 turn(direction=LEFT, angle=2, stop=True)
#                 last_turn_loop_number = loop_number
#         if last_turn_loop_number<loop_number-10 and (current_distances['R'] > current_distances['L']*1.3):
#             drive_robot(0, 0)
#             wait_until_next_sensor_reading()
#             if(current_distances['R'] > current_distances['L']*1.3):
#                 #turn left
#                 turn(direction=RIGHT, angle=2, stop=True)
#                 last_turn_loop_number = loop_number
#         if (current_distances['C']>40):
#             drive_robot(15, 15)
#         elif (current_distances['C']>30):
#             drive_robot(6, 6)
#         else:
#             drive_robot(2, 2)
#         wait_until_next_sensor_reading()
#     drive_robot(0, 0)
#     #print("t", time.time() - processor.camera_processor.camera_mode_set_time if processor.camera_processor.camera_mode_set_time is not None else 0 ,"stoppp",current_distances['C'])
#     last_turn_loop_number =0
#     loop_number =0
#     while True:
#         loop_number+=1
#         for i in range (4):
#             wait_until_next_sensor_reading()
#             # if last_sensor_reading_timestamp_original is not None:
#             #     print("after stoppp", current_distances['C'], time.time() - processor.camera_processor.camera_mode_set_time if processor.camera_processor.camera_mode_set_time is not None else 0, time.time()-last_sensor_reading_timestamp_original)
#             # else:
#             #     print("after stoppp", current_distances['C'],
#             #           time.time() - processor.camera_processor.camera_mode_set_time if processor.camera_processor.camera_mode_set_time is not None else 0)
#         if last_turn_loop_number<loop_number-3 and (current_distances['L'] > current_distances['R']*1.3):
#             drive_robot(0, 0)
#             wait_until_next_sensor_reading()
#             if(current_distances['L'] > current_distances['R']*1.3):
#                 #turn left
#                 turn(direction=LEFT, angle=3, stop=True)
#                 last_turn_loop_number = loop_number
#         if last_turn_loop_number<loop_number-3 and (current_distances['R'] > current_distances['L']*1.3):
#             drive_robot(0, 0)
#             wait_until_next_sensor_reading()
#             if(current_distances['R'] > current_distances['L']*1.3):
#                 #turn left
#                 turn(direction=RIGHT, angle=3, stop=True)
#                 last_turn_loop_number = loop_number
#         if current_distances['C'] > 12:
#             drive_robot(10, 10)
#             time.sleep(0.05*min((current_distances['C']-11),5))
#             drive_robot(0, 0)
#         else:
#             break

def drive_diagonal(colour):
    drive_robot(15, 15)
    loop_number = 0
    last_turn_loop_number = -20
    sheet_time_stamp = last_coloured_sheet_timestamp
    while current_distances['C'] > 27:
        loop_number+=1
        if current_distances['C']>27 and last_coloured_sheet_timestamp>sheet_time_stamp and last_turn_loop_number<loop_number-20:
            sheet_time_stamp = last_coloured_sheet_timestamp
            x_angle = get_sheet_x_angle(colour)
            if x_angle is None:
                turn_until_colour(colour)
            else:
                if math.fabs(x_angle) > 3:
                    turn(RIGHT if x_angle>0 else LEFT, angle=math.fabs(x_angle)-3, stop=True)
                    last_turn_loop_number = loop_number
        if (current_distances['C']>40):
            drive_robot(15, 15)
        elif (current_distances['C']>30):
            drive_robot(10, 10)
        else:
            drive_robot(3, 3)
        wait_until_next_sensor_reading()
    drive_robot(0, 0)
    #print("t", time.time() - processor.camera_processor.camera_mode_set_time if processor.camera_processor.camera_mode_set_time is not None else 0 ,"stoppp",current_distances['C'])
    while True:
        for i in range (4):
            wait_until_next_sensor_reading()
            # if last_sensor_reading_timestamp_original is not None:
            #     print("after stoppp", current_distances['C'], time.time() - processor.camera_processor.camera_mode_set_time if processor.camera_processor.camera_mode_set_time is not None else 0, time.time()-last_sensor_reading_timestamp_original)
            # else:
            #     print("after stoppp", current_distances['C'],
            #           time.time() - processor.camera_processor.camera_mode_set_time if processor.camera_processor.camera_mode_set_time is not None else 0)
        if current_distances['C'] > 15:
            drive_robot(10, 10)
            time.sleep(0.04*min((current_distances['C']-12),5))
            drive_robot(0, 0)
        else:
            break

# def drive_by_the_to_wall(follow_wall=RIGHT):
#     #initial measurement of direction
#     last_difference = current_distances['R' if follow_wall == RIGHT else 'L'] - TARGET_WALL_FOLLOWING_DISTANCE
#     drive_robot(15, 15)
#     wait_until_next_sensor_reading()
#     cycles_driven, _ = keep_driving_n_sensor_cycles(7)
#     low_forward_reading = False
#     while True:
#         if forward_starting_distance is not None:
#             if current_distances['C']<forward_starting_distance:
#                 if low_forward_reading:
#                     keep_driving_n_sensor_cycles(1000)
#                     return
#                 else:
#                     low_forward_reading = True
#                     continue
#             else:
#                 low_forward_reading = False
#         current_difference = current_distances['R' if follow_wall==RIGHT else 'L']-TARGET_WALL_FOLLOWING_DISTANCE
#
#         difference_derivative_per_cycle  = (current_difference-last_difference)/cycles_driven if cycles_driven>0 else 0
#         print("current_difference", current_difference, "difference_derivative_per_cycle ", difference_derivative_per_cycle )
#         few_steps_ahead_prediction = current_difference + NUM_PREDICT_STEPS_AHEAD * difference_derivative_per_cycle
#         if math.fabs(few_steps_ahead_prediction)>7:
#             #correct the course
#             if current_difference/few_steps_ahead_prediction > 0: #same sign of current difference and prediction - not enough to recover in 4 steps, need to steer more
#                 steer_factor = few_steps_ahead_prediction/math.fabs(few_steps_ahead_prediction)
#             else: #different sign, overshoot, need to steer reverse
#                 steer_factor = -few_steps_ahead_prediction/math.fabs(few_steps_ahead_prediction)
#             sign_factor = steer_factor if follow_wall == RIGHT else -steer_factor
#             if math.fabs(difference_derivative_per_cycle) < MAX_DIFFERENCE_PER_CYCLE_TO_STEER or difference_derivative_per_cycle/few_steps_ahead_prediction>0:
#                 #if difference_derivative_per_cycle is not that big or we are looking to reduce it with steer in opposite direction
#                 drive_robot(sign_factor*30, sign_factor*-30)
#                 print("t", time.time(), "steerting driving", sign_factor*30, sign_factor*-30, "for",math.fabs(few_steps_ahead_prediction)*0.007)
#                 time.sleep(math.fabs(few_steps_ahead_prediction)*0.007)
#         #go forward and calc next derivative from sensors
#         print("t", time.time(), "finished steerting driving")
#         drive_robot(15, 15)
#         wait_until_next_sensor_reading()
#         current_difference = current_distances['R' if follow_wall==RIGHT else 'L']-TARGET_WALL_FOLLOWING_DISTANCE
#         last_difference = current_difference
#         cycles_driven, wall_ahead = keep_driving_n_sensor_cycles(NUM_PREDICT_STEPS_AHEAD)
#         if wall_ahead:
#             break

def reverse():
    drive_robot(-15,-15)
    while True:
        wait_until_next_sensor_reading()
        if current_distances['C'] > 30:
            drive_robot(0,0)
            indeed_far = True
            for i in range(7):
                wait_until_next_sensor_reading()
                if current_distances['C'] < 40:
                    indeed_far = False
                    break
            if indeed_far:
                return
            else:
                drive_robot(-15, -15)


def main():
    try:
        visit_order = ['red', 'blue', 'yellow', 'green']
        global processor
        processor = RobotProcessor()
        processor.initialise()
        processor.set_camera_mode(1)
        processor.set_coloured_sheet_update_handler(colour_sheet_update)
        processor.set_distance_update_handler(distance_update)
        processor.set_orientation_update_handler(orientation_update)
        while current_distances is None or current_orientation is None or current_sheets is None:
            print("Waiting for sensor data")
            time.sleep(0.5)
        input("Ready to go. Press Enter to start")

        for target_colour in visit_order:
            turn_until_colour(target_colour)
            time.sleep(0.2)
            drive_diagonal(target_colour)
            reverse()
            # route = get_route_type()
            # if route == ROUTE_DIAGONAL:
            #     drive_diagonal()
            #     break
            # elif route == ROUTE_FOLLOW_LEFT_WALL:
            #     drive_by_the_to_wall(wall=LEFT)
            # else:
            #     drive_by_the_to_wall(wall=RIGHT)
        drive_robot(0,0)
        time.sleep(0.5)
        processor.close()
        time.sleep(0.5)
    except KeyboardInterrupt:
        processor.close()

if __name__ == '__main__':
    main()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()