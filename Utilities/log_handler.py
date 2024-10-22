import logging
from logging import debug, info, warning, error
import os
import time
import sys

# Find where the main script path is
if getattr(sys, 'frozen', False):
    MainPath = os.path.dirname(sys.executable)
else:
    assert __file__, 'MainPath not found!'
    MainPath = os.path.split(os.path.dirname(__file__))[0]

# Prepare the output folder
OutputPath = os.path.join(MainPath, 'Output')

class LogHandler(object):
    LogFolder = os.path.join(OutputPath, 'Log')
    DateFormat = '%Y-%m-%d %a %H:%M:%S'
    LevelDict = {
        'D' : logging.DEBUG,
        'I' : logging.INFO,
        'W' : logging.WARNING,
        'E' : logging.ERROR,
        'C' : logging.CRITICAL
        }
    def __init__(self, name=None, **kwargs):
        valid_keys = ('level', )
        if invalid_keys:=[key for key in kwargs if key not in valid_keys]:
            raise ValueError(f'Unexpected keyword argument(s): {invalid_keys}')
        if 'level' in kwargs:
            log_level = self.LevelDict[kwargs['level']]
        else:
            log_level = logging.DEBUG

        self.Logger = logging.getLogger(name)
        
        # Console output
        self.ConsoleHandler = logging.StreamHandler()
        self.ConsoleHandler.setLevel(logging.INFO)
        self.ConsoleHandler.setFormatter(
            logging.Formatter(
                '%(asctime)s.%(msecs)03d %(message)s',
                self.DateFormat
                )
            )
        
        # Log file output
        self.initLogFile()
        self.FileHandler = logging.FileHandler(self.CurrentLogPath, encoding='utf-8')
        self.FileHandler.setFormatter(
            logging.Formatter(
                '%(asctime)s.%(msecs)03d %(filename)20s[line:%(lineno)03d] %(levelname)5s %(message)s',
                self.DateFormat
                )
            )
        
        # Setting for logger
        self.Logger.setLevel(log_level)
        self.Logger.addHandler(self.ConsoleHandler)
        self.Logger.addHandler(self.FileHandler)
    
    def initLogFile(self):
        if not os.path.exists(OutputPath):
            os.mkdir(OutputPath)
        if not os.path.exists(self.LogFolder):
            os.mkdir(self.LogFolder)
        self.CurrentLogFilename = 'RunLog_' + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + '.txt'
        self.CurrentLogPath = os.path.join(self.LogFolder, self.CurrentLogFilename)
    
    def setLevel(self, level):
        self.Logger.setLevel(self.LevelDict[level])
    
    def __getattr__(self, name):
        try:
            return getattr(self, name)
        except AttributeError:
            return getattr(self.Logger, name)

    def __setattr__(self, name, value):
        try:
            object.__setattr__(self, name, value)
        except AttributeError:
            setattr(self.Logger, name, value)

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return getattr(self.Logger, name)

    def __setattribute__(self, name, value):
        try:
            object.__setattribute__(self, name, value)
        except AttributeError:
            setattr(self.Logger, name, value)

log = LogHandler()
