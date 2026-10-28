
"""
======================================================================================
Project: Cyber Security
Module: main
======================================================================================
Author: Pawe Sokoowski SL3
Date: 2026-03-13
Version: 1.0
Main script

Functionality:
Main functions handler
**================================EXAMPLE COMMANDS====================================**
Standard settings
#set_setings(std_conf.timers())

Mqtt settings
#iot.request(mqtt_client.client_stop())
#set_setings(mqtt_client.client_conf())
#set_setings(cmd.cmd_conf())
#iot.request(mqtt_client.client_start())
#iot.request(cmd.cmd_stop())
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

mirror=Mirror()
mirror.add_device("192.168.5.131","AL13xx",iot.request)
print(mirror.get_device_lit(iot.request))
mirror.remove_device(fix_host_name,"AL13xx",iot.request)

display_values()
display_buffer_variable()
iot.refresh_values()
display_buffer_variable()
08.10.2026  - dodano projekt do GitHub;
"""
from MqttConf import Mqtt,Cmd,Notification
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from utils.Iot_core import IoTClient
import time
from utils.Mirror import Mirror
from StandardConf import Std_conf
from datetime import datetime
from openpyxl import Workbook, load_workbook
import os
from HttpTest import http_test
from MqttClientTest import Mqtt_client
import MqttConf
import base64
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
def create_file(keyList,ex_path:str,excel_name:str):
    now = datetime.now()
    excel_file = os.path.join(ex_path, excel_name)

    if not os.path.exists(excel_file):
        wb = Workbook()
        ws = wb.active
        ws.title = "Mqtt test AL1302"
        ws.append(keyList)
        wb.save(excel_file)
        print(f"-->{excel_name} file created")
    print(f"-->Saving to {excel_name}.")
    return excel_file

def save_settings_to_file(listx,path,name):
    adr=None
    value=None
    keyList=["Itema","value"]


    try:
        wb = load_workbook(create_file(keyList,path,name))
        ws = wb.active
        for n in listx.values():
            if n['set'] != None:
                adr=(n['adr'])
                if isinstance(n['value'], dict) or isinstance(n['value'], list):

                    result=[adr]
                    for vx in n['value']:
                        result.append(vx)
                else:
                    value=(n['value'])
                    result=[adr , value]
                ws.append(result)
        wb.save(create_file(keyList,path,name))
        wb.close()
        print(f"-->Settings saved")
    except Exception as e:
        print(f"RESULT4={result}")
        print("-->XCL file creating error:", e)

def read_settings_from_file(path, col_key, col_value, sheet_name=None):
    excel_file = os.path.join(path, sheet_name)
    print(f"-->Reading settings from file: {excel_file}")
    separator()
    try:
        wb = load_workbook(excel_file)
        ws = wb.active
        data = {}
        for row in ws.iter_rows(min_row=2):  # pomija nagłówki
            key = row[col_key - 1].value
            value = row[col_value - 1].value
            if key is not None:
                data[key] = value
        wb.close()
        print(data)
        return data
    except Exception as e:
        print(f"XCL file {path} - {sheet_name}reading error:", e)

def separator():
    print("")
    print("========================================================================================")
    print("")

def display_filtered_values(key, iot):
    separator()
    for n in iot.search_key(key):
        print(f"\n-->Data: {n} \nValue: {iot.get_value(n)}")

def set_setings(presetingsList, fix_host_name,iot):
    separator()
    for endpoint, value in presetingsList.items():
        if fix_host_name.lower() in endpoint.lower():
            print(f"-->Host founded ,Set - {endpoint} to: {value}")
            iot.set_value(f"{endpoint}", value)

        else:
            iot.set_value(f"{fix_host_name}/{endpoint}", value)
            print(f"-->Setting {endpoint} to {value}")

def display_values(iot):
    separator()
    key = ""
    while key != "exit":
        separator()
        key = ""
        key = input(
            'Enter filter name :iolinkmaster / timer / network /connection / port[1] / deviceinfo / devicetag / procesdatamaster: \nor type - exit, \nto refresh values type refresh')
        display_filtered_values(key,iot)
        if key=='refresh':
            iot.refresh_values()
def display_buffer_variable(iot,fix_host_name):

    print(f"-->Buffer editor of {fix_host_name}")
    key = ""

    while key != "exit":
        separator()
        var = None
        key = input('Enter path:  /processdatamaster/voltage: or type - exit') or "/processdatamaster/voltage"
        if iot.sb:
            if fix_host_name.lower() in key.lower():
                nkey = key.replace(fix_host_name.lower(), fix_host_name)
                print(f"-->Key changed: {nkey}")
                var=iot.show_buffer_variable(f"{nkey}")
            else:
                var=iot.show_buffer_variable(f"{fix_host_name}{key}")
        else:
            var = iot.show_buffer_variable(f"{key}")
        if var !=None:
            key = input('Edit value y/n or exit - from buffer editor')
            if key == "y":
                if var['set'] != None:
                    key = input(f"Value: {var['value']}\nType:{var['type']}\nNew value:")
                    print(f"-->Set {var['adr']} to {key}")
                    if var['type']=="number":
                        iot.set_value(var['adr'], int(key))
                    else:
                        iot.set_value(var['adr'], key)
                else:
                    print("-->Only read variable")

def notifications_gen(notify_interval,sample_interval, not1,iot,mqtt_client):
    """Notification creator - different adr for monitor or subscription method """

    not1.user = "pawel"
    not1.password = "haslo"
    s1 = not1.constructor(True, "mqtt", False, 1, "Windows_TLS_1", sample_interval, notify_interval, 10,
                                     True, False, "/monitor/add", ["/iolinkmaster/port[1]/iolinkdevice/pdin","/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/Temperature","/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/Fatigue__v-RMS_x-Axis_",
                                     "/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/Fatigue__v-RMS_y-Axis_","/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/Fatigue__v-RMS_z-Axis_",
                                                                   "/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/Fatigue__v-RMS_Magnitude_","/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/Impact__a-Peak_x-Axis_",
                                                                   "/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/Impact__a-Peak_y-Axis_","/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/Impact__a-Peak_z-Axis_",
                                                                   "/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/Impact__a-Peak_Magnitude_","/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/Friction__a-RMS_x-Axis_",
                                                                   "/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/Friction__a-RMS_y-Axis_","/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/Friction__a-RMS_z-Axis_",
                                                                   "/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/Friction__a-RMS_Magnitude_","/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/Device_Status",
                                                                   "/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/Unbalance___Bearing","/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/v-ou1","/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/OUT2",
                                                                   "/iolinkmaster/port[1]/iolinkdevice/pdin_interpreted/Process_Data_Input_Output/OUT1"], 3,iot.sb)

   #  not1.add_monitor_notification(iot.request, subscription11)
    not1.add_monitor_notification(iot.request, s1)

    '''!!!!!!!!!!!!! dolozyc kolejne numerowanie lub przekazywanie cid podczas tworzenia subskrypcji dla AL13 urzadzen oraz SB /subscribe'''
    #not1.add_subscribe_notification(iot.request, "/timer[1]/counter/datachanged/subscribe", subscription4)
    #not1.add_subscribe_notification(iot.request, "/timer[2]/counter/datachanged/subscribe", subscription5)
    print(f"SB flag = {iot.sb}")
    if iot.sb:
        not1.get_iteam_list(iot.request)
    mqtt_client.client_stop(iot.request,iot.sb)
    mqtt_client.client_start(iot.request,iot.sb)
    mqtt_client.client_status(iot.request,iot.sb)
    not1.check_notification_exist(iot.request, 1, "/timer[1]/counter/datachanged/getsubscriptioninfo","mqtt://192.168.5.10:1883/Topic4")
    not1.check_notification_exist(iot.request,2,"/timer[2]/counter/datachanged/getsubscriptioninfo","http://192.168.5.10:1883/Topic5")

def notifications_remove(not1,iot):
    not1.remove_notification(iot.request,1)
    not1.remove_notification(iot.request,2)
    not1.remove_notification(iot.request,3)
    not1.remove_notification(iot.request,4)
    not1.remove_notification(iot.request,5)

def mirror_add(mirror,iot):
    #Mirror / Remote setings
    mirror.add_device("192.168.5.131","AL13xx",iot.request)
    mirror.add_device("192.168.5.141","AL1402",iot.request)
    mirror.add_device("192.168.5.191","AL1901",iot.request)
    print(f"Remote devices list:\n{mirror.get_device_lit(iot.request)['data']}")
def mirror_remove(mirror, fix_host_name,iot):

    mirror.remove_device(fix_host_name,"AL13xx",iot.request)
    mirror.remove_device(fix_host_name,"AL1402",iot.request)
    print(f"Remote devices list:\n{mirror.get_device_lit(iot.request)['data']}")
def mirror_list(mirror, iot):
    print(f"Remote devices list:\n{mirror.get_device_lit(iot.request)['data']}")
def daisy_chain_test(iot):
    x_range = int(input("Set unit number") or "6")
    x_range+=1
    print(f"Daisy chain test in progress...")
    ip_mem=iot.ip
    code=0
    while code!=200:
        try:
            code= iot.request(f"/deviceinfo/swrevision/getdata")['code']
            print(f"Waiting for Linux startup - code:{code}")
            time.sleep(0.5)
        except:
            print("...............")
    time.sleep(1)
    result=[]
    for n in range(1,x_range):
        ip = "192.168.5.15"
        ip=ip+str(n)
        print(f"Connecting with {ip}")
        iot.ip = ip
        req_result=(iot.request(f"/iolinkmaster/port[1]/iolinkdevice/pdin/getdata"))
        print(req_result)
        if req_result['code']==404:
            print(f"\n==============Device :{ip} failure!=====================\n")
        result.append({ip:req_result['code']})
        time.sleep(0.5)
    iot.ip=ip_mem
    print(result)
def connection(iot,mqtt_client,cmd,std_conf,pdin_test,mqtt_test,fix_host_name,fw):

    ip = input("Set Ip address or press ENTER for default [192.168.5.151]: ") or "192.168.5.151"
    password = input('Type password or ENTER for default:password') or "password"
    print(f"Connecting with: {ip}")
    print("password", base64.b64encode(password.encode("utf-8")))
    # Object constructor:
    mqtt_test.password = iot.password
    iot.ip=ip
    serial_number = iot.request(f"/deviceinfo/serialnumber/getdata")
    product_code = iot.request(f"/deviceinfo/productcode/getdata")
    iot.check_product_name(product_code['data']['value'])
    """Building fixed host name witch is part of url"""
    # for n,v in iot.itc().items():
    #   print(n)
    #  print(v)
    print("Iot core in progress")
    iot.clear_iot_core_buffer()
    if iot.sb:
        fix_host_name = f"ifm-{product_code['data']['value']}-{serial_number['data']['value']}"
        fw = iot.get_value(f"{fix_host_name}/deviceinfo/swversion")

    else:
        fw = iot.get_value(f"/deviceinfo/swrevision")
    print("Iot core created")
    separator()
    print(f"                    Connected --> Product code:{product_code['data']['value']}")  # Product code
    print(f"                    Firmware: {fw}")  # firmware
    separator()

    if iot.sb:
        time_set(iot, fix_host_name)

    separator()
    # status = iot.get_value(f"{fix_host_name}/devicetag/applicationtag")
    return fix_host_name
def iot_core_buffer(iot):
    print(iot.itc())

def function_choice():
    separator()
    key = ""

    iot = IoTClient(ip="192.168.5.151", tls=False, credentials=True)
    mqtt_client = Mqtt()
    cmd = Cmd()
    std_conf = Std_conf()
    pdin_test = http_test(30.0, 0.5)
    mqtt_test = Mqtt_client(cmd.server_ip, cmd.server_port, cmd.cmd_topic, cmd.cmd_reply_topic)
    fix_host_name = ""
    fw = ""
    not1 = Notification()
    mirror = Mirror()
    fix_host_name=connection(iot, mqtt_client, cmd, std_conf, pdin_test, mqtt_test, fix_host_name, fw)

    while key != "close":
        separator()
        key = input('Chose the function:\n Refresh actual values - 1'
                    '\n Edit buffor - 2'
                    '\n Search key values -3'
                    '\n Load configuration from file - 4'
                    '\n Load configuration from python script - 5'
                    '\n Save settings to file - 6'
                    '\n Load notifications - 7'
                    '\n Remove notifications - 8'
                    '\n Add mirror device - 9'
                    '\n Remove device - 10'
                    '\n Notifications list - 11'
                    '\n Remote devices list - 12'
                    '\n Change Iot IP address - 13'
                    '\n Http proces data test - 14'    
                    '\n Mqtt test - 15'   
                    '\n HTTP server (Notifications) test - 16'   
                    '\n New master connection - 17'   
                    '\n Show iot core buffer - 18' 
                    '\n Daisy chain test - 19' 
                    '\n-->')
        if key=="1":
            iot.refresh_values()
        if key=="2":
            display_buffer_variable(iot,fix_host_name)
        if key=="3":
            display_values(iot)
        if key=="4":
            set_setings(read_settings_from_file(r"C:\Praca",1,2,f"settings.xlsx"),fix_host_name,iot)
        if key=="5":
            """Standard settings"""
            set_setings(std_conf.timers(),fix_host_name,iot)
            set_setings(std_conf.network(),fix_host_name,iot)
            std_conf.set_network_address(iot.request)
            set_setings(std_conf.deviceSettingsTime(),fix_host_name,iot)
            set_setings(std_conf.deviceTag(),fix_host_name,iot)
            set_setings(std_conf.iolinkmaster(),fix_host_name,iot)
            set_setings(std_conf.iolinkDevice(),fix_host_name,iot)
            set_setings(std_conf.validation(),fix_host_name,iot)
            """Mqtt settings"""
            mqtt_client.client_stop(iot.request,iot.sb)
            set_setings(mqtt_client.client_conf(),fix_host_name,iot)
            mqtt_client.client_start(iot.request,iot.sb)
            cmd.cmd_stop(iot.request)
            set_setings(cmd.cmd_conf(),fix_host_name,iot)
            cmd.cmd_start(iot.request)
        if key=="6":
            save_settings_to_file(iot.itc(), r"C:\Praca", f"settings.xlsx")
        if key=="7":
            ninterval = int(input("Set notify interval or press enter for default : 500ms") or 100)
            sinterval = int(input("Set sample interval or press enter for default : 500ms") or 20)
            not1.server_ip=input("Set server Ip address or press ENTER for default [192.168.5.10]: ") or "192.168.5.10"
            not1.server_port = int(input("Set server port or press ENTER for default:80 ") or 80)
            notifications_gen(ninterval,sinterval, not1, iot,mqtt_client)
        if key=="8":

            notifications_remove(not1,iot)
        if key=="9":
            mirror_add(mirror,iot)
        if key=="10":
            mirror_remove(mirror, fix_host_name,iot)
        if key=="11":
            not1.get_iteam_list(iot.request)
        if key=="12":
            mirror_list(mirror, iot)
        if key=="13":
            std_conf.network_address["address"]= input("Set Ip address or press ENTER for default [192.168.5.151]: ") or "192.168.5.151"
            if fw=="1.7.0.0" or "1.7.0.1":
                print(f"New visualization firmware: {fw}, changing network commands to SETNETWORK")
                std_conf.network_address_setnetwork_data["address"][0]["address"]= std_conf.network_address["address"]
                std_conf.set_network_address_new_visu(iot.request)
            else:
                std_conf.set_network_address(iot.request)
            iot.ip=std_conf.network_address["address"]
        if key=="14":
            pdin_test.process_data_test(1,iot.request)
        if key=="15":

            mqtt_test.subs(["t1","Windows_TLS_1",mqtt_test.cmd_reply_topic,]) #"""Subscriptions topics list""
            test_variant = input("Type [cmd] for command channel mqtt test or press ENTER for notification test]") or "notification"
            cmd_settings=input("Type [set] for configure device command channel settings or press ENTER to skip]") or "skip"
            if test_variant == "cmd":
                if cmd_settings=="set":
                    cmd.cmd_stop(iot.request)
                    set_setings(cmd.cmd_conf(),fix_host_name,iot)
                    cmd.cmd_start(iot.request)
            mqtt_test.test(test_variant)
            mqtt_test.disconnect()
        if key=="16":
            pdin_test.http_notifications_test()
        if key=="17":
            iot.clear_iot_core_buffer()
            fix_host_name=connection(iot,mqtt_client,cmd,std_conf,pdin_test,mqtt_test,fix_host_name,fw)
        if key == "18":
            iot_core_buffer(iot)
        if key == "19":
            daisy_chain_test(iot)
        else:
            print(f"-->{key} key not found.")

def time_set(iot,fix_host_name):
    """ Actual time to unix time stamp conversion"""
    ts_seconds = int(time.time_ns() / 1000000)
    print(f"Unix time stamp :{ts_seconds}")
    iot.set_value(f"{fix_host_name}/devicesettings/systemtime/datetime", ts_seconds)
    actual_time = iot.get_value(f"{fix_host_name}/devicesettings/systemtime/datetime")
    print(f"Actual time:{actual_time}")
"""*****************************************************************************************************************"""
"""                                                     Main program                                                """
"""*****************************************************************************************************************"""

separator()
print("                                 Hello in Support level III Tools ")
print("                                         Version V1.0")
separator()




    # Lista zmiennych
    #iot.list_variables()
separator()
function_choice()


