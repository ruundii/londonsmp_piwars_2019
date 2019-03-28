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
NUM_PREDICT_STEPS_AHEAD = 30
MAX_DIFFERENCE_PER_CYCLE_TO_STEER = 0.1
SPEED_FORWARD = 30
DISTANCE_TO_WALL_THRESHOLD = 33
MIN_SENSOR_READING_THRESHOLD = 16

class RobotLostExpection(Exception):
    pass

def alien_update(aliens):
    global current_aliens
    if aliens is not None and 'aliens' in aliens:
        current_aliens = aliens['aliens']

distance_update_count = 0

def distance_update(distances):
    global current_distances,last_sensor_reading_timestamp,distance_update_count
    if distances is not None and 'readings' in distances:
        distance_update_count += 1
        current_distances = distances['readings']
        last_sensor_reading_timestamp = time.time()
        #if distance_update_count % 50 == 0: print("t", last_sensor_reading_timestamp, "sensor distance", current_distances)

def orientation_update(orientation):
    global current_orientation
    current_orientation = orientation['angle']
    #print("t", time.time(), "current_orientation", current_orientation)


def find_first_alien_target():
    while current_aliens is None or len(current_aliens) == 0:
        time.sleep(0.05)
    central_alien = sorted(current_aliens,key=lambda r:math.fabs(r['xAngle']))[0]
    print("first alien found:",central_alien)
    return central_alien


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
        if current_distances is not None and 'C' in current_distances and current_distances['C'] < DISTANCE_TO_WALL_THRESHOLD:
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

def check_if_robot_is_lost(throw=True):
    if (current_distances['R'] < MIN_SENSOR_READING_THRESHOLD and current_distances['L'] < MIN_SENSOR_READING_THRESHOLD):
        wait_until_next_sensor_reading()
        if (current_distances['R'] < MIN_SENSOR_READING_THRESHOLD and current_distances['L'] < MIN_SENSOR_READING_THRESHOLD):
            drive_robot(0,0)
            if throw: raise RobotLostExpection()



def drive_to_wall_ahead(follow_wall=None):
    if(follow_wall is None):
        drive_robot(SPEED_FORWARD, SPEED_FORWARD)
        keep_driving_n_sensor_cycles(1000)
        return
    #initial measurement of direction
    last_difference = current_distances['R' if follow_wall == RIGHT else 'L'] - TARGET_WALL_FOLLOWING_DISTANCE
    drive_robot(SPEED_FORWARD, SPEED_FORWARD)
    wait_until_next_sensor_reading()
    cycles_driven, _ = keep_driving_n_sensor_cycles(int(NUM_PREDICT_STEPS_AHEAD/2))
    while True:
        check_if_robot_is_lost()
        current_difference = current_distances['R' if follow_wall==RIGHT else 'L']-TARGET_WALL_FOLLOWING_DISTANCE
        #detect sudden disappearence of the wall
        if current_difference > last_difference + 15:
            #looks suspicious
            for i in range(5):
                wait_until_next_sensor_reading()
                cycles_driven +=1
            current_difference = current_distances['R' if follow_wall == RIGHT else 'L'] - TARGET_WALL_FOLLOWING_DISTANCE
            if current_difference > last_difference + 15: #suspicion confirmed, side wall disappeared, drive to wall ahead
                keep_driving_n_sensor_cycles(1000)
                return

        difference_derivative_per_cycle  = (current_difference-last_difference)/cycles_driven if cycles_driven>10 else 0
        print("current_difference", current_difference, "difference_derivative_per_cycle ", difference_derivative_per_cycle, "R",current_distances['R'], "L",current_distances['L'] )
        few_steps_ahead_prediction = current_difference + NUM_PREDICT_STEPS_AHEAD * difference_derivative_per_cycle
        if math.fabs(few_steps_ahead_prediction)>5:
            #correct the course
            if current_difference/few_steps_ahead_prediction > 0: #same sign of current difference and prediction - not enough to recover in 4 steps, need to steer more
                steer_factor = few_steps_ahead_prediction/math.fabs(few_steps_ahead_prediction)
            else: #different sign, overshoot, need to steer reverse
                steer_factor = -few_steps_ahead_prediction/math.fabs(few_steps_ahead_prediction)
            sign_factor = steer_factor if follow_wall == RIGHT else -steer_factor
            if math.fabs(difference_derivative_per_cycle) < MAX_DIFFERENCE_PER_CYCLE_TO_STEER or difference_derivative_per_cycle/few_steps_ahead_prediction>0:
                #if difference_derivative_per_cycle is not that big or we are looking to reduce it with steer in opposite direction
                drive_robot(sign_factor*35, sign_factor*-35)
                print("t", time.time(), "steerting driving", sign_factor*35, sign_factor*-35, "for",math.fabs(few_steps_ahead_prediction)*0.007)
                time.sleep(math.fabs(few_steps_ahead_prediction)*0.005)
        #go forward and calc next derivative from sensors
        print("t", time.time(), "finished steerting driving")
        drive_robot(SPEED_FORWARD, SPEED_FORWARD)
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
        check_if_robot_is_lost()
        if direction==RIGHT:
            if current_orientation - start_orientation < -85:
                break
        if direction==LEFT:
            if current_orientation - start_orientation > 85:
                break
            time.sleep(0.01)
    drive_robot(0, 0)

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

def determine_turn_direction():
    last_result = -1
    result_in_a_row =0
    print("determine_turn_direction. R:", current_distances['R'], "L", current_distances['L'])
    while True:
        if current_distances['R'] > 55 and current_distances['L']>55:
            if last_result == 1:
                if result_in_a_row == 5:
                    return RIGHT, LEFT, True
                result_in_a_row+=1
            else:
                last_result = 1
                result_in_a_row = 1
        elif current_distances['R'] < current_distances['L']:
            if last_result == 2:
                if result_in_a_row == 5:
                    return LEFT, RIGHT, False
                result_in_a_row+=1
            else:
                last_result = 2
                result_in_a_row = 1
        else:
            if last_result == 3:
                if result_in_a_row == 5:
                    return RIGHT, LEFT, False
                result_in_a_row+=1
            else:
                last_result = 3
                result_in_a_row = 1
        wait_until_next_sensor_reading()

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
        follow_wall = RIGHT
        while True:
            try:
                drive_to_wall_ahead(follow_wall=follow_wall)
                turn_direction, follow_wall, is_last_turn = determine_turn_direction()
                print("turn_direction",turn_direction, "follow_wall",follow_wall, "is_last_turn",is_last_turn)
                turn(direction=turn_direction)
            except RobotLostExpection:
                print("Robot lost")
                while check_if_robot_is_lost(throw=False):
                    time.sleep(0.1)
                print("Robot recovery")
            if is_last_turn:
                little_kick(0.6)
                break
        processor.close()
        time.sleep(0.5)
    except KeyboardInterrupt:
        processor.close()

if __name__ == '__main__':
    main()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()