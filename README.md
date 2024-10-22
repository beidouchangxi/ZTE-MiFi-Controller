# ZTE-MiFi-Controller
SMS forwarding script for ZTE MiFi Product MF79U 

## Background
I have a company SIM card which mostly used for networking with MiFi, but sometimes I would like to receive phone call and SMS from it.

For phone call there is already the call forwarding service from MNO, I can forward phone calls to my private phone, the problem is not similar service for SMS.

As there is a web interface for MF79U for receive/send SMS, I did some reverse engineering to find APIs and wrote this script.

## What it really does
This script checks unread SMSs from MiFI device with fixed interval and forwards them to a pre-set phone number.

All read SMSs would be deleted to save storage space, forwarding activities will be logged in /Output/Log folder for user audit.

## How to use it

### Configuration
You must first complete the config file "UserSetting.ini" before use it, If you don't have a UserSetting.ini, the first run of ForwardSMS.py will generate one with default content.

For section "zte_device_info":
  - "hostname" is your MiFi IP address;
  - "password" is your MiFi admin password.

For section "forwarding_setting":
  - "sms_forward_to" is your target phone number with contry code;
  - "check_interval" is the delay for each SMS checking cycle with unit second;
  - "logging_level" is the logging level for the log file under /Output/Log with one letter, possible options: 'D', 'I', 'W', 'E', 'C'.

### Click and run
ForwardSMS.py is the main entry for the service, normally perform command "python ForwardSMS.py" will start everything for you (or simply double click).

The recommended settting is run the scirpt in background with Windows task scheduler or other similar tools.

StartForwarding.bat works also for Windows user, it does nothing more but try to activate the venv which is not needed if you don't have one.

## Compatibility

### Mifi Device
Built with my ZTE MiFi MF79U, might be compatible for other ZTE models.

### Python
Built with python3.12 and lib requests.

### OS
Tested with Windows, since no native API is used, should be compatible with other OS.
