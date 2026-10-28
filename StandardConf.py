
"""
======================================================================================
Project: Cyber Security
Module: StandardConf
======================================================================================
Author: Pawe Sokoowski SL3
Date: 2026-03-13
Version: 1.0

Functionality:
Fast standard  configuration for IO-link master
**================================EXAMPLE COMMANDS====================================**
Standard settings
#set_setings(std_conf.timers())
#set_setings(std_conf.deviceSettingsTime())
#set_setings(std_conf.iolinkmaster())
"""
import time


class Std_conf:
    def __init__(self):
        # --- Device tag
        self.application_tag = "Al1590"
        self.function_tag = "Al1590"

        # --- Time
        self.timezone = "Europe/Berlin"

        # --- Network
        self.network_ip_address="192.168.5.151"
        self.network_subnet_mask = "255.255.255.0"
        self.hostname = "Al1590_host"
        self.ipv4_mode = 1
        self.gateway = "192.168.5.1"
        self.static_dns = "8.8.8.8"
        self.dns_mode = 2
        self.gateway_mode = 1

        # --- Network address (setblock)
        self.network_address_setblock ="/network/br0/ipv4/address0/setblock"
        self.network_address_setnetwork="/network/br0/ipv4/setnetwork"
        self.network_address =  {
            "address": self.network_ip_address,
            "subnetmask": self.network_subnet_mask,
            "mode": self.ipv4_mode
        }
        self.network_address_setnetwork_data= {
        "mode": self.ipv4_mode,
        "gateway": self.gateway,
        "address": [
            {
                "address": self.network_ip_address,
                "subnetmask": self.network_subnet_mask
            }
        ],
        "staticdnsservers": [
            self.static_dns,
            "1.1.1.1"
        ],
        "dns_mode": self.dns_mode,
        "gateway_mode": self.gateway_mode
        }

        # --- Timers
        self.timer_intervals = {
            1: 100,
            2: 4321,
        }

        # --- IO-Link ports
        self.ports = range(1, 9)

        self.port_modes = {
            1: 3, 2: 3, 3: 3, 4: 3,
            5: 3, 6: 3, 7: 3, 8: 3,
        }

        self.powercontrol_mode_ua = {
            1: 0, 2: 0, 3: 0, 4: 0,
            5: 0, 6: 0, 7: 0, 8: 0,
        }

        self.master_cycle_times = {
            1: 0, 2: 0, 3: 0, 4: 0,
            5: 0, 6: 0, 7: 0, 8: 0,
        }

        # --- Validation
        self.validation_datastorage_mode = {
            1: 0, 2: 0, 3: 0, 4: 0,
            5: 0, 6: 0, 7: 0, 8: 0,
        }

        self.validation_vendor_id = {
            1: 123, 2: 123, 3: 123, 4: 123,
            5: 123, 6: 123, 7: 123, 8: 123,
        }

        self.validation_device_id = {
            1: 123, 2: 123, 3: 123, 4: 123,
            5: 123, 6: 123, 7: 123, 8: 123,
        }

        # --- IO-Link device tags
        self.sensor_tags = {
            1: "sensor1",
            2: "sensor2",
            3: "sensor3",
            4: "sensor4",
            5: "sensor5",
            6: "sensor6",
            7: "sensor7",
            8: "sensor8",
        }

    # -------------------------------------------------
    # Methods
    # -------------------------------------------------

    def deviceTag(self):
        return {
            "devicetag/applicationtag": self.application_tag,
            "devicetag/functiontag": self.function_tag,
        }

    def deviceSettingsTime(self):
        ts = int(time.time_ns()/1000000)
        return {
            "devicesettings/systemtime/datetime": ts,
            "devicesettings/systemtime/timezone": self.timezone,
        }

    def network(self):
        return {
            "network/br0/hostname": self.hostname,
            "network/br0/ipv4/mode": self.ipv4_mode,
            "network/br0/ipv4/gateway": self.gateway,
            "network/br0/ipv4/staticdnsservers": self.static_dns,
            "network/br0/ipv4/dns_mode": self.dns_mode,
        }

    def networkAddress(self):
        return {self.network_address_setblock: self.network_address}
    def set_network_address(self, function):
        print(f"set_network_address: {self.network_address}")
        function(
            self.network_address_setblock,
            self.network_address, )
    def set_network_address_new_visu(self, function):
        print(f"set_network_address: {self.network_address}")
        function(
            self.network_address_setnetwork,
            self.network_address_setnetwork_data, )


    def timers(self):
        return {
            f"timer[{tid}]/interval": interval
            for tid, interval in self.timer_intervals.items()
        }

    def iolinkmaster(self):
        cfg = {}

        for port in self.ports:
            cfg[f"iolinkmaster/port[{port}]/mode"] = self.port_modes[port]
            if port < 5:
                cfg[f"iolinkmaster/port[{port}]/powercontrol/mode_ua"] = self.powercontrol_mode_ua[port]
            cfg[f"iolinkmaster/port[{port}]/mastercycletime_preset"] = self.master_cycle_times[port]

        return cfg

    def validation(self):
        cfg = {}

        for port in self.ports:
            cfg[f"iolinkmaster/port[{port}]/validation_datastorage_mode"] = \
                self.validation_datastorage_mode[port]

            cfg[f"iolinkmaster/port[{port}]/validation_vendorid"] = \
                self.validation_vendor_id[port]

            cfg[f"iolinkmaster/port[{port}]/validation_deviceid"] = \
                self.validation_device_id[port]

        return cfg

    def iolinkDevice(self):
        return {
            f"iolinkmaster/port[{port}]/iolinkdevice/applicationspecifictag": tag
            for port, tag in self.sensor_tags.items()
        }