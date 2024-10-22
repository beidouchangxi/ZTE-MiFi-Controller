import time

from Utilities import controller, sms_forward_to, check_interval, log

while True:
    if total_unread:=controller.get_sms_unread():
        log.info('Unread SMS total: %s' % total_unread)
        sms_list = controller.get_sms_total()
        if sms_list==None:
            controller.initSession()
            continue
        for sms in sms_list:
            if sms['tag'] == "1":
                log.info(f'sms {sms["id"]} msimdn:  {sms["number"]}')
                log.info(f'sms {sms["id"]} date:    {sms["date"]}')
                log.info(f'sms {sms["id"]} content: {sms["content_decoded"]}')
                log.info(f'sms {sms["id"]} class:   {sms["sms_class"]}')
                controller.set_tag_sms(sms["id"], 0)
                forward_content = f'From: {sms["number"]}\nContent: {sms["content_decoded"]}'
                forward_result = controller.send_sms(sms_forward_to, forward_content)
                log.info(f'sms forwarded to {sms_forward_to} with result {forward_result}')
                time.sleep(1)
        id_list = [sms["id"] for sms in sms_list]
        log.info(f'Delete SMS with id list {id_list}')
        controller.delete_sms(id_list)
    else:
        log.info("No unread SMS from device")
    time.sleep(check_interval)