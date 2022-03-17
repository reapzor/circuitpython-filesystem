from settings import settings


class MQTTProperty:

    def __init__(self, group, key, value=None, mqtt_client=None):
        if group is type(list):
            self.group = "/".join(group)
        else:
            self.group = group
        self.key = key
        self.value = value
        self.mqtt_client = mqtt_client

    def mqtt_path(self):
        return f"things/{settings.thing_name}/{self.group}/{self.key}"

    async def publish(self, value=None):
        if not value:
            value = self.value
        else:
            self.value = value
        await self.mqtt_client.publish(self.mqtt_path(), value, retain=True)
