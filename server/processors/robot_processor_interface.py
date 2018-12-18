import abc

class RobotProcessorInterface(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.onDistanceUpdateHandler = None
        self.onColourUpdateHandler = None
        self.onLineSensorsUpdateHandler = None

    @abc.abstractmethod
    def initialise(self):
        pass

    @abc.abstractmethod
    def setSimulationMode(self, isSimulation):
        pass

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def drive(self, isForward, speed):
        pass

    @abc.abstractmethod
    def turn(self, direction, angle):
        pass

    @abc.abstractmethod
    def say(self, text, lang):
        pass

    @abc.abstractmethod
    def displayText(self, text, lines):
        pass

    @abc.abstractmethod
    def onDistanceUpdate(self, handler):
        self.onDistanceUpdateHandler = handler

    @abc.abstractmethod
    def onColourUpdate(self, handler):
        self.onColourUpdateHandler = handler

    @abc.abstractmethod
    def onLineSensorsUpdate(self, handler):
        self.onLineSensorsUpdateHandler = handler
