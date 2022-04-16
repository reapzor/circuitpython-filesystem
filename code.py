import asyncio
import gc
from microcontroller import watchdog
from watchdog import WatchDogTimeout
import supervisor
from async_tasks import async_tasks
from wifi_client import wifi_client
from mqtt_client import mqtt_client
from mqtt_system_properties import mqtt_system_properties


# Collect Garbage
async def collect_gc():
    gc.collect()


# Connect to wifi
async def connect_wifi():
    await wifi_client.connect()


# Connect to mqtt
async def connect_mqtt():
    await mqtt_client.connect()


# Keep main loop alive forever. Async tasks will control exit flow of the program
async def stay_awake():
    while True:
        # Two days
        await asyncio.sleep(60 * 60 * 24 * 2)


try:
    # Start tasks
    async_tasks.start()

    # Create a GC collection task
    async_tasks.every(20000, collect_gc)

    # Connect wifi
    asyncio.run(connect_wifi())

    # Connect mqtt
    asyncio.run(connect_mqtt())

    # Start up system properties monitor
    mqtt_system_properties.generate_properties(mqtt_client)
    mqtt_system_properties.start_monitor()

    # Keep main execution running and defer to the async loops for the rest of the program
    asyncio.run(stay_awake())

except WatchDogTimeout as e:
    print("Watchdog timeout exception hit. Reloading.")
    supervisor.reload()
