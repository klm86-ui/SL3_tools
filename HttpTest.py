
import time
import threading
from flask import Flask, request, jsonify
import ssl
import requests
SetPin2State={"Port1Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[1]/iqout/setdata","data":{"newvalue":1}},
                "Port2Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[2]/iqout/setdata","data":{"newvalue":1}},
                "Port3Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[3]/iqout/setdata","data":{"newvalue":1}},
                "Port4Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[4]/iqout/setdata","data":{"newvalue":1}},
                "Port5Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[5]/iqout/setdata","data":{"newvalue":1}},
                "Port6Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[6]/iqout/setdata","data":{"newvalue":1}},
                "Port7Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[7]/iqout/setdata","data":{"newvalue":1}},
                "Port8Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[8]/iqout/setdata","data":{"newvalue":1}},
                 }
ResetPin2State={"Port1Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[1]/iqout/setdata","data":{"newvalue":0}},
                "Port2Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[2]/iqout/setdata","data":{"newvalue":0}},
                "Port3Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[3]/iqout/setdata","data":{"newvalue":0}},
                "Port4Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[4]/iqout/setdata","data":{"newvalue":0}},
                "Port5Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[5]/iqout/setdata","data":{"newvalue":0}},
                "Port6Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[6]/iqout/setdata","data":{"newvalue":0}},
                "Port7Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[7]/iqout/setdata","data":{"newvalue":0}},
                "Port8Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[8]/iqout/setdata","data":{"newvalue":0}},
                 }

GetPin2State={"Port1Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[1]/iqout/getdata",'auth':{"user": "YWRtaW4=", "passwd": "cGFzc3dvcmQ="}},
                "Port2Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[2]/iqout/getdata",'auth':{"user": "YWRtaW4=", "passwd": "cGFzc3dvcmQ="}},
                "Port3Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[3]/iqout/getdata",'auth':{"user": "YWRtaW4=", "passwd": "cGFzc3dvcmQ="}},
                "Port4Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[4]/iqout/getdata",'auth':{"user": "YWRtaW4=", "passwd": "cGFzc3dvcmQ="}},
                "Port5Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[5]/iqout/getdata",'auth':{"user": "YWRtaW4=", "passwd": "cGFzc3dvcmQ="}},
                "Port6Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[6]/iqout/getdata",'auth':{"user": "YWRtaW4=", "passwd": "cGFzc3dvcmQ="}},
                "Port7Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[7]/iqout/getdata",'auth':{"user": "YWRtaW4=", "passwd": "cGFzc3dvcmQ="}},
                "Port8Pin2":{"code": "request","cid": 1,"adr": "/iolinkmaster/port[8]/iqout/getdata",'auth':{"user": "YWRtaW4=", "passwd": "cGFzc3dvcmQ="}},
                 }
class http_test:
    def __init__(self,
                 test_time:float=10.0,
                 request_interval:float=0.5,
                 ):
        self.test_time=test_time
        self.request_interval=request_interval
        self.test_start_time=0.0
        self.test_current_time=0.0
        self.request_start_time=0.0
        self.request_current_time=0.0
        self.request_elapsed_time=0.0
        self.packets_ok=0.0
        self.packets_send=0.0
        self.packets_error=0.0
        self.summary_elapsed_time=[]

    def process_data_test(self,port_number,http_request_function):
        self.test_time = float(input("Set test interval or press ENTER for default 30 sec: ") or 30.0)
        self.request_interval = float(input("Set request interval or press ENTER for default 0.5 sec: ") or 0.5)
        acyclic=input("For procesdata test press p, for acyclic data test press a, or Enter for default: procesdata test ") or "p"
        if acyclic=="a":
            index_number=int(input("Chose index number, or Enter for default: 24 ") or 24)
            subindex_number=int(input("Chose subindex number, or Enter for default: 0 ") or 0)
        print(f"Http test started : {self.test_time} seconds")
        self.test_start_time = time.time()
        self.request_start_time = time.time()

        while self.test_current_time<self.test_time:
            self.test_current_time = time.time() - self.test_start_time
            self.request_current_time=time.time()-self.request_start_time

            if self.request_current_time>self.request_interval:
                self.request_start_time=time.time()
                if acyclic=="p":
                    response=http_request_function(f"/iolinkmaster/port[{port_number}]/iolinkdevice/pdin/getdata",0)
                if acyclic=="a":
                    response = http_request_function(f"/iolinkmaster/port[{port_number}]/iolinkdevice/iolreadacyclic", {"index": index_number, "subindex": subindex_number})

                try:
                    print(f"Code: {response['code']}, Data:{response['data']}")
                except:
                    print(f"Msg error: Response: {response}")
                self.request_elapsed_time=time.time()-self.request_start_time
                self.summary_elapsed_time.append(self.request_elapsed_time)
                self.packets_send+=1
                if response['code']==200:
                    self.packets_ok+=1
                else:
                    self.packets_error+=1

                print(f"Http request time = {self.request_elapsed_time}")
        if acyclic=="p":
            print(f"Proces data test summary:")
        else:
            print(f"Acyclic data test summary:")
        print(f"Http test finished.\nPackets send: {self.packets_send}\nPackets ok:{self.packets_ok}\nPackets error: {self.packets_error}\nPackets missing {self.test_time/self.request_interval-self.packets_ok}\nRequest times:{sorted(self.summary_elapsed_time)}")
        self.test_current_time=0.0
        self.packets_ok=0
        self.packets_send=0
        self.packets_error=0
        self.request_elapsed_time=[]

    def http_notifications_test(self):


        # -----------------------------
        # KONFIGURACJA
        # -----------------------------
        # True = HTTPS, False = HTTP
        listen_port = int(input("Set server port or ENTER for default: 80 ") or 80)
        measurement_time = int(input("Set test time [sec] or ENTER for default: 60 ") or 60)
        packet_interval = float(input("Set notification interval [sec] for packets send amount or ENTER for default: 0.1 ") or 0.1)
        multiplayer = int(input("Set multiplayer for recived packets calculation ( number of notifications) or ENTER for default: 8 ") or 8)
        topic_buffer=["/http","/http_s","/h1","/h2","/h3","/h4","/h5","/h6","/h7","/h8"]
        https=int(input("For HTTPS press 1 or ENTER for default:0 ") or 0)
        ix=1
        app = Flask(__name__)
        for n in topic_buffer:
            input(f"Write http endpoint (topic) nr:{ix}, or press Enter for default: /h{ix}" or f"/h{ix}")
            ix = +1
            print(f"N:{n}")

        print(f"========Server parmeters:\nPort:{listen_port}\nMeasurment time:{measurement_time}\nPacket interval:{packet_interval}\nMultiplayer:{multiplayer}\ntopic_buffer:{topic_buffer}\nhttps:{https}")

        # -----------------------------
        # ZMIENNE GLOBALNE
        # -----------------------------
        packet_count = 0
        measurement_active = False

        # -----------------------------
        # ENDPOINT ODBIERAJĄCY JSON
        # -----------------------------
        @app.route(topic_buffer[0], methods=["POST"])
        @app.route(topic_buffer[1], methods=["POST"])
        @app.route(topic_buffer[2], methods=["POST"])
        @app.route(topic_buffer[3], methods=["POST"])
        @app.route(topic_buffer[4], methods=["POST"])
        @app.route(topic_buffer[5], methods=["POST"])
        @app.route(topic_buffer[6], methods=["POST"])
        @app.route(topic_buffer[7], methods=["POST"])
        def receive_data():
            global packet_count, measurement_active

            if measurement_active:
                try:
                    data = request.get_json()
                    print("DATA:", data)
                    packet_count += 1
                    return jsonify({"status": "OK"}), 200
                except Exception:
                    return jsonify({"error": "Invalid JSON"}), 400
            else:
                return jsonify({"status": "Measurement not active"}), 200

        # -----------------------------
        # FUNKCJA POMIARU
        # -----------------------------
        def start_measurement():
            global packet_count, measurement_active

            packet_count = 0
            measurement_active = True

            print(f"Rozpoczynam pomiar na {measurement_time} sekund...")
            time.sleep(measurement_time)

            measurement_active = False
            print("Pomiar zakończony.")

            expected_packets = (measurement_time / packet_interval) * multiplayer

            print("\n--- PODSUMOWANIE ---")
            print(f"Odebrane pakiety: {packet_count}")
            print(f"Oczekiwana liczba pakietów: {expected_packets:.2f}")
            print(f"Różnica: {packet_count - expected_packets:.2f}")

        # -----------------------------
        # START SERWERA
        # -----------------------------
        def run_server():
            if https:
                print("Serwer działa w trybie HTTPS")
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain("certs/Cert.crt", "certs/Key.pem")
                app.run(host="192.168.5.10", port=listen_port, ssl_context=context,use_reloader=False)
                # app.run(host="192.168.5.10", port=LISTEN_PORT, ssl_context=context)
            else:
                print("Serwer działa w trybie HTTP")
                app.run(host="192.168.5.10", port=listen_port,use_reloader=False)

        from flask import request


        @app.route('/shutdown', methods=['POST'])
        def shutdown():
            func = request.environ.get('werkzeug.server.shutdown')
            if func:
                func()
                return 'Server shutting down...'
            else:
                return 'Shutdown not available', 500
        # -----------------------------
        # GŁÓWNY PROGRAM
        # -----------------------------
        # uruchamiamy serwer w osobnym wątku
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # czekamy aż serwer się uruchomi
        time.sleep(5)
        # start pomiaru
        start_measurement()
        print("Koniec pomiaru — zamykam")
        import os
        os._exit(0)
