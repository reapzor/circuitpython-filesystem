from adafruit_minimqtt import adafruit_minimqtt as MQTT
import socketpool
from check_settings import settings

class MQTTClient:

    def __init__(self):
        self.mqtt_client = None
        self.radio


    async def start_mqtt(radio):
        # Set up a MiniMQTT Client
        mqtt_client = MQTT.MQTT(
            broker=settings["mqtt_broker"],
            socket_pool=socketpool.SocketPool(radio)
        )
