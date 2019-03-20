import time
from videoutils.robot_camera import RobotCamera
from videoutils.fps import FPS
import config.constants_global as constants
import cv2
import json
import videoutils.image_display as display
from multiprocessing import Process, Pipe
import asyncio

CAMERA_MODE_OFF = -1
CAMERA_MODE_DETECT_ALIENS = 0
CAMERA_MODE_DETECT_COLOURED_SHEETS = 1
CAMERA_MODE_DETECT_WHITE_LINE_TRACK = 2

import os
havedisplay = "DISPLAY" in os.environ or os.name == 'nt'
display.image_display.set_mode(havedisplay)

def init_camera_subprocess(pipe, camera_mode):
    camera_process_controller = CameraProcessController(pipe, camera_mode)
    camera_process_controller.run_camera_processing_loop()
    pipe.close()

class CameraProcessController():
    def __init__(self, pipe, camera_mode):
        self.camera = None
        self.is_camera_live = False
        self.keep_camera_processing = False
        self.fps = FPS()
        self.camera_mode = camera_mode
        self.last_drive_params = (0,0)
        self.start_time = time.time()
        self.client_server_time_difference = 0
        self.video_writer = None
        self.parent_process_pipe = pipe

        with open(constants.regions_config_name) as json_config_file:
            self.regions_config = json.load(json_config_file)

        if (camera_mode == CAMERA_MODE_DETECT_ALIENS):
            self.camera_settings = constants.camera_settings_aliens
            self.region_of_interest = self.__get_region_of_interest(self.regions_config["labyrinth"])
            self.prepare_hsv=True
            self.prepare_gray = False
        elif (camera_mode == CAMERA_MODE_DETECT_COLOURED_SHEETS):
            self.camera_settings = constants.camera_settings_coloured_sheet
            self.region_of_interest = self.__get_region_of_interest(self.regions_config["colour_sheets"])
            self.prepare_hsv=True
            self.prepare_gray = False
        elif (camera_mode == CAMERA_MODE_DETECT_WHITE_LINE_TRACK):
            self.camera_settings = constants.camera_settings_speed_track
            self.region_of_interest = self.__get_region_of_interest(self.regions_config["speed_line"])
            self.prepare_hsv=False
            self.prepare_gray = True
        print("CameraProcessController init finished")

    def run_camera_processing_loop(self):
        # Camera initialisation
        try:
            self.camera = RobotCamera(self.camera_settings, self.region_of_interest, self.prepare_gray, self.prepare_hsv)
            self.camera.load()
            self.camera.start()
            time.sleep(0.3)
            self.is_camera_live = True
        except Exception as exc:
            print('Exception in camera_processor.__start_camera: Failed to initialise camera ' + str(exc))
        if self.is_camera_live:
            self.keep_camera_processing = True
            if constants.image_processing_tracing_record_video:
                self.start_time = time.time()
                video_path = constants.video_log_folder_path + 'video_trace' + time.strftime(
                    "%Y-%m-%d_%H-%M-%S") + '.avi'
                self.video_writer = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'MJPG'), 4,
                                                    self.camera.actual_resolution)

            print('Camera started')
            got_first_image=False
            while self.keep_camera_processing:
                if not got_first_image:
                    if not self.camera.is_image_ready(self.prepare_hsv, self.prepare_gray):
                        time.sleep(0.05)
                        continue
                    else:
                       got_first_image = True
                self.__process_next_frame()
                self.__process_pipe_message()
        time.sleep(0.3)
        if self.is_camera_live:
            self.camera.stop()
            self.camera.close()
            self.is_camera_live = False
        self.camera = None
        print('Camera stopped')
        display.image_display.destroy_windows()
        print("cv2.destroyAllWindows")
        if constants.image_processing_tracing_record_video: self.video_writer.release()

    def __process_pipe_message(self):
        while self.parent_process_pipe.poll():
            msg = self.parent_process_pipe.recv()
            if msg[0] == 'close':
                self.keep_camera_processing = False
            elif msg[0] == 'time_diff':
                self.client_server_time_difference = msg[1]
            elif msg[0] == 'last_drive_params':
                self.last_drive_params = msg[1]

    def __process_next_frame(self):
        try:
            _, fps, frame_num = self.fps.update()
            #print("Camera processing FPS:"+str(fps)+" frame number:"+str(frameNum)+" datetime:"+ str(datetime.now()))
            if constants.image_processing_tracing_show_original:
                display.image_display.add_image_to_queue("Original", self.camera.original_frame)
            if constants.image_processing_tracing_show_region_of_interest:
                display.image_display.add_image_to_queue("Region Of Interest", self.camera.image)

            if(self.camera_mode == CAMERA_MODE_DETECT_ALIENS):
                alien_objects, frame_timestamp, detected_image = self.camera.detect_aliens()
                payload = {'message': 'updateAlienReadings', 'frame_timestamp':frame_timestamp-self.client_server_time_difference, 'aliens': []}
                if alien_objects is not None:
                    for (alien_id, alien_object) in alien_objects.items():
                        payload['aliens'].append(
                            {'id': int(alien_id), 'distance': int(round(alien_object[3] * 100)), 'xAngle': int(round(alien_object[4])), 'yAngle': 0})
            elif (self.camera_mode == CAMERA_MODE_DETECT_COLOURED_SHEETS):
                sheets, frame_timestamp, detected_image = self.camera.detect_coloured_sheets()
                payload = {'message': 'updateColouredSheetsReadings', 'frame_timestamp':frame_timestamp-self.client_server_time_difference, 'sheets': []}
                if(sheets is not None and len(sheets)>0):
                    for colour, distance, x_angle in sheets:
                        payload['sheets'].append({'colour': colour, 'distance':int(round(distance * 100)), 'xAngle': int(round(x_angle))})
            elif (self.camera_mode == CAMERA_MODE_DETECT_WHITE_LINE_TRACK):
                vector, frame_timestamp, detected_image = self.camera.detect_white_line()
                payload = {'message': 'updateWhiteLineReadings', 'frame_timestamp':frame_timestamp-self.client_server_time_difference}
                if(vector is not None and len(vector)>0):
                    payload['vector']=vector

            self.parent_process_pipe.send(payload)
            self.write_trace_video_frame(detected_image, frame_timestamp)

        except Exception as exc:
            print("Exception in camera_processor.__process_next_frame:", exc)

    def write_trace_video_frame(self, image, frame_timestamp):
        if not constants.image_processing_tracing_record_video: return
        cv2.putText(image, 'frame time:'+str(round(frame_timestamp-self.start_time,3)) +' lag:'+str(round(time.time()-frame_timestamp,3)), (10,25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        cv2.putText(image, 'drive:'+str(round(self.last_drive_params[0],1))+':'+str(round(self.last_drive_params[1],1)), (10,55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        self.video_writer.write(image)

    def __get_region_of_interest(self, config_section):
        t = config_section["top"]
        b = config_section["bottom"]
        l = config_section["left"]
        r = config_section["right"]
        if t>0 or b > 0 or l>0 or r>0:
            return (t,b,l,r)
        return None

class CameraProcessor:
    def __init__(self):
        self.camera_sub_process = None
        self.camera_sub_process_pipe = None
        self.on_alien_update_handler = None
        self.on_coloured_sheet_update_handler = None
        self.on_white_line_update_handler = None
        self.camera_mode = CAMERA_MODE_OFF
        print("CameraProcessor init finished")

    def set_camera_mode(self, new_camera_mode):
        print("set_camera_mode ", new_camera_mode)
        if self.camera_mode == new_camera_mode:
            print("set_camera_mode - mode did not change. ignoring")
            return
        else:
            if self.camera_sub_process is not None:
                #close the pre-existing camera process
                self.camera_sub_process_pipe.send(('close',))
                self.camera_sub_process.join()
                self.camera_sub_process_pipe= None
                self.camera_sub_process = None

        if new_camera_mode != CAMERA_MODE_OFF:
            #start the camera
            self.camera_sub_process_pipe, sub_process_pipe = Pipe()
            self.camera_sub_process = Process(target=init_camera_subprocess,args=(sub_process_pipe, new_camera_mode))
            self.camera_sub_process.start()
            loop = asyncio.get_event_loop()
            loop.create_task(self.__process_camera_messages())

        self.camera_mode = new_camera_mode

    async def __process_camera_messages(self):
        while self.camera_mode!=CAMERA_MODE_OFF:
            while self.camera_sub_process_pipe.poll():
                payload = self.camera_sub_process_pipe.recv()
                if payload['message'] == 'updateAlienReadings' and self.on_alien_update_handler is not None:
                    self.on_alien_update_handler(payload)
                elif payload['message'] == 'updateColouredSheetsReadings' and self.set_coloured_sheet_update_handler is not None:
                    self.set_coloured_sheet_update_handler(payload)
                elif payload['message'] == 'updateWhiteLineReadings' and self.on_white_line_update_handler is not None:
                    self.on_white_line_update_handler(payload)
                await asyncio.sleep(0.0001)

    def set_alien_update_handler(self, handler):
        self.on_alien_update_handler=handler

    def set_coloured_sheet_update_handler(self, handler):
        self.on_coloured_sheet_update_handler=handler

    def set_white_line_update_handler(self, handler):
        self.on_white_line_update_handler=handler

    def set_client_server_time_difference(self, time_diff):
        if self.camera_sub_process_pipe is not None:
            self.camera_sub_process_pipe.send(('time_diff',time_diff))

    def set_last_drive_params(self, speed_left, speed_right):
        if self.camera_sub_process_pipe is not None:
            self.camera_sub_process_pipe.send(('last_drive_params',(speed_left, speed_right)))
