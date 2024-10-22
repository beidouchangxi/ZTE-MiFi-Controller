import requests
import time
import json
import base64
import hashlib

try:
    from log_handler import log
except ModuleNotFoundError:
    from Utilities.log_handler import log

class ZteController(object):
    def __init__(self, host, pw):
        self.password = pw
        self.baseurl_get = f'http://{host}/goform/goform_get_cmd_process'
        self.baseurl_set = f'http://{host}/goform/goform_set_cmd_process'
        self.header_req = {
            'accept'          : 'application/json, text/javascript, */*; q=0.01',
            'connection'      : 'keep-alive',
            'referer'         :f'http://{host}/index.html',
            'x-requested-with': 'XMLHttpRequest',
            }
        self.initSession()
    
    def initSession(self):
        while True:
            if self._initSession():
                break
            else:
                log.error("No cookies fetched! Let's try again.")
                time.sleep(1)
    
    def _initSession(self):
        '''
        returns {"result":"0"} when success
        returns {"result":"1"} when missing parameter
        returns {"result":"3"} when wrong password
        returns {"result":"failure"} when invalid header
        '''
        self.session = requests.Session()
        data = {
            'isTest'   : False,
            'goformId' : 'LOGIN',
            'password' : base64.b64encode(self.password.encode('utf-8'))
            }
        response = self.post(data)
        if self.session.cookies.get_dict():
            return True
        else:
            return False
    
    def get(self, para):
        para = dict(para)
        para['_'] = int(time.time()*1000)
        while True:
            try:
                response = self.session.get(
                    self.baseurl_get,
                    headers=self.header_req,
                    params=para,
                    timeout=2
                    )
            except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
                log.warning('Connection timeout! Try again for get data!')
                continue
            else:
                break
        return self.handleResponse(response)
    
    def post(self, data):
        while True:
            try:
                log.debug('Post data: ' + str(data))
                response = self.session.post(
                    self.baseurl_set,
                    data=data,
                    headers=self.header_req,
                    timeout=2
                    )
            except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
                log.warning('Connection timeout! Try again for post data!')
                continue
            else:
                break
        return self.handleResponse(response)
    
    def handleResponse(self, response):
        if response.status_code in (200, 201, 204):
            log.debug("Request successfully: " + response.text)
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                return None
        else:
            log.error("Request failed. Status code:", response.status_code)
            log.error(response.text)
            return None
    
    @staticmethod
    def text2sms(text):
        return text.encode('utf_16be').hex()
    
    @staticmethod
    def sms2text(sms_content):
        return bytes.fromhex(sms_content).decode('utf_16be')
    
    @staticmethod
    def handle_id_or_ids(id_info):
        if isinstance(id_info, str):
            if id_info.isdecimal():
                return id_info+';'
            else:
                return id_info
        elif isinstance(id_info, int):
            return str(int)+';'
        elif isinstance(id_info, list):
            return ''.join(str(i)+';' for i in id_info)
        else:
            raise TypeError('Unsupported type for id!')
    
    def update_sms(self):
        '''
        with valid cookie returns {"upgrade_result":"error"}
        otherwise returns {"upgrade_result":""}
        '''
        para_upgrade_result = {
            'isTest' : False,
            'cmd'    : 'upgrade_result'
            }
        return self.get(para_upgrade_result)
    
    def get_sms_capa(self):
        '''
        works without valid cookie, return a dict like {
            "sms_nv_total":"100","sms_sim_total":"50","sms_nvused_total":"7","sms_nv_rev_total":"1","sms_nv_send_total":"6",
            "sms_nv_draftbox_total":"0","sms_sim_rev_total":"0","sms_sim_send_total":"0","sms_sim_draftbox_total":"0"}
        '''
        para_sms_capacity_info = {
            'isTest' : False,
            'cmd' : 'sms_capacity_info'
            }
        return self.get(para_sms_capacity_info)
    
    def get_sms_unread(self):
        '''
        works without valid cookie, return the total unread sms stored in device(sms_dev_unread_num)
        the API returns something like: {"sms_unread_num":"0","sms_dev_unread_num":"0","sms_sim_unread_num":"0"}
        '''
        para_sms_unread_num = {
            'isTest' : False,
            'cmd' : 'sms_unread_num',
            'multi_data' : '1'
            }
        return int(self.get(para_sms_unread_num)['sms_dev_unread_num'])
    
    def get_sms_total(self):
        '''
        with valid coolie this function returns a list contains multiply dict, each one represents a SMS, keys listed bellow;
        the raw result from api wrap the sms list with a dict like: {"messages": sms_list}
        id:                         int string, unique id for SMS;
        number:                     string starts with "+" and followed by int, target or source MSISDN, depends on tag;
        content:                    hex string, encoded with utf_16be;
        content_decoded:            content decoded    
        tag:                        int string:
                                                "0" for read and recived SMS,
                                                "1" for unread and recived SMS,
                                                "2" for sent SMS;
        date:                       timestamp like "24,10,08,20,43,44,+32";
        draft_group_id:             something always "";
        received_all_concat_sms:    something always "1";
        concat_sms_total:           something always "0";
        concat_sms_received:        something always "0";
        sms_class:                  something always "4"
        
        if no sms is stored, then the sms_list is empty;
        
        without valid cookie this function returns None, the raw API result is {"sms_data_total":""}
        '''
        para_sms_data_total = {
            'isTest' : False,
            'cmd' : 'sms_data_total',
            'page' : 0,
            'data_per_page' : 500,
            'mem_store' : 1,
            'tags' : 10,
            'order_by' : 'order+by+id+desc'
            }
        if "messages" in (result:=self.get(para_sms_data_total)):
            sms_list = result["messages"]
            for sms in sms_list:
                sms['content_decoded'] = self.sms2text(sms['content'])
            return sms_list
        else:
            return None
    
    def get_ad(self):
        '''
        Something needed for post APIs, calculated with some strange things by md5
        works normally without valid cookie
        '''
        para_rd = {
            'isTest': False,
            'cmd': 'RD,cr_version,wa_inner_version',
            'multi_data' : 1
            }
        data = self.get(para_rd)
        rd, rd0, rd1 = data['RD'], data['wa_inner_version'], data['cr_version']
        md5 = lambda x:hashlib.md5(x.encode('ascii')).hexdigest()
        return md5(md5(rd0+rd1)+rd)
    
    def send_sms(self, num, content):
        '''
        returns {"result":"success"} when success
        returns {"result":"failure"} when failed (including invalid cookie)
        '''
        data_send_sms = {
            'isTest' : False,
            'goformId' : 'SEND_SMS',
            'notCallback' : True,
            'Number' : num,
            'sms_time' : time.strftime("%y;%m;%d;%H;%M;%S;%z", time.localtime()),
            'MessageBody' : self.text2sms(content),
            'ID' : -1,
            'encode_type' : 'UNICODE',
            'AD' : self.get_ad(),
            }
        return self.post(data_send_sms)
    
    def delete_sms(self, id_info):
        '''
        returns {"result":"success"} when success
        returns {"result":"failure"} when failed (including invalid cookie)
        '''
        id_info = self.handle_id_or_ids(id_info)
        data_delete_sms = {
            'isTest' : False,
            'goformId' : 'DELETE_SMS',
            'msg_id' : id_info,
            'notCallback' : True,
            'AD' : self.get_ad(),
            }
        return self.post(data_delete_sms)
    
    def set_tag_sms(self, id_info, tag=0):
        '''
        returns {"result":"success"} when success
        returns {"result":"failure"} when failed (including invalid cookie)
        '''
        id_info = self.handle_id_or_ids(id_info)
        data_read_sms = {
            'isTest': False,
            'goformId': 'SET_MSG_READ',
            'msg_id': id_info,
            'tag': tag,
            'AD': self.get_ad(),
            }
        return self.post(data_read_sms)