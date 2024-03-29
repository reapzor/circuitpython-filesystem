import asyncio
from thing_settings import thing_settings
import wifi
from reloader import reloader
from hardware import hardware


class WifiClient:

    def __init__(self):
        self.wifi_connect_attempts = 1
        self.wifi_reconnects = 0
        self.wifi_ping_failures = 0
        self.ping_disconnect_threshold = 5
        self.wifi_connected = False

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

    async def __do_connect(self):
        print(f"Connecting to {thing_settings.wifi_ssid}. Reconnects: ({self.wifi_reconnects}), Attempt: ({self.wifi_connect_attempts})")
        wifi.radio.enabled = True
        failure = False
        try:
            if self.wifi_reconnects >= 2:
                if hardware:
                    hardware.status_led().set_purple()
                    from time import sleep
                    sleep(500)
                print("Reconnecting to wifi more than a couple times can cause a crash. Performing a Soft Reboot.")
                reloader.reload()
            wifi.radio.connect(thing_settings.wifi_ssid, thing_settings.wifi_pass)
            if hardware:
                hardware.status_led().blink_green(count=1, interval_on=500, interval_off=500)
            self.wifi_reconnects += 1
            self.wifi_connected = True
            self.wifi_connect_attempts = 1
            print(f"Connected with IP: {wifi.radio.ipv4_address}")
        except Exception as e:
            print(f"Capture Me {e}")
            failure = True
        if wifi.radio.ap_info is None or failure:
            self.wifi_connect_attempts += 1
            if self.wifi_connect_attempts > 5:
                if hardware:
                    hardware.status_led().set_purple()
                    from time import sleep
                    sleep(500)
                print("Repeated failures connecting to Wifi. Performing a Soft Reboot.")
                reloader.reload()
            print(f"Failure connecting to Wifi. Trying again.")
            if hardware:
                hardware.status_led().blink_red(count=1, interval_on=500, interval_off=500)
            await asyncio.sleep_ms(1000)
            await self.__do_connect()

    async def connect(self):
        print(f"My MAC Addr: {WifiClient.prettify_mac(wifi.radio.mac_address)}")
        if self.wifi_connected:
            print("Already connect(ed)(ing) to wifi.")
            return
        await self.__do_connect()
        self.wifi_reconnects = 0
        self.wifi_ping_failures = 0

    def __do_disconnect(self):
        self.wifi_connected = False
        wifi.radio.enabled = False

    async def disconnect(self):
        self.__do_disconnect()
        self.wifi_reconnects = 0
        self.wifi_ping_failures = 0

    async def reconnnect(self):
        self.__do_disconnect()
        await asyncio.sleep_ms(1000)
        print("Reconnecting Wifi")
        await self.__do_connect()


wifi_client = WifiClient()
