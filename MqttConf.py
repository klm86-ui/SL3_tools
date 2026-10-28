
"""
======================================================================================
Project: Cyber Security
Module: MqttConf
======================================================================================
Author: Pawe Sokoowski SL3
Date: 2026-03-13
Version: 1.0
Main script

Functionality:
Fast mqtt configuration and notification generator ( http also)
**================================EXAMPLE COMMANDS====================================**
Mqtt settingsd
#iot.request(mqtt_client.client_stop())
#set_setings(mqtt_client.client_conf())
#set_setings(cmd.cmd_conf())
#cmd.cmd_start(iot.request)

Notification creator - different adr for monitor or subscription method
not1=Notification()
not1.user="pawel"
not1.password="haslo"
subscription1=not1.constructor(True,"mqtt",False,1,"Topic1",500,1000,10,
                 True,False,"/monitor/add",["/iolinkmaster/port[1]/iolinkdevice/pdin"],1)
subscription5=not1.constructor(False,"http",False,1,"Topic5",500,1000,10,
                 True,False,"/monitor/add",["/iolinkmaster/port[3]/iolinkdevice/pdin"],5)

not1.add_monitor_notification(iot.request,subscription1)
not1.add_subscribe_notification(iot.request,"/timer[1]/counter/datachanged/subscribe",subscription4)

not1.remove_notification(iot.request,1)
"""
from typing import Any

from utils.Iot_core import IoTClient
import json

rq = IoTClient()


class Mqtt():
    def __init__(self,client :bool=False,
                 keepalive: int = 15,
                 willtopic: str = "will_topic",
                 willmessage: str = "will_message",
                 clientid: str = "1",
                 retain: bool = True,
                 validateservercertificate: int = 0,
                 trustedservercertificates: str = "",
                 certificate_key_pem: str = ""
                 ):
        self.client = client
        self.keepalive = keepalive
        self.willtopic = willtopic
        self.willmessage = willmessage
        self.clientid = clientid
        self.retain = retain
        self.validateservercertificate = validateservercertificate
        self.trustedservercertificates = trustedservercertificates
        self.certificate_key_pem = certificate_key_pem




    def client_conf(self)->dict:
        return {"connections/mqttclient/mqttsetup/qos":2,"connections/mqttclient/mqttsetup/keepalive":self.keepalive,
                "connections/mqttclient/mqttsetup/willtopic":self.willtopic,
                "connections/mqttclient/mqttsetup/willmessage":self.willmessage,
                "connections/mqttclient/mqttsetup/clientid":self.clientid,
                "connections/mqttclient/mqttsetup/retain": self.retain,
                "connections/mqttclient/mqttsetup/securesetup/validateservercertificate":self.validateservercertificate,
                "connections/mqttclient/mqttsetup/securesetup/trustedservercertificates":self.trustedservercertificates,
                "connections/mqttclient/mqttsetup/securesetup/certificate_key_pem":self.certificate_key_pem
                }

    def client_start(self,function, sb_flag)-> str:
        if sb_flag:url="/connections/mqttclient/status/start"
        else:url="connections/mqttConnection/status/start"
        resp=function(url)
        if resp['code'] == 200:
            print("Mqtt client starting")
        return resp


    def client_stop(self,function,sb_flag)-> str:
        if sb_flag:url="/connections/mqttclient/status/start"
        else:url="connections/mqttConnection/status/start"
        resp=function(url)
        if resp['code'] ==200:
            print("Mqtt client stopping")
        return resp
    def client_status(self,function,sb_flag)-> str:
        if sb_flag:url="/connections/mqttclient/status/getdata"
        else:url="connections/mqttConnection/status/getdata"
        resp=function(url)
        print(f"Response code:{resp}")
        if resp['code'] ==200:
            print(f"Mqtt client status : {resp['data']['value']}")
        return resp
class Cmd:
    def __init__(self,cmd  :bool=False,
                 server_ip: str ="192.168.5.10",
                 server_port :int =1883,
                 cmd_topic : str ="cmd",
                 cmd_reply_topic : str ="reply",
                 user: str ="",
                 password: str ="",
                 qos:int =2,
                 secure:int=0,
                 keepalive:int=15,
                 willtopic: str ="will_topic",
                 willmessage: str ="will_message",
                 validateservercertificate:int=0,
                 certificate_key : str = "",
                 trustedservercertificates : str = ""):
        self.cmd = cmd
        self.server_ip = server_ip
        self.server_port = server_port
        self.cmd_topic = cmd_topic
        self.cmd_reply_topic = cmd_reply_topic
        self.user = user
        self.password = password
        self.qos = qos
        self.keepalive = keepalive
        self.willtopic = willtopic
        self.willmessage = willmessage
        self.secure = secure
        self.validateservercertificate = validateservercertificate
        self.certificate_key = certificate_key
        self.trustedservercertificates = trustedservercertificates


        """ Use example:
            not1=Notification()
            not1.user="pawel"
            not1.password="haslo    """



    def cmd_conf(self)->dict:
        return {
                "connections/mqttcommandchannel/mqttcmdchannel/mqttcmdchannelsetup/brokerip": self.server_ip,
                "connections/mqttcommandchannel/mqttcmdchannel/mqttcmdchannelsetup/brokerport": self.server_port,
                "connections/mqttcommandchannel/mqttcmdchannel/mqttcmdchannelsetup/cmdtopic": self.cmd_topic,
                "connections/mqttcommandchannel/mqttcmdchannel/mqttcmdchannelsetup/defaultreplytopic":self.cmd_reply_topic,
                "connections/mqttcommandchannel/mqttcmdchannel/mqttcmdchannelsetup/user":self.user,
                "connections/mqttcommandchannel/mqttcmdchannel/mqttcmdchannelsetup/password":self.password,
                "connections/mqttcommandchannel/mqttcmdchannel/mqttcmdchannelsetup/qos":self.qos,
                "connections/mqttcommandchannel/mqttcmdchannel/mqttcmdchannelsetup/keepalive": self.keepalive,
                "connections/mqttcommandchannel/mqttcmdchannel/mqttcmdchannelsetup/willtopic":self.willtopic,
                "connections/mqttcommandchannel/mqttcmdchannel/mqttcmdchannelsetup/willmessage":self.willmessage,
                "connections/mqttcommandchannel/mqttcmdchannel/mqttcmdchannelsetup/securesetup/secure":self.secure,
                "connections/mqttcommandchannel/mqttcmdchannel/mqttcmdchannelsetup/securesetup/certificate_key_pem":self.certificate_key,
                "connections/mqttcommandchannel/mqttcmdchannel/mqttcmdchannelsetup/securesetup/validateservercertificate":self.validateservercertificate,
                "connections/mqttcommandchannel/mqttcmdchannel/mqttcmdchannelsetup/securesetup/trustedservercertificates":self.trustedservercertificates,
        }

    def cmd_start(self,function)-> str:
        resp=function("/connections/mqttcommandchannel/status/start")
        return resp

    def cmd_stop(self,function)-> str:
        resp=function("/connections/mqttcommandchannel/status/stop")
        return resp

    def cmd_reset(self,function)-> str:
        resp=function("/connections/mqttcommandchannel/status/reset")
        return resp


class Notification:
    def __init__(self,
                 server_ip:str ="192.168.5.10",
                 server_port:int =1883,
                 server_port_tls:int =8883,
                 user: str ="",
                 password: str =""):

        self.server_ip = server_ip
        self.server_port = server_port
        self.server_port_tls = server_port_tls
        self.user = user
        self.password = password


    def url(self, protocol,creds)-> str:
        if protocol =="mqtt" or protocol =="mqtts":
            if creds:
                crd=f"{self.user}:{self.password}@"
            else:
                crd=""
            if protocol=="mqtts":
                url = f"mqtts://{crd}{self.server_ip}:{self.server_port_tls}"
            else:
                url = f"mqtt://{crd}{self.server_ip}:{self.server_port}"
        elif protocol=="http":
            url = f"http://{self.server_ip}:{self.server_port}"
        else:
            print(f"Protocool: {protocol}not implemented ")
            url=""
        return url

    """Use examples:
    subscription1=not1.constructor(True,True,False,1,"Topic3",500,1000,10,True,False,"/monitor/add",["/iolinkmaster/port[3]/iolinkdevice/pdin"])
    subscription2=not1.constructor(False,False,False,1,"Topic4",500,1000,10,True,False,"/monitor/add",["/iolinkmaster/port[3]/iolinkdevice/pdin"])
    
    iot.request("/monitor/add",subscription1)
    iot.request("/timer[1]/counter/datachanged/subscribe",subscription2)    """


    def constructor(self,monitor:bool=True,
                    protocol: str = "mqtt",  # mqtt,mqtts, http
                    creditails:bool=False,
                    cid:int=1,
                    topic: str ="t1",
                    sample_interval:int=500,
                    notify_interval:int=1000,
                    subscribeid:int=0,
                    persist:bool=True,
                    data_change:bool=False,
                    adr:str="/monitor/add",
                    data: list =None,
                    id_number:int=1, sb_flag: bool = False):

        if monitor:
            js={"id":id_number,"recipient":f"{self.url(protocol,creditails)}/{topic}","data_points":data,"sample_interval":sample_interval,"notify_interval":notify_interval,"data_changed":data_change,"persist":persist}
        elif sb_flag == False and monitor == False:
            js = {"callback": f"{self.url(protocol, creditails)}/{topic}",
                  "datatosend": data
                  }
        else:
            # adr exapmle: "ifm-AL1590-000252500027/timer[1]/counter/datachanged/subscribe"
            js={"callbackurl":f"{self.url(protocol,creditails)}/{topic}",
                "datatosend":data,
                "subscribeid":subscribeid,
                "persist":persist}
        print(f"Notification ready: {js}")
        return js

    def remove_notification(self,function,id_number:int):
        #url - "/monitor/remove" ,data - {f"id":id_number})
        resp=function("/monitor/remove" , {f"id":id_number})
        return resp

    def add_monitor_notification(self,function,data):
        resp=function("/monitor/add", data)
        print(f"Noticfication added: {resp}")
        return resp

    def add_subscribe_notification(self,function,url:str,data:any):
        #   example: url="/timer[1]/counter/datachanged/subscribe"
        resp=function(url,data)
        print(f"Noticfication added: {resp}")
        return resp

    def get_iteam_list(self,function):
        resp=function("/monitor/getitems")
        print(f"Notification list:")
        for n in resp['data']['items']:
            print(f"-->{n}")
        return resp['data']
    def check_notification_exist(self, function, cid, adr, callbackurl):
        """
        {
        "code": "request",
        "cid": 1,
        "adr": "/timer[2]/counter/datachanged/getsubscriptioninfo",
        "data": {
            "callback": "http://192.168.5.10:1883/Topic5"
            }
        }
        """

        data={"callback": callbackurl}
        resp = function(adr, data, cid)
        print(f"Notification check: {resp}")





