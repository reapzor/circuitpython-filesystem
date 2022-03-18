import os
import storage


def check_settings_file():
    if "settings.py" not in os.listdir("/"):
        storage.remount("/", False)
        with open("/settings.py", 'w') as config:
            settings_content = (
                        "class Settings:\n" +
                        "    wifi_ssid = None,    # Wifi SSID\n" +
                        "    wifi_pass = None,    # Wifi Pass\n" +
                        "    mqtt_broker = None,  # MQTT broker/server IP\n" +
                        "    thing_name = None    # Unique name of this device for mqtt eventing\n" +
                        "\n\n" +
                        "settings = Settings()\n" +
                        "\n\n" +
                        "def settings_missing():\n" +
                        "    if settings.thing_name is None:\n" +
                        "        print('Please configure settings.py.')\n" +
                        "        return True\n" +
                        "    return False\n")
            config.write(settings_content)
            config.close()
            print("Generates settings.py file. Please fill it out!")
        storage.remount("/", True)
