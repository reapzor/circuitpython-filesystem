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
    # Create a GC collection task
    async_tasks.every(10000, collect_gc)
    # Connect to Wifi and monitor connectivity
    await wifi_client.connect()
    # Start tasks
    async_tasks.start()
    print("here")
    # Start mqtt client
    await mqtt_client.connect()
    await mqtt_system_properties.generate_properties(mqtt_client)
    mqtt_system_properties.start_monitor()
    print("here")
    # Wait for tasks to finish
    await async_tasks.wait()


# Start executing code
asyncio.run(main())
