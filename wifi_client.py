import asyncio
from async_tasks import async_tasks
from settings import settings, settings_missing
import wifi
import ipaddress
import supervisor


class WifiClient:

    def __init__(self):
        self.wifi_connect_attempts = 1
        self.wifi_reconnects = 0
        self.wifi_ping_failures = 0
        self.ping_disconnect_threshold = 5
        self.wifi_connected = False
        self.monitor_task = None

    @staticmethod
    def prettify_mac(mac_bytes):
        result = ""
        for b in mac_bytes:
            result += "%02x:" % b
        return result.upper()[:-1]

    @staticmethod
    def signal_strength(db):
        if db <= -95:
            return 0
        if db >= -45:
            return 100
        return 2 * (db + 95)

    async def __monitor_wifi(self):
        pass
        # if not self.wifi_connected:
        #     return
        # response = wifi.radio.ping(ipaddress.ip_address(settings.ping_ip), timeout=0.5)
        # if response is None:
        #     self.wifi_ping_failures += 1
        # else:
        #     self.wifi_ping_failures = 0
        # if self.wifi_ping_failures >= self.ping_disconnect_threshold:
        #     print(f"Multiple failures attempting to ping {settings.ping_ip}. Reconnecting Wifi.")
        #     self.__do_disconnect()
        #     self.wifi_reconnects += 1
        #     await asyncio.sleep_ms(1000)
        #     await self.__do_connect()
        #     self.wifi_ping_failures = 0

    async def __do_connect(self):
        print(f"Connecting to {settings.wifi_ssid}. Reconnects: ({self.wifi_reconnects}), Attempt: ({self.wifi_connect_attempts})")
        wifi.radio.enabled = True
        failure = False
        try:
            wifi.radio.connect(settings.wifi_ssid, settings.wifi_pass)
            self.wifi_reconnects += 1
            self.wifi_connected = True
            self.wifi_connect_attempts = 1
            print(f"Connected with IP: {wifi.radio.ipv4_address}")
        except Exception as e:
            print(type(e).__name__)
            failure = True
        if wifi.radio.ap_info is None or failure:
            self.wifi_connect_attempts += 1
            if self.wifi_connect_attempts > 5:
                print("Repeated failures connecting to Wifi. Performing a Soft Reboot.")
                supervisor.reload()
            print(f"Failure connecting to Wifi. Trying again.")
            await asyncio.sleep_ms(1000)
            await self.__do_connect()

    async def connect(self):
        print(f"My MAC addr: {WifiClient.prettify_mac(wifi.radio.mac_address)}")
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

    async def reconnnect(self):
        self.__do_disconnect()
        await asyncio.sleep_ms(1000)
        print("Reconnecting Wifi")
        await self.__do_connect()


wifi_client = WifiClient()
