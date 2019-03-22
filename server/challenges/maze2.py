import time, math

try:
    from processors.robot_processor import RobotProcessor
except:
    import sys, os

    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from processors.robot_processor import RobotProcessor

current_aliens = None
current_distances = None
current_orientation = None
last_sensor_reading_timestamp = None
last_drive_params = (0,0)
processor = None
LEFT = 0
RIGHT = 1
TARGET_WALL_FOLLOWING_DISTANCE = 20
NUM_PREDICT_STEPS_AHEAD = 10
MAX_DIFFERENCE_PER_CYCLE_TO_STEER = 0.3


def alien_update(aliens):
    global current_aliens
    if aliens is not None and 'aliens' in aliens:
        current_aliens = aliens['aliens']

def distance_update(distances):
    global current_distances,last_sensor_reading_timestamp
    if distances is not None and 'readings' in distances:
        current_distances = distances['readings']
        last_sensor_reading_timestamp = time.time()
        print("t", last_sensor_reading_timestamp, "sensor distance", current_distances)

def orientation_update(orientation):
    global current_orientation
    current_orientation = orientation['angle']
    print("t", time.time(), "current_orientation", current_orientation)


def find_first_alien_target():
    while current_aliens is None or len(current_aliens) == 0:
        time.sleep(0.05)
    central_alien = sorted(current_aliens,key=lambda r:math.fabs(r['xAngle']))[0]
    print("first alien found:",central_alien)
    return central_alien

def follow_alien(alien):
    ultrasonic_low_distance_counter = 0
    while True:
        print("following alien", alien['id'])
        aliens_by_id = [a for a in current_aliens if a['id']==alien['id']]
        if aliens_by_id is None or len(aliens_by_id)<1:
            print("missed alien. stopping", alien)
            drive_robot(0,0)
            return
        print("updated alien details",aliens_by_id[0])
        if current_distances is not None and 'C' in current_distances:
            print("sensor distance",current_distances['C'])
        if aliens_by_id[0]['distance'] < 28:
            print("distance is too close. stopping", aliens_by_id[0]['distance'])
            drive_robot(0,0)
            return
        if current_distances is not None and 'C' in current_distances and current_distances['C'] < 28:
            print("ultrasonic distance is too low. stopping")
            drive_robot(0,0)
            ultrasonic_low_distance_counter+=1
            if ultrasonic_low_distance_counter >=5:
                return
            time.sleep(0.15)
            continue
        else:
            ultrasonic_low_distance_counter=0

        if aliens_by_id[0]['xAngle']<7 and aliens_by_id[0]['xAngle']>-7:
            print("straight angle, driving straight", aliens_by_id[0]['xAngle'])
            drive_robot(10,10)
        elif aliens_by_id[0]['xAngle']>=7:
            print("alien to the right, driving right", aliens_by_id[0]['xAngle'])
            drive_robot(20, 0)
        elif aliens_by_id[0]['xAngle']<=-7:
            print("alien to the left, driving right", aliens_by_id[0]['xAngle'])
            drive_robot(0, 20)
        time.sleep(0.001)

def turn_to_next_alien(is_left_turn, last_alien):
    while True:
        if current_aliens is not None and len(current_aliens) > 0:
            aliens_by_id = [a for a in current_aliens if a['id'] == last_alien['id']]
            max_x_angle = 1000
            min_x_angle = -1000
            if aliens_by_id is not None and len(aliens_by_id) > 0:
                if is_left_turn:
                    max_x_angle = aliens_by_id[0]['xAngle']-1
                else:
                    min_x_angle = aliens_by_id[0]['xAngle']+1
            if is_left_turn:
                alien_candidates = [a for a in current_aliens if a['xAngle'] <= max_x_angle]
            else:
                alien_candidates = [a for a in current_aliens if a['xAngle'] >= min_x_angle]
            if(len(alien_candidates)>0):
                next_alien = sorted(alien_candidates,key=lambda r:r['xAngle'], reverse=is_left_turn)[0]
                drive_robot(0,0)
                return next_alien
        if is_left_turn:
            drive_robot(-35, 35)
        else:
            drive_robot(35, -35)
            time.sleep(0.03)

def little_kick(period):
    drive_robot(55, 55)
    time.sleep(period)

def wait_until_next_sensor_reading():
    current_sensor_timestamp = last_sensor_reading_timestamp
    while current_sensor_timestamp+0.0001>=last_sensor_reading_timestamp:
        time.sleep(0.001)

def keep_driving_n_sensor_cycles(n):
    actual_drive_cycles = 0
    ultrasonic_low_distance_counter = 0
    for i in range(n):
        if current_distances is not None and 'C' in current_distances and current_distances['C'] < 26:
            print("ultrasonic distance is too low. stopping")
            prev_last_drive_params = last_drive_params
            drive_robot(0, 0)
            ultrasonic_low_distance_counter += 1
            if ultrasonic_low_distance_counter >= 5:
                return actual_drive_cycles, True
            wait_until_next_sensor_reading()
            continue
        ultrasonic_low_distance_counter = 0
        wait_until_next_sensor_reading()
        actual_drive_cycles+=1
    return actual_drive_cycles, False

def drive_robot(speed_left, speed_right):
    global last_drive_params
    last_drive_params = (speed_left,speed_right)
    processor.drive(speed_left,speed_right)

def drive_to_wall_ahead(follow_wall=None, forward_starting_distance = None):
    if(follow_wall is None):
        drive_robot(15, 15)
        keep_driving_n_sensor_cycles(1000)
        return
    #initial measurement of direction
    last_difference = current_distances['R' if follow_wall == RIGHT else 'L'] - TARGET_WALL_FOLLOWING_DISTANCE
    drive_robot(15, 15)
    wait_until_next_sensor_reading()
    cycles_driven, _ = keep_driving_n_sensor_cycles(7)
    low_forward_reading = False
    while True:
        if forward_starting_distance is not None:
            if current_distances['C']<forward_starting_distance:
                if low_forward_reading:
                    keep_driving_n_sensor_cycles(1000)
                    return
                else:
                    low_forward_reading = True
                    continue
            else:
                low_forward_reading = False
        current_difference = current_distances['R' if follow_wall==RIGHT else 'L']-TARGET_WALL_FOLLOWING_DISTANCE

        difference_derivative_per_cycle  = (current_difference-last_difference)/cycles_driven if cycles_driven>0 else 0
        print("current_difference", current_difference, "difference_derivative_per_cycle ", difference_derivative_per_cycle )
        few_steps_ahead_prediction = current_difference + NUM_PREDICT_STEPS_AHEAD * difference_derivative_per_cycle
        if math.fabs(few_steps_ahead_prediction)>7:
            #correct the course
            if current_difference/few_steps_ahead_prediction > 0: #same sign of current difference and prediction - not enough to recover in 4 steps, need to steer more
                steer_factor = few_steps_ahead_prediction/math.fabs(few_steps_ahead_prediction)
            else: #different sign, overshoot, need to steer reverse
                steer_factor = -few_steps_ahead_prediction/math.fabs(few_steps_ahead_prediction)
            sign_factor = steer_factor if follow_wall == RIGHT else -steer_factor
            if math.fabs(difference_derivative_per_cycle) < MAX_DIFFERENCE_PER_CYCLE_TO_STEER or difference_derivative_per_cycle/few_steps_ahead_prediction>0:
                #if difference_derivative_per_cycle is not that big or we are looking to reduce it with steer in opposite direction
                drive_robot(sign_factor*30, sign_factor*-30)
                print("t", time.time(), "steerting driving", sign_factor*30, sign_factor*-30, "for",math.fabs(few_steps_ahead_prediction)*0.007)
                time.sleep(math.fabs(few_steps_ahead_prediction)*0.007)
        #go forward and calc next derivative from sensors
        print("t", time.time(), "finished steerting driving")
        drive_robot(15, 15)
        wait_until_next_sensor_reading()
        current_difference = current_distances['R' if follow_wall==RIGHT else 'L']-TARGET_WALL_FOLLOWING_DISTANCE
        last_difference = current_difference
        cycles_driven, wall_ahead = keep_driving_n_sensor_cycles(NUM_PREDICT_STEPS_AHEAD)
        if wall_ahead:
            break



def turn(direction):
    start_orientation = current_orientation
    if direction==RIGHT:
        drive_robot(50, -50)
    else:
        drive_robot(-50, 50)

    while True:
        if direction==RIGHT and current_orientation - start_orientation < -89:
            break
        if direction==LEFT and current_orientation - start_orientation > 89:
            break
        time.sleep(0.01)

    # cycles_turning = 0
    # while True:
    #     current_side_distance = current_distances['L' if direction==RIGHT else 'R']
    #     current_front_distance = current_distances['C']
    #     side_diff = current_side_distance-TARGET_WALL_FOLLOWING_DISTANCE
    #     if(current_front_distance>50):
    #         keep_driving_n_sensor_cycles(int(cycles_turning/2.0))
    #         drive_robot(0, 0)
    #         break
    #     if direction==RIGHT:
    #         drive_robot(50, -50)
    #     else:
    #         drive_robot(-50, 50)
    #     wait_until_next_sensor_reading()
    #     cycles_turning +=1

def main():
    try:
        global processor
        processor = RobotProcessor()
        processor.initialise()
        processor.set_distance_update_handler(distance_update)
        processor.set_orientation_update_handler(orientation_update)
        while current_distances is None or current_orientation is None:
            time.sleep(0.005)
        little_kick(0.4)
        drive_to_wall_ahead(follow_wall=RIGHT)
        turn(direction=LEFT)
        drive_to_wall_ahead(follow_wall=RIGHT)
        turn(direction=LEFT)
        drive_to_wall_ahead()
        turn(direction=RIGHT)
        drive_to_wall_ahead(follow_wall=LEFT)
        turn(direction=RIGHT)
        drive_to_wall_ahead()
        turn(direction=LEFT)
        drive_to_wall_ahead(follow_wall=RIGHT)
        turn(direction=LEFT)
        drive_to_wall_ahead(follow_wall=RIGHT)
        turn(direction=LEFT)
        drive_to_wall_ahead(follow_wall=RIGHT, forward_starting_distance=70)
        turn(direction=RIGHT)
        little_kick(0.4)
        processor.close()
        time.sleep(0.5)
    except KeyboardInterrupt:
        processor.close()

if __name__ == '__main__':
    main()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()