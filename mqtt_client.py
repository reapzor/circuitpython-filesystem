import gc

from async_tasks import async_tasks
from adafruit_minimqtt import adafruit_minimqtt as mqtt
import socketpool
from settings import settings, settings_missing
from mqtt_property import MQTTProperty
import wifi
from wifi_client import wifi_client
import asyncio
import errno


class MQTTClient:

    def __init__(self):
        self.radio = None
        self.socket_pool = None
        self.mqtt_client = None
        self.loop_task = None
        self.properties = []
        self.connected_property = self.system_property("connected", value=0)
        self.reconnect_count = 0
        self.reconnect_attempts = 0
        self.publish_attempts = 0
        self.loop_attempts = 0

    async def do_loop(self):
        print("tick")
        try:
            self.mqtt_client.is_connected()
            self.mqtt_client.loop(timeout=0.7)
        except (mqtt.MMQTTException, OSError) as e:
            print(f"Loop exception: {e}")
            self.loop_attempts += 1
            if self.loop_attempts > 0:
                self.loop_attempts = 0
                await self.reconnect()

    def on_connnect(self, client, userdata, flags, rc):
        print("Connecty")

    def on_disconnect(self, client, userdata, rc):
        print("Disconnecty")

    async def reconnect(self):
        self._do_disconnect()
        self.reconnect_count += 1
        await self._do_connect()

    async def _do_connect(self):
        print(f"Connecting MQTT at {settings.mqtt_broker}. Reconnects: ({self.reconnect_count}), Attempts: ({self.reconnect_attempts})")
        try:
            self.mqtt_client.connect()
            self.mqtt_client.loop()
            await self.connected_property.publish(value=1)
            self.mqtt_client.loop()
            self.reconnect_attempts = 0
            self.loop_attempts = 0
            self.publish_attempts = 0
        except (mqtt.MMQTTException, OSError, RuntimeError) as e:
            print(f"Connect exception: {e}")
            self.reconnect_attempts += 1
            await asyncio.sleep_ms(1000)
            await self._do_connect()
            # if self.reconnect_attempts > 3:
            #     self.reconnect_attempts = 0
            #     await wifi_client.reconnnect()

    async def connect(self):
        # Set up a MiniMQTT Client
        if settings_missing():
            print("Not connecting MQTT Client - No server settings")
            return
        self.mqtt_client = mqtt.MQTT(
            broker=settings.mqtt_broker,
            port=1883,
            socket_pool=socketpool.SocketPool(wifi.radio)
        )
        self.mqtt_client.will_set(topic=self.connected_property.mqtt_path(),
                                  payload=0,
                                  retain=True)
        self.mqtt_client.on_connect = self.on_connnect
        self.mqtt_client.on_disconnect = self.on_disconnect
        await self._do_connect()
        self.loop_task = async_tasks.every(2000, self.do_loop)

    def _do_disconnect(self):
        if self.mqtt_client:
            try:
                self.mqtt_client.disconnect()
            except (mqtt.MMQTTException, OSError):
                pass

    async def disconnect(self):
        if self.loop_task:
            print("stop task")
            await self.loop_task.stop()
        self.loop_task = None
        self._do_disconnect()

    def property(self, group, key, value=-1):
        property = MQTTProperty(group=group, key=key, value=value, mqtt_client=self)
        self.properties.append(property)
        return property

    def system_property(self, key, value=None):
        return self.property(group="system", key=key, value=value)

    def data_property(self, key, value=None):
        return self.property(group="data", key=key, value=value)

    def command_property(self, key, value=None):
        return self.property(group="command", key=key, value=value)

    def system_command_property(self, key, value=None):
        return self.property(group=["system", "command"], key=key, value=value)

    async def _do_publish(self, path, value, retain):
        try:
            self.mqtt_client.publish(path, value, retain=retain)
        except (mqtt.MMQTTException, OSError) as e:
            print(f"Publish exception: {e}")
            self.publish_attempts += 1
            if self.publish_attempts >= 3:
                self.publish_attempts = 0
                await self.reconnect()
            await asyncio.sleep_ms(1000)
            await self._do_publish(path, value, retain)

    async def publish(self, path, value, retain=True):
        await self._do_publish(path, value, retain)



mqtt_client = MQTTClient()
