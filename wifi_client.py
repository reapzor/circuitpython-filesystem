import asyncio
from async_tasks import async_tasks
from settings import settings, settings_missing
import wifi
import ipaddress


class WifiClient:

    def __init__(self):
        self.wifi_reconnects = 0
        self.wifi_ping_failures = 0
        self.ping_disconnect_threshold = 5
        self.wifi_connected = False
        self.monitor_task = None

    def __prettify_mac(self, mac_bytes):
        result = ""
        for b in mac_bytes:
            result += "%02x:" % b
        return result.upper()

    async def __monitor_wifi(self):
        if not self.wifi_connected:
            return
        response = wifi.radio.ping(ipaddress.ip_address(settings.ping_ip), timeout=0.5)
        if response is None:
            self.wifi_ping_failures += 1
        else:
            self.wifi_ping_failures = 0
        if self.wifi_ping_failures >= self.ping_disconnect_threshold:
            print(f"Multiple failures attempting to ping {settings.ping_ip}. Reconnecting Wifi.")
            self.__do_disconnect()
            self.wifi_reconnects += 1
            await asyncio.sleep_ms(1000)
            await self.__do_connect()
            self.wifi_ping_failures = 0

    async def __do_connect(self):
        print(f"Connecting to {settings.wifi_ssid}. Reconnects: {self.wifi_reconnects}")
        wifi.radio.enabled = True
        wifi.radio.connect(settings.wifi_ssid, settings.wifi_pass)
        if wifi.radio.ap_info is None:
            self.wifi_reconnects += 1
            print(f"Failure connecting to Wifi. Trying again.")
            await asyncio.sleep_ms(1000)
            await self.__do_connect()
        self.wifi_connected = True
        print(f"Connected with IP: {wifi.radio.ipv4_address}")

    async def connect(self):
        print(f"My MAC addr: {self.__prettify_mac(wifi.radio.mac_address)}")
        if settings_missing():
            print("Not connecting to wifi, no credentials.")
            return
        if self.monitor_task is not None:
            print("Already connect(ed)(ing) to wifi.")
            return
        await self.__do_connect()
        self.wifi_reconnects = 0
        self.wifi_ping_failures = 0
        self.monitor_task = async_tasks.every(7000, self.__monitor_wifi)

    def __do_disconnect(self):
        self.wifi_connected = False
        wifi.radio.enabled = False

    async def disconnect(self):
        if self.monitor_task is not None:
            await self.monitor_task.stop()
            self.__do_disconnect()
            self.monitor_task = None
            self.wifi_reconnects = 0
            self.wifi_ping_failures = 0


wifi_client = WifiClient()
