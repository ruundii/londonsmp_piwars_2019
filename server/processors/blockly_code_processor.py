from _thread import start_new_thread
code_processor = None
import time

class BlocklyCodeProcessor:

    def __init__(self, robot_processor):
        global code_processor
        self.robot_processor = robot_processor
        code_processor = self
        self.stop_handler = None

    def init_handlers(self, stop_handler):
        self.stop_handler = stop_handler

    def start_run(self, code):
        global thread_stop
        thread_stop = False
        self.__init_processor_handlers(True)
        code += '\r\nrun_finished()'
        start_new_thread(self.__start_code, (code,))

    def __start_code(self, code):
        code = code.replace('time.sleep(','sleep_in_ms(')

        try:
            exec(code, {'is_thread_stopped': is_thread_stopped,
                          'sleep_in_ms': sleep_in_ms,
                          'run_finished': run_finished,
                          'robot_drive': robot_drive,
                          'robot_stop': robot_stop,
                          'robot_set_camera_mode': robot_set_camera_mode,
                          'robot_get_list_of_alien_ids': robot_get_list_of_alien_ids,
                          'robot_get_distance_to_alien': robot_get_distance_to_alien,
                          'robot_get_x_angle_to_alien': robot_get_x_angle_to_alien,
                          'robot_get_y_angle_to_alien': robot_get_y_angle_to_alien,
                          'robot_get_list_of_coloured_sheets': robot_get_list_of_coloured_sheets,
                          'robot_get_distance_to_a_coloured_sheet': robot_get_distance_to_a_coloured_sheet,
                          'robot_get_x_angle_to_a_coloured_sheet': robot_get_x_angle_to_a_coloured_sheet,
                          'robot_get_x_angle_to_a_white_line': robot_get_x_angle_to_a_white_line})
        except Exception as exc:
            print("Exception in blockly_code_processor.__start_code:", exc)
            global thread_stop
            thread_stop = True
            self.stop_run()
            if (self.stop_handler is not None):
                self.stop_handler(True)

    def stop_run(self):
        self.__init_processor_handlers(False)
        self.robot_processor.stop_run()

    def __init_processor_handlers(self, on):
        self.robot_processor.set_alien_update_handler(alien_update_handler if on else None)
        self.robot_processor.set_coloured_sheet_update_handler(coloured_sheet_update_handler if on else None)
        self.robot_processor.set_white_line_update_handler(white_line_crossings_update_handler if on else None)

    def run_finished(self):
        global thread_stop
        thread_stop=True
        self.stop_run()
        if(self.stop_handler is not None):
            self.stop_handler(False)


thread_stop = False
last_aliens = None
last_coloured_sheets = None
last_white_line_crossings = None
last_drive_params = None

def sleep_in_ms(ms):
    time.sleep(ms/1000.0)

def is_thread_stopped():
    global thread_stop
    return thread_stop

def run_finished():
    code_processor.run_finished()

def alien_update_handler(data):
    global last_aliens
    #print('alien_update_handler:',len(data['aliens']))
    last_aliens = data['aliens']

def coloured_sheet_update_handler(data):
    global last_coloured_sheets
    last_coloured_sheets = data['sheets']

def white_line_crossings_update_handler(data):
    global last_white_line_crossings
    last_white_line_crossings = data['crossings']

def robot_drive(speed_left, speed_right):
    #print('robot_drive',speed_left, speed_right)
    global last_drive_params
    if(last_drive_params is not None and last_drive_params['speed_left'] == speed_left and last_drive_params['speed_right'] == speed_right):
        return
    else:
        last_drive_params = {'speed_left':speed_left,'speed_right':speed_right}
    code_processor.robot_processor.drive(speed_left, speed_right)

def robot_stop():
    robot_drive(0,0)

def robot_set_camera_mode(mode):
    code_processor.robot_processor.set_camera_mode(mode)

def robot_get_list_of_alien_ids():
    global last_aliens
    if(last_aliens is None or len(last_aliens)==0): return [-1]
    alien_ids=[]
    for alien in last_aliens:
        alien_ids.append(alien['id'])
    return alien_ids

def robot_get_distance_to_alien(alien_id):
    global last_aliens
    if(last_aliens is None): return 0
    for alien in last_aliens:
        if alien['id']==alien_id:
            return alien['distance']
    return 0

def robot_get_x_angle_to_alien(alien_id):
    global last_aliens
    if(last_aliens is None): return 0
    for alien in last_aliens:
        if alien['id']==alien_id:
            return alien['xAngle']
    return 0

def robot_get_y_angle_to_alien(alien_id):
    global last_aliens
    if(last_aliens is None): return 0
    for alien in last_aliens:
        if alien['id']==alien_id:
            return alien['yAngle']
    return 0

def robot_get_list_of_coloured_sheets():
    global last_coloured_sheets
    if(last_coloured_sheets  is None or len(last_coloured_sheets )==0): return [-1]
    coloured_sheets=[]
    for sheet in last_coloured_sheets:
        coloured_sheets.append(sheet['colour'])
    return coloured_sheets

def robot_get_distance_to_a_coloured_sheet(colour):
    global last_coloured_sheets
    if(last_coloured_sheets is None): return 0
    for sheet in last_coloured_sheets:
        if sheet['colour']==colour:
            return sheet['distance']
    return 0

def robot_get_x_angle_to_a_coloured_sheet(colour):
    global last_coloured_sheets
    if(last_coloured_sheets is None): return 0
    for sheet in last_coloured_sheets:
        if sheet['colour']==colour:
            return sheet['xAngle']
    return 0

def robot_get_x_angle_to_a_white_line(line_number):
    global last_white_line_crossings
    if(last_white_line_crossings is None): return -1000
    return last_white_line_crossings[int(line_number)-1]['xAngle']

