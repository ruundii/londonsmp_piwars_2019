import time
from videoutils.robot_camera import RobotCamera
from videoutils.fps import FPS
from threading import Thread, Lock
import config.constants_global as constants
import cv2
import json
import videoutils.image_display as display


CAMERA_MODE_OFF = -1
CAMERA_MODE_DETECT_ALIENS = 0
CAMERA_MODE_DETECT_COLOURED_SHEETS = 1
CAMERA_MODE_DETECT_WHITE_LINE_TRACK = 2
import os
havedisplay = "DISPLAY" in os.environ or os.name == 'nt'
display.image_display.set_mode(havedisplay)


class CameraProcessor:
    def __init__(self):
        self.camera_mode_lock = Lock()
        self.camera_lock = Lock()
        self.camera_thread = None
        self.camera = None
        self.is_camera_live = False
        self.keep_camera_processing = False
        self.fps = FPS()
        self.camera_mode = CAMERA_MODE_OFF
        self.last_drive_params = (0,0)
        self.start_time = time.time()
        with open(constants.regions_config_name) as json_config_file:
            self.regions_config = json.load(json_config_file)
        self.video_writer = None

        self.on_alien_update_handler = None
        self.on_coloured_sheet_update_handler = None
        self.on_white_line_update_handler = None
        print("CameraProcessor init finished")
        self.client_server_time_difference = 0

    def set_last_drive_params(self, speed_left, speed_right):
        self.last_drive_params = (speed_left, speed_right)

    def set_camera_mode(self, new_camera_mode):
        print("set_camera_mode ", new_camera_mode)
        with self.camera_mode_lock:
            if(self.camera_mode == new_camera_mode):
                print("set_camera_mode - mode did not change. ignoring")
                return
            elif(new_camera_mode == CAMERA_MODE_OFF):
                self.__stop_camera()
                if constants.image_processing_tracing_record_video: self.video_writer.release()
            else:
                if(new_camera_mode == CAMERA_MODE_DETECT_ALIENS):
                    self.__start_camera(constants.resolution_aliens, constants.framerate, region_of_interest=self.__get_region_of_interest(self.regions_config["labyrinth"]), prepare_hsv=True)
                elif(new_camera_mode == CAMERA_MODE_DETECT_COLOURED_SHEETS):
                    self.__start_camera(constants.resolution_coloured_sheet, constants.framerate, region_of_interest=self.__get_region_of_interest(self.regions_config["colour_sheets"]), prepare_hsv=True)
                elif(new_camera_mode == CAMERA_MODE_DETECT_WHITE_LINE_TRACK):
                    self.__start_camera(constants.resolution_speed_track, constants.framerate, region_of_interest=self.__get_region_of_interest(self.regions_config["speed_line"]), prepare_hsv=False, prepare_gray=True)
                if constants.image_processing_tracing_record_video:
                    self.start_time = time.time()
                    video_path = 'video_trace'+time.strftime("%Y-%m-%d_%H-%M-%S")+'.avi'
                    self.video_writer = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'MJPG'), 4, self.camera.actual_resolution)
            self.camera_mode=new_camera_mode

    def __get_region_of_interest(self, config_section):
        t = config_section["top"]
        b = config_section["bottom"]
        l = config_section["left"]
        r = config_section["right"]
        if t>0 or b > 0 or l>0 or r>0:
            return (t,b,l,r)
        return None

    def set_alien_update_handler(self, handler):
        self.on_alien_update_handler=handler

    def set_coloured_sheet_update_handler(self, handler):
        self.on_coloured_sheet_update_handler=handler

    def set_white_line_update_handler(self, handler):
        self.on_white_line_update_handler=handler


    def __start_camera(self, resolution, framerate, region_of_interest = None, prepare_gray = False, prepare_hsv=False):
        with self.camera_lock:
            # Camera initialisation
            try:
                self.camera = RobotCamera(resolution, framerate, region_of_interest, prepare_gray, prepare_hsv)
                self.camera.load()
                self.camera.start()
                time.sleep(0.3)
                self.is_camera_live = True
            except Exception as exc:
                print('Exception in camera_processor.__start_camera: Failed to initialise camera ' + str(exc))
            if self.is_camera_live:
                self.keep_camera_processing = True
                if self.camera_thread is None or not self.camera_thread.isAlive():
                    self.camera_thread = Thread(target=self.__camera_processing_loop)
                    self.camera_thread.start()
            print('Camera started')

    def __stop_camera(self):
        with self.camera_lock:
            self.keep_camera_processing = False
            time.sleep(0.3)
            self.camera_thread = None
            if self.is_camera_live:
                self.camera.stop()
                self.camera.close()
                self.is_camera_live = False
            self.camera = None
            print('Camera stopped')

    def __camera_processing_loop(self):
        while self.keep_camera_processing:
            try:
                _, fps, frame_num = self.fps.update()
                #print("Camera processing FPS:"+str(fps)+" frame number:"+str(frameNum)+" datetime:"+ str(datetime.now()))
                if constants.image_processing_tracing_show_original:
                    display.image_display.add_image_to_queue("Original", self.camera.original_frame)
                if constants.image_processing_tracing_show_region_of_interest:
                    display.image_display.add_image_to_queue("Region Of Interest", self.camera.image)

                if(self.camera_mode == CAMERA_MODE_DETECT_ALIENS):
                    alien_objects, frame_timestamp, detected_image = self.camera.detect_aliens()
                    if frame_timestamp is None:
                        time.sleep(0.05)
                        continue
                    payload = {'message': 'updateAlienReadings', 'frame_timestamp':frame_timestamp-self.client_server_time_difference, 'aliens': []}
                    if alien_objects is not None:
                        for (alien_id, alien_object) in alien_objects.items():
                            payload['aliens'].append(
                                {'id': int(alien_id), 'distance': int(round(alien_object[3] * 100)), 'xAngle': int(round(alien_object[4])), 'yAngle': int(round(alien_object[5]))})
                    if self.on_alien_update_handler is not None:
                        self.on_alien_update_handler(payload)
                    self.write_trace_video_frame(detected_image, frame_timestamp)
                    #time.sleep(0.1)
                elif (self.camera_mode == CAMERA_MODE_DETECT_COLOURED_SHEETS):
                    sheets, frame_timestamp, detected_image = self.camera.detect_coloured_sheets()
                    if frame_timestamp is None:
                        time.sleep(0.05)
                        continue
                    payload = {'message': 'updateColouredSheetsReadings', 'frame_timestamp':frame_timestamp-self.client_server_time_difference, 'sheets': []}
                    if(sheets is not None and len(sheets)>0):
                        for colour, distance, x_angle in sheets:
                            payload['sheets'].append({'colour': colour, 'distance':int(round(distance * 100)), 'xAngle': int(round(x_angle))})
                    if self.on_coloured_sheet_update_handler is not None:
                        self.on_coloured_sheet_update_handler(payload)
                    #time.sleep(0.05)
                    self.write_trace_video_frame(detected_image, frame_timestamp)
                elif (self.camera_mode == CAMERA_MODE_DETECT_WHITE_LINE_TRACK):
                    vector, frame_timestamp, detected_image = self.camera.detect_white_line()
                    if frame_timestamp is None:
                        time.sleep(0.05)
                        continue
                    payload = {'message': 'updateWhiteLineReadings', 'frame_timestamp':frame_timestamp-self.client_server_time_difference}
                    if(vector is not None and len(vector)>0):
                        payload['vector']=vector
                    if self.on_white_line_update_handler is not None:
                        self.on_white_line_update_handler(payload)
                    self.write_trace_video_frame(detected_image, frame_timestamp)

            except Exception as exc:
                print("Exception in camera_processor.__camera_processing_loop:", exc)
        print("cv2.destroyAllWindows")
        display.image_display.destroy_windows()

    def write_trace_video_frame(self, image, frame_timestamp):
        if not constants.image_processing_tracing_record_video: return
        cv2.putText(image, 'frame time:'+str(round(frame_timestamp-self.start_time,3)) +' lag:'+str(round(time.time()-frame_timestamp,3)), (10,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.putText(image, 'drive:'+str(self.last_drive_params[0])+':'+str(self.last_drive_params[1]), (10,55), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        self.video_writer.write(image)


    def set_client_server_time_difference(self, time_diff):
        self.client_server_time_difference = time_diff
