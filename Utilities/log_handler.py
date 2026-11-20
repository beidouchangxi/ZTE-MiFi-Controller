import logging
from logging import debug, info, warning, error
from logging.handlers import TimedRotatingFileHandler
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

        # Log file output (rotate daily, keep 14 days)
        self.initLogFile()
        self.FileHandler = TimedRotatingFileHandler(
            self.CurrentLogPath,
            when='midnight',
            interval=1,
            backupCount=14,
            encoding='utf-8',
            )
        self.FileHandler.suffix = '%Y-%m-%d'        

        # Setting for logger
        self.Logger.setLevel(log_level)
        self.Logger.addHandler(self.ConsoleHandler)
        self.Logger.addHandler(self.FileHandler)

    def initLogFile(self):
        os.makedirs(self.LogFolder, exist_ok=True)
        self.CurrentLogFilename = 'RunLog.txt'
        self.CurrentLogPath = os.path.join(self.LogFolder, self.CurrentLogFilename)    

    def setLevel(self, level):
        self.Logger.setLevel(self.LevelDict[level])
    
    def __getattr__(self, name):
        return getattr(self.Logger, name)

log = LogHandler()
