import time, math

try:
    from processors.robot_processor import RobotProcessor
except:
    import sys, os

    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from processors.robot_processor import RobotProcessor

current_aliens = None
current_distances = None
last_sensor_reading_timestamp = None
last_drive_params = (0,0)
processor = None
LEFT = 0
RIGHT = 1
TARGET_WALL_FOLLOWING_DISTANCE = 20

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

def little_kick():
    drive_robot(55, 55)
    time.sleep(0.4)

def wait_until_next_sensor_reading():
    current_sensor_timestamp = last_sensor_reading_timestamp
    while current_sensor_timestamp+0.0001>=last_sensor_reading_timestamp:
        time.sleep(0.001)

def keep_driving_n_sensor_cycles(n):
    actual_drive_cycles = 0
    ultrasonic_low_distance_counter = 0
    for i in range(n):
        if current_distances is not None and 'C' in current_distances and current_distances['C'] < 28:
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

def drive_to_wall_ahead(follow_wall=RIGHT):
    last_difference = None
    while True:
        #use pd control to follow the wall
        if current_distances is None or (follow_wall == RIGHT and 'R' not in current_distances) or (follow_wall == LEFT and 'L' not in current_distances):
            drive_robot(0, 0)
            wait_until_next_sensor_reading()
            continue

        current_difference = current_distances['R' if follow_wall==RIGHT else 'L']-TARGET_WALL_FOLLOWING_DISTANCE

        difference_derivative  = 0 if last_difference is None else current_difference-last_difference
        print("current_difference", current_difference, "difference_derivative", difference_derivative)
        if math.fabs(current_difference)>5 or difference_derivative>2:
            few_steps_ahead_prediction = current_difference+10*difference_derivative
            if math.fabs(few_steps_ahead_prediction)>3:
                if current_difference/few_steps_ahead_prediction > 0: #same sign of current difference and prediction - not enough to recover in 4 steps, need to steer more
                    steer_factor = 1
                else: #different sign, overshoot, need to steer reverse
                    steer_factor = -1
            #correct the course
            sign_factor = steer_factor if follow_wall == RIGHT else -steer_factor
            drive_robot(sign_factor*20, sign_factor*-20)
            print("t", time.time(), "steerting driving", sign_factor*20, sign_factor*-20)
            time.sleep(math.fabs(few_steps_ahead_prediction)*0.01)
        #go forward and calc next derivative from sensors
        print("finished steerting driving")
        drive_robot(20, 20)
        last_difference = current_difference
        time.sleep(0.3)
        # #wait until next sensor signal comes in
        # while current_sensor_timestamp+0.0001>=last_sensor_reading_timestamp:
        #     await asyncio.sleep(0.001)
        # print("got next reading", time.time())
        # current_sensor_timestamp=last_sensor_reading_timestamp
        # if current_distances is None or (follow_wall == RIGHT and 'R' not in current_distances) or (follow_wall == LEFT and 'L' not in current_distances):
        #     drive_robot(0, 0)
        #     await asyncio.sleep(0.01)
        #     continue
        # else:
        #     last_difference = current_distances['R' if follow_wall==RIGHT else 'L']-TARGET_WALL_FOLLOWING_DISTANCE
        #     print("last_difference after steering", last_difference)
        # while current_sensor_timestamp+0.0001>=last_sensor_reading_timestamp:
        #     await asyncio.sleep(0.001)
        # print("got further next reading", time.time())


def main():
    try:
        global processor
        processor = RobotProcessor()
        processor.initialise()
        processor.set_distance_update_handler(distance_update)
        while current_distances is None:
            time.sleep(0.005)
        #little_kick()
        drive_to_wall_ahead(follow_wall=RIGHT)
        processor.close()
        time.sleep(0.5)
    except KeyboardInterrupt:
        processor.close()

if __name__ == '__main__':
    main()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()