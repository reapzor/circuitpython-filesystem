import asyncio
import gc
from async_tasks import async_tasks
from wifi_client import wifi_client
from mqtt_client import mqtt_client
from mqtt_system_properties import mqtt_system_properties


# Collect Garbage
async def collect_gc():
    gc.collect()


# Main execution
async def main():
    # Connect to Wifi and monitor connectivity
    await wifi_client.connect()
    # Create a GC collection task
    async_tasks.every(20000, collect_gc)
    # Start tasks
    async_tasks.start()
    # Start mqtt client
    await mqtt_client.connect()
    mqtt_system_properties.generate_properties(mqtt_client)
    mqtt_system_properties.start_monitor()
    # Wait for tasks to finish
    await async_tasks.wait()


# Start executing code
asyncio.run(main())
