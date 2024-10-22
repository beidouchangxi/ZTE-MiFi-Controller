from Utilities import controller, sms_forward_to

while True:
    input('Wait for start')
    print(controller.send_sms(sms_forward_to, 'SMS fowrading test 123456 短信测试'))
