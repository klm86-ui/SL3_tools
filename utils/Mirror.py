
"""
{
    "code": "request",
    "cid": 1,
    "adr": "/device_management/adddevice",
    "data": {
        "uri": "http://192.168.5.131:80",
        "alias": "al13",
        "persist": true
    }
}
{
    "code": "request",
    "cid": 1,
    "adr": "/device_management/removedevice",
    "data": {
        "adr": "ifm-AL1590-000252500027/remote/{alias}"
    }
}

"""

class Mirror:

    def add_device(self,ip:str, alias:str,function):
        url=f"http://{ip}:80"
        data={"uri": url,"alias": alias, "persist": True}
        resp=function("/device_management/adddevice" ,data)
        return resp
    def remove_device(self,host_name,alias:str,function):
        #data={"alias": alias} { "adr": "ifm-AL1590-000252500027/remote/al1300"}
        data={ "adr": f"{host_name}/remote/{alias}"}
        resp=function("/device_management/removedevice", data)
        return resp
    def get_device_lit(self,function):
        resp=function("/device_management/getdevicelist")
        return resp

