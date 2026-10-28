
"""
======================================================================================
Project: Cyber Security
Module: Iot_core
File: IoT_core.py
======================================================================================
Author: Pawe Sokoowski SL3
Date: 2026-03-13
Version: 1.0

Functionality:
Http POST function.
Downloading iot tree from IOLM, creating variables buffer based on endpoints ,downloading and uploading variables values:
                variable = {
                    "identifier": identifier,
                    "adr": adr,
                    "type": fmt.get("type"),
                    "encoding": fmt.get("encoding"),
                    "namespace": fmt.get("namespace"),
                    "get": None,
                    "set": None,
                    "value": None,
                }
Downloading variables values:
**================================EXAMPLE COMMANDS====================================**
iot = IoTClient(ip=ip, tls=False, credentials=True)

def get_value(self, logical_path: str) -> Any:
fw=iot.get_value(f"{fix_host_name}/deviceinfo/swversion")

iot.iot_core() - creating variable buffer

def set_value(self, logical_path: str, value: Any) -> None:
iot.set_value(f"{fix_host_name}/devicesettings/systemtime/datetime",ts_seconds)

#iot.request(mqtt_client.client_stop())  - direct HTTP request
request(self, endpoint: str, data: Any = None) -> Dict[str, Any]
#iot.request("/connections/mqttcommandchannel/status/start")  - direct HTTP request

#iot.list_variables() - variable list print

iot.refresh_values() - refresh variables from device

def show_buffer_variable(self,path):
iot.show_buffer_variable("/processdatamaster/voltage")
"""
import requests
from typing import Any, Dict, Optional


class IoTClient:
    DEFAULT_TIMEOUT = 5

    def __init__(
        self,
        ip: str = "192.168.5.151",
        tls: bool = False,
        credentials: bool = False,
        user: str = "YWRtaW4=",
        password: str = "YWwxNTkw"# YWwxNTkw - al1590 ; password - "cGFzc3dvcmQ="
    ):
        self.ip = ip
        self.tls = tls
        self.credentials = credentials
        self.user = user
        self.password = password

        self.session = requests.Session()
        self.buffer: Optional[Dict[str, Dict[str, Any]]] = None
        self.sb=True
        self.cid=1

    # -------------------------------------------------------------

    def _base_url(self) -> str:
        return f"{'https' if self.tls else 'http'}://{self.ip}"

    def _auth_block(self) -> Dict[str, str]:
        return {
            "user": self.user,
            "passwd": self.password,
        }

    # -------------------------------------------------------------

    def request(self, endpoint: str, data: Any = None, cid:int=1) -> Dict[str, Any]:
        self.cid=cid
        payload: Dict[str, Any] = {
            "code": "request",
            "cid": self.cid,
            "adr": endpoint,
        }

        if data is not None:
            if "getdatamulti" in endpoint:
                payload["data"] = {"datatosend": data}
            elif "setdata" in endpoint:
                payload["data"] = {"newvalue": data}
            elif "setblock" in endpoint:
                print(f"Setblock:{endpoint} : {data}")
                payload["data"] = {"datatoset": data}
            elif self.sb and ("monitor/add" or "subscribe")  in endpoint:

                payload['code']=10
                payload["data"] =data
                print("PAYLOAD1",payload)
                payload['cid'] = self.cid
                self.cid+=1
            elif not self.sb  and ("subscribe"  in endpoint or "getsubscriptioninfo" in endpoint):

                payload['code']="request"
                payload["data"] =data
                print("PAYLOAD2",payload)
                payload['cid'] = self.cid
                self.cid+=1
            elif "monitor/remove" or "removedevice" or "adddevice" in endpoint:
                payload['code']="request"
                payload["data"] =data
                print("PAYLOAD3",payload)
            elif "iolreadacyclic" in endpoint:
                payload['code']=10
                payload["data"] =data
                print("PAYLOAD3",payload)

        if self.credentials:
            payload["auth"] = self._auth_block()
        print(payload)
        try:
            response = self.session.post(
                self._base_url(),
                json=payload,
                verify=False,
                timeout=self.DEFAULT_TIMEOUT,
            )
            response.raise_for_status()
            #print(f"Status:{response.status_code}")
            #print(response.json())
            if response.status_code != 200:
                print(f"Request failed with status code {response.status_code}")
            if response.json()['code']!= 200:
                print(f"Request failed with status code {response.json()}")
            return response.json()
        except requests.RequestException as exc:
            print (f"HTTP request failed: {exc}")

    # -------------------------------------------------------------
    # 🔥 GETTREE → MAPA ZMIENNYCH
    # -------------------------------------------------------------

    def iot_core(self) -> Dict[str, Dict[str, Any]]:
        if self.buffer is not None:
            print(f"Reading from buffer...........")
            return self.buffer

        tree = self.request("/gettree")
        print(f"Gettree request ->Iot core download...........")
        variables: Dict[str, Dict[str, Any]] = {}

        def walk(node: Any, path: str = "") -> None:
            if not isinstance(node, dict):
                return

            node_type = node.get("type")
            identifier = node.get("identifier")
            adr = node.get("adr")

            current_path = f"{path}/{identifier}" if identifier else path

            # ✅ ZNALEŹLIŚMY ZMIENNĄ DANYCH
            if node_type == "data" and identifier and adr:
                fmt = node.get("format", {})

                variable = {
                    "identifier": identifier,
                    "adr": adr,
                    "type": fmt.get("type"),
                    "encoding": fmt.get("encoding"),
                    "namespace": fmt.get("namespace"),
                    "get": None,
                    "set": None,
                    "value": None,
                }

                for sub in node.get("subs", []):
                    if sub.get("identifier") == "getdata":
                        variable["get"] = sub.get("adr")
                    elif sub.get("identifier") == "setdata":
                        variable["set"] = sub.get("adr")

                variables[current_path.strip("/")] = variable

            for sub in node.get("subs", []):
                walk(sub, current_path)

        walk(tree.get("data", {}))
        self.buffer = variables
        return self.buffer
    def clear_iot_core_buffer(self):
        self.buffer = None

    def iot_core_no_sb(self) -> Dict[str, Dict[str, Any]]:
        if self.buffer is not None:
            #print(f"Reading from buffer...........")
            return self.buffer

        tree = self.request("/gettree")
        print(f"Gettree request ->Iot core download...........")
        variables: Dict[str, Dict[str, Any]] = {}

        def walk(node: Any, path: str = "") -> None:
            #print(node, path)
            if not isinstance(node, dict):
                return
            #print("=======================Node detected===================")
            node_type = node.get("type")
            identifier = node.get("identifier")
            #adr = node.get("adr")
            if node_type != 'device':
                current_path = f"{path}/{identifier}" if identifier else path
            else:
                current_path = f"{path}" if identifier else f"{path}"

            # ✅ ZNALEŹLIŚMY ZMIENNĄ DANYCH
            if node_type == "data" and identifier:
                fmt = node.get("format", {})
                #print("===================Variable creator========================")
                variable = {
                    "identifier": identifier,
                    "adr": current_path,
                    "type": fmt.get("type"),
                    "encoding": fmt.get("encoding"),
                    "namespace": fmt.get("namespace"),
                    "get": None,
                    "set": None,
                    "value": None,
                }

                for sub in node.get("subs", []):
                    if sub.get("identifier") == "getdata":
                        variable["get"] = f"{current_path}/getdata"
                    elif sub.get("identifier") == "setdata":
                        variable["set"] = f"{current_path}/setdata"

                variables[f"/{current_path.strip('/')}"] = variable

            for sub in node.get("subs", []):
                walk(sub, current_path)

        walk(tree.get("data", {}))
        self.buffer = variables
        return self.buffer
    # -------------------------------------------------------------
    # 📥 ODCZYT WARTOŚCI
    # -------------------------------------------------------------
    def check_product_name(self, product_name: str):
        if product_name =="AL1590" or product_name =="AL1591" :
            self.sb = True
            print(f"Welcome in Solution Block product group :{self.sb}")
        else:

            self.sb = False
            print(f"Welcome in {product_name} product group :{self.sb}")

    def itc(self):
        if self.sb:
            return self.iot_core()
        else:
            return self.iot_core_no_sb()

    def refresh_values(self) -> None:
        print(f"Reading from device...........")
        for variable in self.itc().values():
            if variable["get"]:
                print(f"Variable '{variable['get']}' -> {variable['value']}")
                resp = self.request(variable["get"])
                variable["value"] = resp.get("data", {}).get("value")

    def refresh_value(self,var)->Any:
        resp = self.request(var["get"])
        print(f"Reading from device '{var['identifier']}' -> {resp.get('data')}")
        return resp.get("data", {}).get("value")

    def get_value(self, logical_path: str) -> Any:
        variable = self.itc().get(logical_path)

        if not variable:
            raise KeyError(f"Variable '{logical_path}' not found")

        if variable["value"] is None:
            variable["value"]=self.refresh_value(variable)

        return variable["value"]

    def show_buffer_variable(self,path):
        #print(self.itc())
        print(f"Showing buffer variable {path}......")
        var=self.itc().get(path)
        print("BUFFER", var)
        if var is None:
            print(f"Variable '{path}' not found")
        else:
            print(f"Variable {path} -> ")
            for n,v in var.items():
                print(f"---{n}: {v}")
        return var

    def search_key(self, key: str,) -> Any:
        result=[]
        print(f"Searching key: {key}")
        for name in self.itc():
            if key in  name:
                print(f"Result: {key} found in {name} :)")
                result.append(name)
            if result==None:
                print(f"Result: {key} not found :)")
        return result

    # -------------------------------------------------------------
    # 📤 ZAPIS WARTOŚCI
    # -------------------------------------------------------------

    def set_value(self, logical_path: str, value: Any) -> None:
        variable = self.itc().get(logical_path)
        if not variable:
            print (f"Variable :{variable} , path:'{logical_path}' not found")

        elif not variable["set"]:
            print (f"Variable :{variable} , path:'{logical_path}' is read-only")
        #print(f"Setting new value to {logical_path}, setdata path:{variable['set']}, value :{value}")
        else:
            self.request(variable["set"], value)
            variable["value"] = value

    # -------------------------------------------------------------
    # 🔍 NARZĘDZIA
    # -------------------------------------------------------------

    def list_variables(self) -> None:
        for name, var in self.itc().items():
            rw = "RW" if var["set"] else "RO"
            print(f"{name} [{rw}] -> {var['type']}")