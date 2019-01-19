import time
from server.videoutils.robot_camera import RobotCamera
from server.videoutils.fps import FPS
from threading import Thread, Lock
import server.config.constants_global as constants

CAMERA_MODE_OFF = -1
CAMERA_MODE_DETECT_ALIENS = 0
CAMERA_MODE_DETECT_COLOURED_SHEETS = 1
CAMERA_MODE_DETECT_WHITE_LINE_TRACK = 2

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

        self.on_alien_update_handler = None
        self.on_coloured_sheet_update_handler = None

    def set_camera_mode(self, new_camera_mode):
        print("set_camera_mode ", new_camera_mode)
        with self.camera_mode_lock:
            if(self.camera_mode == new_camera_mode):
                print("set_camera_mode - mode did not change. ignoring")
                return
            elif(new_camera_mode == CAMERA_MODE_OFF):
                self.__stop_camera()
            elif(new_camera_mode == CAMERA_MODE_DETECT_ALIENS or new_camera_mode == CAMERA_MODE_DETECT_COLOURED_SHEETS):
                self.__start_camera()
            self.camera_mode=new_camera_mode

    def set_alien_update_handler(self, handler):
        self.on_alien_update_handler=handler

    def set_coloured_sheet_update_handler(self, handler):
        self.on_coloured_sheet_update_handler=handler


    def __start_camera(self):
        with self.camera_lock:
            # Camera initialisation
            try:
                self.camera = RobotCamera()
                self.camera.load()
                self.camera.start()
                time.sleep(0.3)
                self.is_camera_live = True
            except Exception as exc:
                print('Failed to initialise camera ' + str(exc))
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
            time.sleep(0.1)
            payload = {'message': 'updateAlienReadings', 'aliens': []}

            try:
                self.camera.update()
                _, fps, frame_num = self.fps.update()
                #print("Camera processing FPS:"+str(fps)+" frame number:"+str(frameNum)+" datetime:"+ str(datetime.now()))
                frame,_ = self.camera.last_frame()
                alien_objects = self.camera.detect_aliens()
                if alien_objects is not None:
                    for (alien_id, alien_object) in alien_objects.items():
                        distance = constants.alien_image_height_mm/alien_object[3]*constants.alien_distance_multiplier+constants.alien_distance_offset
                        x = min(max(alien_object[0],0),constants.resolution[0])
                        y = min(max(alien_object[1], 0), constants.resolution[1])
                        x_angle = ((x - constants.resolution[0]/2.0) / constants.resolution[0]) * constants.camera_pov[0]
                        y_angle = ((constants.resolution[1]/2.0-y) / constants.resolution[1]) * constants.camera_pov[1]
                        payload['aliens'].append(
                            {'id': int(alien_id), 'distance': int(distance * 100), 'xAngle': int(x_angle), 'yAngle': int(y_angle)})
                if self.on_alien_update_handler is not None:
                    self.on_alien_update_handler(payload)
            except Exception as exc:
                print(exc)
