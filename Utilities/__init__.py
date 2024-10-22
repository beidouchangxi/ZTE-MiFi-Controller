try:
    from Utilities.zte_controller import ZteController
    from Utilities.config_handler import ConfigFile
    from Utilities.log_handler import log
except ModuleNotFoundError:
    from zte_controller import ZteController
    from config_handler import ConfigFile
    from log_handler import log


DefaultSetting = {
    'zte_device_info' : {
        'hostname': 'example_username',
        'password': 'example_password',
        },
    'forwarding_setting' : {
        'sms_forward_to' : '+8613888888888',
        'check_interval' : '5',
        'logging_level'  : 'D',
        }
    }

config = ConfigFile(DefaultSetting)

if not config.is_default:
    
    hostname = config.fallbackRead('zte_device_info', 'hostname')
    password = config.fallbackRead('zte_device_info', 'password')
    
    sms_forward_to = config.fallbackRead('forwarding_setting', 'sms_forward_to')
    check_interval = int(config.fallbackRead('forwarding_setting', 'check_interval'))
    logging_level = config.fallbackRead('forwarding_setting', 'logging_level')
    
    log.info(f'SMS message will be forward to: {sms_forward_to}')
    log.info(f'Check interval for each cycle: {check_interval}')
    log.info(f'Log level loaded from config: {logging_level}')
    
    # Init everything
    log.setLevel(logging_level)
    controller = ZteController(hostname, password)
    
else:
    raise Exception('No config file found! An example file is generated')