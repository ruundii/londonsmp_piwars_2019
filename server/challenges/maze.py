import time, math
import asyncio

try:
    from processors.robot_processor import RobotProcessor
except:
    import sys, os

    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from processors.robot_processor import RobotProcessor

current_aliens = None
current_distances = None
processor = None

def alien_update(aliens):
    global current_aliens
    if aliens is not None and 'aliens' in aliens:
        current_aliens = aliens['aliens']

def distance_update(distances):
    global current_distances
    if distances is not None and 'readings' in distances:
        current_distances = distances['readings']

async def find_first_alien_target():
    while current_aliens is None or len(current_aliens) == 0:
        await asyncio.sleep(0.05)
    central_alien = sorted(current_aliens,key=lambda r:math.fabs(r['xAngle']))[0]
    print("first alien found:",central_alien)
    return central_alien

async def follow_alien(alien):
    ultrasonic_low_distance_counter = 0
    while True:
        print("following alien", alien['id'])
        aliens_by_id = [a for a in current_aliens if a['id']==alien['id']]
        if aliens_by_id is None or len(aliens_by_id)<1:
            print("missed alien. stopping", alien)
            processor.drive(0,0)
            return
        print("updated alien details",aliens_by_id[0])
        if current_distances is not None and 'C' in current_distances:
            print("sensor distance",current_distances['C'])
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
            await asyncio.sleep(0.15)
            continue
        else:
            ultrasonic_low_distance_counter=0

        if aliens_by_id[0]['xAngle']<7 and aliens_by_id[0]['xAngle']>-7:
            print("straight angle, driving straight", aliens_by_id[0]['xAngle'])
            processor.drive(10,10)
        elif aliens_by_id[0]['xAngle']>=7:
            print("alien to the right, driving right", aliens_by_id[0]['xAngle'])
            processor.drive(20, 0)
        elif aliens_by_id[0]['xAngle']<=-7:
            print("alien to the left, driving right", aliens_by_id[0]['xAngle'])
            processor.drive(0, 20)
        await asyncio.sleep(0.001)

async def turn_to_next_alien(is_left_turn, last_alien):
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
        await asyncio.sleep(0.001)

async def main():
    try:
        global processor
        processor = RobotProcessor()
        processor.initialise()
        processor.set_alien_update_handler(alien_update)
        processor.set_distance_update_handler(distance_update)
        processor.set_camera_mode(0)
        alien = await find_first_alien_target()
        await follow_alien(alien)
        alien = await turn_to_next_alien(True, alien)
        await follow_alien(alien)
        alien = await turn_to_next_alien(True, alien)
        await follow_alien(alien)
        alien = await turn_to_next_alien(False, alien)
        await follow_alien(alien)

        # for turn in [True, True, False, False, True, True, True]:
        #     alien = await turn_to_next_alien(turn, alien)
        #     await follow_alien(alien)
        processor.close()
        await asyncio.sleep(0.5)
    except KeyboardInterrupt:
        processor.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()