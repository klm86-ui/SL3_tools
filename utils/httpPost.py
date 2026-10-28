"""
httpPost
Script for http comunications via REST API

Functionality:


Author: Pawe Sokolowski SL3
Company: ifm ecolink
Date: 2026-03-13
Version: 1.0
ProjectŁ Cyber security
**EXAMPLE COMMANDS**

"""
"""-----------Imports-----------"""

from enum import Enum
import json
from typing import Any, Dict, List, Optional
import requests


class IoTClient:
    DEFAULT_TIMEOUT = 5

    def __init__(
        self,
        ip: str = "192.168.5.151",
        tls: bool = False,
        credentials: bool = False,
        user: str = "YWRtaW4=",
        password: str = "cGFzc3dvcmQ=",
    ):
        self.ip = ip
        self.tls = tls
        self.credentials = credentials
        self.user = user
        self.password = password

        self.buffer: Optional[Dict[str, List[str]]] = None
        self.session = requests.Session()

    # ------------------------------------------------------------------

    def _base_url(self) -> str:
        protocol = "https" if self.tls else "http"
        return f"{protocol}://{self.ip}"

    def _auth_block(self) -> Dict[str, str]:
        return {"user": self.user, "passwd": self.password}

    # ------------------------------------------------------------------

    def request(self, endpoint: str, data: Any = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "code": "request",
            "cid": 1,
            "adr": endpoint,
        }

        if data is not None:
            if "getdatamulti" in endpoint:
                payload["data"] = {"datatosend": data}
            elif "setdata" in endpoint:
                payload["data"] = {"newvalue": data}
            elif "setblock" in endpoint:
                payload["data"] = {"datatoset": data}

        if self.credentials:
            payload["auth"] = self._auth_block()

        try:
            response = self.session.post(
                self._base_url(),
                json=payload,
                verify=False,
                timeout=self.DEFAULT_TIMEOUT,
            )
            response.raise_for_status()
            print(f"Status:{response.status_code}")
            return response.json()

        except requests.RequestException as exc:
            raise RuntimeError(f"HTTP request failed: {exc}") from exc

    # ------------------------------------------------------------------

    def iot_core(self) -> Dict[str, List[str]]:
        if self.buffer is not None:
            return self.buffer

        tree = self.request("/gettree")

        self.buffer = {
            "adr": [],
            "adrGetdata": [],
            "adrSetdata": [],
        }

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                adr = node.get("adr")
                if isinstance(adr, str):
                    if "getdata" in adr:
                        self.buffer["adrGetdata"].append(adr)
                    elif "setdata" in adr:
                        self.buffer["adrSetdata"].append(adr)
                    else:
                        self.buffer["adr"].append(adr)

                for value in node.values():
                    walk(value)

            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(tree)
        return self.buffer

    # ------------------------------------------------------------------

    def get_data(self, endpoints: List[str], keyword: str = "network") -> List[Dict[str, Any]]:
        results = []

        for endpoint in endpoints:
            if keyword not in endpoint:
                continue

            response = self.request(endpoint)
            data = response.get("data", {})
            value = data.get("value", data)
            print(f">>> {endpoint}: {value}")
            results.append({endpoint: value})

        return results

    # ------------------------------------------------------------------

    def settings_uploader(self, endpoints: List[str], settings: Dict[str, Dict[str, Any]]) -> None:
        for name, cfg in settings.items():
            value = cfg.get("value")
            if value is None:
                continue

            for endpoint in endpoints:
                if name in endpoint:
                    self.request(endpoint, value)





















