"""
GetTree
Script for http comunications via REST API

Functionality:
Download Iot core tree , and searching agress objests inside.

Author: Pawe Sokoowski SL3
Company: ifm ecolink
Date: 2026-03-13
Version: 1.0
ProjectŁ Cyber security
**EXAMPLE COMMANDS**

"""
from utils.httpPost import Post
post2= Post("192.168.5.151",False,False, "YWRtaW4=","cGFzc3dvcmQ=")
buffor = {"adr": [], "adrGetdata": [], "adrSetdata": []}
IP="192.168.5.151"
TLS=0
CREDI=True
IotCoreTree={}
def httpConnectionSetting(ip,tls, credi):
    global IP
    global TLS
    global CREDI
    IP=ip
    TLS=tls
    CREDI=credi

getTreeStr="/gettree"

endPoint= {}
settingsValues=[]
n=False



def getTree():
    httpResponse = post(IP, TLS, CREDI, endpointGen(getTreeStr, 0))
    print(f"***Get tree download finished from {IP}***")
    return httpResponse

def Al1590_gettreeConvert(data):
    #print(data)


    for na,nx in data.items():
        global n
        if na=="type" and nx=="structure":
            n=True
        if n and na=="identifier":
            #print("SUBMENU:",nx)
            n=False
        if na=="subs":
            #print("New submenu")
            x=1
        if na=="adr":

            if "getdata" in nx:
                buffor['adrGetdata'].append(nx)

            elif "setdata" in nx:
                buffor['adrSetdata'].append(nx)

            else:
                buffor['adr'].append(nx)


        if isinstance(nx,dict):
            Al1590_gettreeConvert(nx)
        elif isinstance(nx,list):
            for nl in nx:
                if isinstance(nl, dict):
                    Al1590_gettreeConvert(nl)
    return buffor




def Al1590_urlList():
    httpResponse=getTree()
    if isinstance(httpResponse, dict):
        print(f"***HTTP RESPONSE: Http status: {httpResponse['code']}***")
        endPoint = Al1590_gettreeConvert(httpResponse)
        return endPoint
    else:
        print(httpResponse)
        return httpResponse
    # print(f"***SETDATA{endPoint['adrSetdata']}")
    print("***Endpoint buffor creation***")









