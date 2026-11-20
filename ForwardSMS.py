import time

from Utilities import controller, sms_forward_to, check_interval, log

day_no = time.localtime().tm_yday

while True:
    try:
        if total_unread := controller.get_sms_unread():
            log.info('Unread SMS total: %s', total_unread)
            sms_list = controller.get_sms_total()
            if sms_list is None:
                log.warning('Session expired while fetching SMS list, re-initializing...')
                controller.initSession()
                continue

            delete_ids = []
            for sms in sms_list:
                if sms['tag'] == '1':
                    log.info('sms %s msisdn:  %s', sms['id'], sms['number'])
                    log.info('sms %s date:    %s', sms['id'], sms['date'])
                    log.info('sms %s content: %s', sms['id'], sms['content_decoded'])
                    log.info('sms %s class:   %s', sms['id'], sms['sms_class'])

                    forward_content = f"From: {sms['number']}\nContent: {sms['content_decoded']}"
                    forward_result = controller.send_sms(sms_forward_to, forward_content)
                    log.info('sms forwarded to %s with result %s', sms_forward_to, forward_result)

                    if isinstance(forward_result, dict) and forward_result.get('result') == 'success':
                        controller.set_tag_sms(sms['id'], 0)
                        delete_ids.append(sms['id'])
                    else:
                        log.error('Failed to forward sms %s, keeping it unread for retry', sms['id'])
                    time.sleep(1)
                else:
                    delete_ids.append(sms['id'])

            if delete_ids:
                log.info('Delete SMS with id list %s', delete_ids)
                controller.delete_sms(delete_ids)

        elif day_no != (day_now := time.localtime().tm_yday):
            log.info('Reboot the device for a new day: %s', day_now)
            day_no = day_now
            controller.reboot()
        else:
            log.debug('No unread SMS from device')

    except Exception:
        log.exception('Unhandled exception in main loop, retrying after %ss', check_interval)

    time.sleep(check_interval)