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
last_drive_params = (0,0)
last_sensor_reading_timestamp = None
processor = None
LEFT = 0
RIGHT = 1

def alien_update(aliens):
    global current_aliens
    #print("alien update")
    if aliens is not None and 'aliens' in aliens:
        current_aliens = aliens['aliens']

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

def find_next_alien_target(prev_alien=None):
    while current_aliens is None or len(current_aliens) == 0 or (prev_alien is not None and len(current_aliens)==1 and current_aliens[0]['id']<= prev_alien['id']):
        time.sleep(0.05)
    central_alien = sorted(current_aliens,key=lambda r:math.fabs(r['xAngle']))[0]
    print("first alien found:",central_alien)
    return central_alien

def follow_alien(alien):
    ultrasonic_low_distance_counter = 0
    while True:
        #print("following alien", alien['id'])
        aliens_by_id = [a for a in current_aliens if a['id']==alien['id']]
        if aliens_by_id is None or len(aliens_by_id)<1:
            print("missed alien. stopping", alien)
            processor.drive(0,0)
            return
        #print("updated alien details",aliens_by_id[0])
        #if current_distances is not None and 'C' in current_distances:
            #print("sensor distance",current_distances['C'])
        if aliens_by_id[0]['distance'] < 28:
            print("distance is too close. stopping", aliens_by_id[0]['distance'])
            processor.drive(0,0)
            return
        if current_distances is not None and 'C' in current_distances and current_distances['C'] < 28:
            print("ultrasonic distance is too low. stopping")
            processor.drive(0,0)
            ultrasonic_low_distance_counter+=1
            if ultrasonic_low_distance_counter >=5:
                return
            time.sleep(0.15)
            continue
        else:
            ultrasonic_low_distance_counter=0

        if aliens_by_id[0]['xAngle']<7 and aliens_by_id[0]['xAngle']>-7:
            #print("straight angle, driving straight", aliens_by_id[0]['xAngle'])
            processor.drive(15,15)
        elif aliens_by_id[0]['xAngle']>=7:
            #print("alien to the right, driving right", aliens_by_id[0]['xAngle'])
            processor.drive(20, 0)
        elif aliens_by_id[0]['xAngle']<=-7:
            #print("alien to the left, driving right", aliens_by_id[0]['xAngle'])
            processor.drive(0, 20)
        wait_until_next_sensor_reading()

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
                processor.drive(0,0)
                return next_alien
        if is_left_turn:
            processor.drive(-35, 35)
        else:
            processor.drive(35, -35)
        time.sleep(0.001)

def drive_robot(speed_left, speed_right):
    global last_drive_params
    last_drive_params = (speed_left,speed_right)
    processor.drive(speed_left,speed_right)

def turn(direction, stop=False):
    start_orientation = current_orientation
    if direction==RIGHT:
        drive_robot(50, -50)
    else:
        drive_robot(-50, 50)

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
        processor.set_alien_update_handler(alien_update)
        processor.set_distance_update_handler(distance_update)
        processor.set_orientation_update_handler(orientation_update)
        processor.set_camera_mode(0)
        while current_distances is None or current_orientation is None:
            time.sleep(0.005)
        alien = find_next_alien_target()
        print("first alien",alien)
        follow_alien(alien)
        for dir in [LEFT,LEFT,RIGHT,RIGHT,LEFT,LEFT,LEFT]:
            turn(direction=dir, stop=True)
            alien = find_next_alien_target(alien)
            print("next alien",alien)
            follow_alien(alien)

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