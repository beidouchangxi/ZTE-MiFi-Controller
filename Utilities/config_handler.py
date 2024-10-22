from configparser import ConfigParser
import os

try:
    from log_handler import MainPath
except ModuleNotFoundError:
    from Utilities.log_handler import MainPath

class ConfigFile(ConfigParser):
    def __init__(self, DefaultContent, ConfigFileName = 'UserSetting.ini'):
        '''
        DefaultContent: Keys are section names, values are dictionaries with keys and values
        '''
        ConfigFilePath = os.path.join(MainPath, ConfigFileName)
        self.DefaultContent = DefaultContent
        default = 'warning_info'
        super().__init__(self, default_section=default)
        self[default][default] = 'Please be noticed that I am not responsible for any damage this tool could cause'
        if os.path.exists(ConfigFilePath):
            self.read(ConfigFilePath, encoding='utf-8')
            self.is_default = False
        else:
            self.read_dict(DefaultContent)
            with open(ConfigFilePath, 'w', encoding='utf-8') as f:
                self.write(f)
            self.is_default = True
    
    def fallbackRead(self, *keys):
        try:
            result = self
            for key in keys:
                result = result[key]
        except KeyError:
            result = self.DefaultContent
            for key in keys:
                result = result[key]
        return result