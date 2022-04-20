from persisted_storage import persisted_storage
from getpass import getpass


class ThingSettings:

    def __init__(self):
        self.wifi_ssid = None
        self.wifi_pass = None
        self.mqtt_broker = None
        self.thing_name = None
        self.settings_configured = False

    def load(self):
        if "set_conf" in persisted_storage.data:
            self.wifi_ssid = persisted_storage.data["wssid"]
            self.wifi_pass = persisted_storage.data["wpass"]
            self.mqtt_broker = persisted_storage.data["mqttbrok"]
            self.thing_name = persisted_storage.data["thname"]
            self.settings_configured = True

    def configure(self, force=False):
        self.load()
        if self.settings_configured and not force:
            return
        print("User Settings required. Please enter the configuration details for this thing below.")
        self.wifi_ssid = input("Enter WiFi SSID: ")
        self.wifi_pass = getpass("Enter WiFi Password: ")
        self.mqtt_broker = input("Enter MQTT Broker IP: ")
        self.thing_name = input("Enter a name for this thing: ")
        self.settings_configured = True
        self.save()

    def save(self):
        persisted_storage.data["wssid"] = self.wifi_ssid
        persisted_storage.data["wpass"] = self.wifi_pass
        persisted_storage.data["mqttbrok"] = self.mqtt_broker
        persisted_storage.data["thname"] = self.thing_name
        persisted_storage.data["set_conf"] = True
        persisted_storage.save()


thing_settings = ThingSettings()
