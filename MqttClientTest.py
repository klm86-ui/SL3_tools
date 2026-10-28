import paho.mqtt.client as mqtt
import json
import time

class Mqtt_client:
    def __init__(self, broker_address: str, broker_port: int, cmd_topic:str,cmd_reply_topic: str):
        self.broker_address = broker_address
        self.broker_port = broker_port

        self.client = mqtt.Client()
        self.client.username_pw_set("pawel", "al1590")

        self.subscriptions = []
        self.password ="YWwxNTkw"
        # ✅ PODPINASZ CALLBACKI TU
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.cmd_topic = cmd_topic
        self.cmd_reply_topic = cmd_reply_topic
        self.cmd_response_counter=0
        self.notification_counter=0
        self.request_start_time=0.0
        self.request_current_time=0.0
        self.request_elapsed_time=0.0
        self.summary_elapsed_time=[]

        self.test_time=30.0
        self.request_interval=0.5
        self.test_start_time=0.0
        self.test_current_time = 0.0
        self.packets_ok = 0
        self.packets_send = 0
        self.packets_error = 0

        self.cmd_variant = False
    # ---------------- SUBSKRYPCJE ----------------

    def subs(self, subscriptions):
        self.subscriptions = subscriptions

    # ---------------- CALLBACKI ----------------

    def on_connect(self, client, userdata, flags, rc):
        print("MQTT BROKER ONLINE, code:", rc)

        if rc == 0:
            for topic in self.subscriptions:
                client.subscribe(topic)
                print(f"Subscribed: {topic}")

    def on_message(self, client, userdata, msg):
        data = msg.payload.decode()
        print(f"Msg from topic:{msg.topic}")

        try:
            daneJson = json.loads(data)
            self.notification_counter += 1
            if msg.topic == self.cmd_reply_topic and self.cmd_variant:
                self.cmd_response_counter+=1
                self.request_elapsed_time = time.time() - self.request_start_time
                self.summary_elapsed_time.append(self.request_elapsed_time)
                print(f"MQTT CMD raw: {data}")
                print(f"MQTT topic:{daneJson.get('adr')} data:, {daneJson.get('data', {})}")
            elif not self.cmd_variant:
                print(f"MQTT notification, raw: {data}")
                print(f"MQTT topic:{daneJson.get('adr')} data:, {daneJson.get('data', {})}")

        except Exception:
            print(f"MQTT raw: {data}")

    # ---------------- POŁĄCZENIE ----------------

    def connect(self):
        self.broker_address = input("Set broker IP address, or press ENTER for default cmd config:192.168.5.10") or self.broker_address
        self.broker_port = int(input("Set broker PORT, or press ENTER for default cmd config :1883") or  self.broker_port)
        try:
            self.client.connect(self.broker_address, self.broker_port, 60)
            self.client.loop_start()   # bardzo ważne
        except Exception:
            print("Broker offline")
    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()
        print("MQTT BROKER OFFLINE")
    # ---------------- PUBLIKOWANIE ----------------

    def publish(self, topic, payload):
        self.client.publish(topic, payload)

    def cmd(self, cmd_topic:str,data_point:str, data ):
        print(f"CMD request:{cmd_topic},data:{data}")
        if data is None:
            self.publish(cmd_topic, json.dumps({"code": "request", "cid": 1, "adr": data_point, 'auth':{"user": "YWRtaW4=", "passwd": self.password}}))
        else:
            self.publish(cmd_topic,json.dumps({"code": "request", "cid": 1, "adr": data_point, "data": {"newvalue": data},'auth':{"user": "YWRtaW4=", "passwd": self.password}}))
    def test(self, variant):
        self.test_time=30.0
        self.request_interval=0.5
        self.test_start_time=0.0
        self.test_current_time=0.0

        self.packets_ok=0.0
        self.packets_send=0.0
        self.packets_error=0.0
        calculated_notifications=0.0
        time.sleep(0.5)
        self.test_time = float(input("Set test interval or press ENTER for default 30 sec: ") or 30.0)
        self.request_interval = float(input("Set request interval or press ENTER for default 0.1 sec: ") or 0.1)
        if variant == "cmd":
            cmd_endpoint = input("Set cmd endpoint or press enter for [/devicestatus/temperature/cpu/getdata]") or "/devicestatus/temperature/cpu/getdata"
            print(f"MQTT CMD test started : {self.test_time} seconds")
            self.cmd_variant=True
        else:
            cmd_endpoint = ""
            self.cmd_variant=False
            print("MQTT notification test in progress")
        self.test_start_time = time.time()
        self.request_start_time = time.time()
        self.connect()
        while self.test_current_time < self.test_time:
            self.test_current_time = time.time() - self.test_start_time
            if variant=="cmd":
                self.cmd_test(cmd_endpoint)

        calculated_notifications =self.test_time / self.request_interval
        print(
            f"MQTT CMD test finished.\nCalculated notifications: {calculated_notifications}\nRecived notifications: {self.notification_counter}\nMissing notifications: {calculated_notifications-self.notification_counter}\nMsg send: {self.packets_send}\nMsg recived:{self.cmd_response_counter}\nMsg error: {self.packets_error}\nMsg missing {self.packets_send - self.cmd_response_counter}\nRequest times:{sorted(self.summary_elapsed_time)}")
        self.test_current_time = 0.0
        self.packets_ok = 0
        self.packets_send = 0
        self.packets_error = 0
        self.cmd_response_counter = 0
        self.notification_counter = 0
        self.request_elapsed_time = []
    def notification_test(self):
        print("MQTT notification test in progress")
    def cmd_test(self, datapoint):

        self.request_current_time = time.time() - self.request_start_time
        if self.request_current_time > self.request_interval:
            self.request_start_time = time.time()
            self.cmd(self.cmd_topic,datapoint,None)
            self.packets_send += 1


