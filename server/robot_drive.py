from server.processors.robot_processor import RobotProcessor
import asyncio
import sys
import time

processor = RobotProcessor()


def runRobot():
    processor.initialise()
    processor.drive(True, 5)
    #processor.turn('right',10)

    processor.onMarkerUpdateHandler=onMarkerUpdate;
    for i in range(0, 20):
        print()
    time.sleep(2)
    processor.turn('straight',0)
    processor.drive(True, 0)

def onMarkerUpdate(data):
    print(data)


try:
    runRobot()
except (KeyboardInterrupt, SystemExit):
    print('Shutting down')
    processor.drive(True, 0)
    processor.turn('straight', 0)
    processor.close()
    sys.exit(0)
