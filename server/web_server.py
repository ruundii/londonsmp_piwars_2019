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

isDebugUpdates = False
isDebugCommands = False
processor = None
joystick_processor = None

mainloop = None
executor = None

for argument in sys.argv:
    if str(argument).lower() == '-debug':
        isDebugUpdates = True
        isDebugCommands = True
    if str(argument).lower() == '-debugupdates':
        isDebugUpdates = True
    if str(argument).lower() == '-debugcommands':
        isDebugCommands = True


class RobotWebsocketServer(WebSocketHandler):
    connected = False
    processor = None
    clients = []

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def on_message(self, message):
        try:
            payload = json.loads(message)
            if isDebugCommands:
                print(payload)
            client_cmd = payload['command']

            if client_cmd == 'drive':
                speedLeft = int(payload['speedLeft'])
                speedRight = int(payload['speedRight'])
                #print("drive ",speedLeft,speedRight)
                mainloop.run_in_executor(executor, self.processor.drive, speedLeft, speedRight)

            elif client_cmd == 'say':
                mainloop.run_in_executor(executor, self.processor.say, payload['text'], payload['lang'])

            elif client_cmd == 'displayText':
                mainloop.run_in_executor(executor, self.processor.displayText, payload['text'], payload['lines'])

            elif client_cmd == 'display_clear':
                mainloop.run_in_executor(executor, self.processor.displayText, "", payload['lines'])

            elif client_cmd == 'ready':
                pass

            elif client_cmd == 'startRun':
                pass
                #mainloop.run_in_executor(executor, self.processor.robotController.initialiseRun, bool(payload['isSimulation']))

            elif client_cmd == 'shutdown':
                self.processor.close()
                pass
            else:
                print("Unknown command received", client_cmd)
        except Exception as exc:
            print(exc)

    def handleSensorUpdate(self, data):
        if self.connected:
            global mainloop
            mainloop.add_callback(self.writeUpdateMessage, json.dumps(data))

    def writeUpdateMessage(self, data):
        if isDebugUpdates:
            print(data)
        if self.connected and self.stream is not None and not self.stream._closed:
            self.write_message(data)

    def open(self):
        print(self.stream.socket, 'ws connect called')
        self.clients.append(self)
        if len(self.clients) == 0:
            return
        try:
            global processor
            self.processor = processor
            self.set_nodelay(True)
            mainloop.run_in_executor(executor, self.initProcessor)
            print('ws connect success')
            self.connected = True
        except Exception as exc:
            print(exc)
            raise exc

    def initProcessor(self):
        self.processor.initialise()
        self.processor.onDistanceUpdate(self.handleSensorUpdate)
        self.processor.onColourUpdate(self.handleSensorUpdate)
        self.processor.onLineSensorsUpdate(self.handleSensorUpdate)
        self.processor.onMarkerUpdate(self.handleSensorUpdate)

    def closeProcessor(self):
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
        mainloop.run_in_executor(executor, self.closeProcessor)

    def check_origin(self, origin):
        return True


def run_server():
    # checking running processes.
    global mainloop
    global processor
    global executor
    global joystick_processor
    executor = ThreadPoolExecutor(max_workers=1)
    processor = RobotProcessor()
    joystick_processor = JoystickProcessor(processor)
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


