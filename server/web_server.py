#!/usr/bin/env python3

import json
import sys
from processors.robot_processor import RobotProcessor
from processors.joystick_processor import JoystickProcessor
from tornado.websocket import WebSocketHandler
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application
import asyncio
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from file_server import FileRequestHandler, StaticFileRequestHandler
from concurrent.futures import ThreadPoolExecutor
import time
from processors.blockly_code_processor import BlocklyCodeProcessor

is_debug_updates = False
is_debug_commands = False
processor = None
blockly_code_processor = None
joystick_processor = None

mainloop = None
executor = None
import os
#os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

for argument in sys.argv:
    if str(argument).lower() == '-debug':
        is_debug_updates = True
        is_debug_commands = True
    if str(argument).lower() == '-debugupdates':
        is_debug_updates = True
    if str(argument).lower() == '-debugcommands':
        is_debug_commands = True


class RobotWebsocketServer(WebSocketHandler):
    connected = False
    processor = None
    blockly_code_processor = None
    timestamp_request_time = None
    clients = []
    is_running_on_robot = False

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def on_message(self, message):
        try:
            global joystick_processor
            payload = json.loads(message)
            if('client_timestamp' in payload):
                now = time.time()
                roundtrip = now-self.timestamp_request_time
                client_server_time_difference = now - payload['client_timestamp']/1000.00-roundtrip/2.0
                print('roundtrip:',roundtrip,' time difference:', client_server_time_difference)
                mainloop.run_in_executor(executor, self.processor.set_client_server_time_difference, client_server_time_difference)
                return

            if is_debug_commands:
                print(payload)
            client_cmd = payload['command']

            if client_cmd == 'drive':
                speed_left = int(payload['speedLeft'])
                speed_right = int(payload['speedRight'])
                #print("drive command",speed_left,speed_right)
                mainloop.run_in_executor(executor, self.processor.drive, speed_left, speed_right)

            elif client_cmd == 'setCameraMode':
                mode = int(payload['mode'])
                mainloop.run_in_executor(executor, self.processor.set_camera_mode, mode)

            elif client_cmd == 'ready':
                pass

            elif client_cmd == 'startRunInBrowser':
                joystick_processor.set_state(False)
                self.init_handlers(True)
                self.is_running_on_robot = False
                #mainloop.run_in_executor(executor, self.processor.robotController.initialiseRun, bool(payload['is_simulation']))

            elif client_cmd == 'startRunOnRobot':
                joystick_processor.set_state(False)
                self.is_running_on_robot = True
                mainloop.run_in_executor(executor, self.blockly_code_processor.start_run, payload['code'])

            elif client_cmd == 'stopRun':
                if(self.is_running_on_robot):
                    mainloop.run_in_executor(executor, self.blockly_code_processor.stop_run)
                else:
                    mainloop.run_in_executor(executor, self.processor.stop_run)
                joystick_processor.set_state(True)
                self.init_handlers(False)

            elif client_cmd == 'shutdown':
                self.processor.close()
            else:
                print("Unknown command received", client_cmd)
        except Exception as exc:
            print(exc)

    def handle_update_from_robot(self, data):
        if self.connected:
            global mainloop
            mainloop.add_callback(self.write_update_message, json.dumps(data))

    def write_update_message(self, data):
        if is_debug_updates:
            print(data)
        if self.connected and self.stream is not None and not self.stream._closed:
            self.write_message(data)

    def open(self):
        print(self.stream.socket, 'ws connect called')
        self.clients.append(self)
        if len(self.clients) == 0:
            return
        try:
            global processor, blockly_code_processor
            self.processor = processor
            self.blockly_code_processor = blockly_code_processor
            self.blockly_code_processor.init_handlers(self.robot_run_stopped)
            self.set_nodelay(True)
            mainloop.run_in_executor(executor, self.init_processor)
            print('ws connect success')
            self.connected = True
            self.timestamp_request_time = time.time()
            self.write_message(json.dumps({'server_timestamp':self.timestamp_request_time}))
        except Exception as exc:
            print(exc)
            raise exc

    def robot_run_stopped(self, error):
        self.is_running_on_robot = False
        joystick_processor.set_state(True)
        if self.connected and self.stream is not None and not self.stream._closed:
            self.write_message(json.dumps({'robot_run_finished':True, 'error_occured': error}))


    def init_handlers(self, on):
        self.processor.set_alien_update_handler(self.handle_update_from_robot if on else None)
        self.processor.set_coloured_sheet_update_handler(self.handle_update_from_robot if on else None)
        self.processor.set_distance_update_handler(self.handle_update_from_robot if on else None)
        self.processor.set_line_sensors_update_handler(self.handle_update_from_robot if on else None)


    def init_processor(self):
        self.processor.initialise()

    def close_processor(self):
        if len(self.clients)>0:
            return
        try:
            self.connected = False
            self.processor.close()
            print('ws close success')
        except Exception as exc:
            print(exc)
            raise exc

    def on_close(self):
        print('ws close called')
        self.clients.remove(self)
        mainloop.run_in_executor(executor, self.close_processor)

    def check_origin(self, origin):
        return True


def run_server():
    # checking running processes.
    global mainloop
    global processor
    global executor
    global joystick_processor
    global blockly_code_processor
    executor = ThreadPoolExecutor(max_workers=1)
    processor = RobotProcessor()
    joystick_processor = JoystickProcessor(processor)
    blockly_code_processor = BlocklyCodeProcessor(processor)
    app = Application([(r"/ws", RobotWebsocketServer),
                       (r"/blockly/(.*)", StaticFileRequestHandler,  {"path": "../blockly/"}),
                       (r"/svg-editor/(.*)", StaticFileRequestHandler, {"path": "../svg-editor/"}),
                       (r"/closure-library/(.*)", StaticFileRequestHandler, {"path": "../closure-library/"}),
                       (r"/files/(.*\.xml)", StaticFileRequestHandler, {"path": "./files"}),
                       (r"/svgs/(.*\.svg)", StaticFileRequestHandler, {"path": "./svgs"}),
                       (r'/(favicon.ico)', StaticFileRequestHandler, {"path": "../blockly/"}),
                       (r'/files/', FileRequestHandler),
                       (r'/svgs/', FileRequestHandler),
                       (r'/files/upload', FileRequestHandler),
                       (r'/svgs/upload', FileRequestHandler)])
    server = HTTPServer(app)
    server.listen(8000)
    mainloop = IOLoop.current()
    mainloop.start()

asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())

if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        processor.close()
        executor.shutdown()
        sys.exit(0)
else:
    try:
        run_server()
    except KeyboardInterrupt:
        processor.close()
        executor.shutdown()


