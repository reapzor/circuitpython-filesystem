import time
from async_tasks import async_tasks
import wifi
from wifi_client import WifiClient
from mqtt_client import mqtt_client
import gc
import os


class MQTTSystemProperties:
    def __init__(self):
        self.battery = None
        self.wifi_strength = None
        self.uptime = None
        self.mac_addr = None
        self.ip_addr = None
        self.mem_free = None
        self.storage_free = None
        self.monitor_task = None
        self.ip = None
        self.initial_publish = True

    def generate_properties(self):
        self.battery = mqtt_client.system_property("battery")
        self.wifi_strength = mqtt_client.system_property("wifi_strength")
        self.uptime = mqtt_client.system_property("uptime")
        self.mac_addr = mqtt_client.system_property("mac_addr")
        self.ip_addr = mqtt_client.system_property("ip_addr")
        self.mem_free = mqtt_client.system_property("mem_free")
        self.storage_free = mqtt_client.system_property("storage_free")

    async def __monitor(self):
        if self.initial_publish:
            self.initial_publish = False
            await self.mac_addr.publish(WifiClient.prettify_mac(wifi.radio.mac_address))
        if self.ip != wifi.radio.ipv4_address:
            self.ip = wifi.radio.ipv4_address
            await self.ip_addr.publish(str(self.ip))
        await self.battery.publish("100")
        await self.wifi_strength.publish(WifiClient.signal_strength(wifi.radio.ap_info.rssi))
        await self.uptime.publish(time.monotonic())
        await self.mem_free.publish(gc.mem_free()/1024)
        fs_stat = os.statvfs('/')
        await self.storage_free.publish(fs_stat[0] * fs_stat[3] / 1024)

    def start_monitor(self):
        self.monitor_task = async_tasks.every(1000, self.__monitor)

    async def stop_monitor(self):
        await self.monitor_task.stop()


mqtt_system_properties = MQTTSystemProperties()
