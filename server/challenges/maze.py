import time, math

try:
    from processors.robot_processor import RobotProcessor
except:
    import sys, os

    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from processors.robot_processor import RobotProcessor

current_aliens = None

def alien_update(aliens):
    global current_aliens
    if aliens is not None and 'aliens' in aliens:
        current_aliens = aliens['aliens']

def find_first_alien_target():
    while current_aliens is None or len(current_aliens) == 0:
        time.sleep(0.05)
    print(current_aliens)
    central_alien = sorted(current_aliens,key=lambda r:math.fabs(r['xAngle']))[0]
    print(central_alien)
    return central_alien

def follow_alien(alien):
    while True:
        aliens_by_id = [a for a in current_aliens if a['id']==alien['id']]
        if aliens_by_id is None or len(aliens_by_id)<1:
            processor.drive(0,0)
            return
        if aliens_by_id[0]['distance'] < 20:
            processor.drive(0,0)
            return
        if aliens_by_id[0]['xAngle']<8 and aliens_by_id[0]['xAngle']>-8:
            processor.drive(10,10)
        elif aliens_by_id[0]['xAngle']>=8:
            processor.drive(10, 0)
        elif aliens_by_id[0]['xAngle']<=-8:
            processor.drive(-10, 0)

def turn_to_next_alien(is_left_turn, last_alien):
    while True:
        if current_aliens is not None and len(current_aliens) > 0:
            aliens_by_id = [a for a in current_aliens if a['id'] == last_alien['id']]
            max_x_angle = 1000
            min_x_angle = -1000
            if aliens_by_id is not None and len(aliens_by_id) < 1:
                if is_left_turn:
                    max_x_angle = aliens_by_id['xAngle']-1
                else:
                    min_x_angle = aliens_by_id['xAngle']+1
            if is_left_turn:
                alien_candidates = [a for a in current_aliens if a['xAngle'] <= max_x_angle]
            else:
                alien_candidates = [a for a in current_aliens if a['xAngle'] >= min_x_angle]
            if(len(alien_candidates)>0):
                next_alien = sorted(alien_candidates,key=lambda r:r['xAngle'], reverse=is_left_turn)[0]
                processor.drive(0,0)
                return next_alien
        if is_left_turn:
            processor.drive(-10, 10)
        else:
            processor.drive(10, -10)

try:
    processor = RobotProcessor()
    processor.initialise()
    processor.set_alien_update_handler(alien_update)
    processor.set_camera_mode(0)
    alien = find_first_alien_target()
    follow_alien(alien)
    for turn in [True, True, False, False, True, True, True]:
        turn_to_next_alien(turn, alien)
        follow_alien(alien)
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    processor.close()
