import asyncio
import gc
from async_tasks import async_tasks
from wifi_client import wifi_client


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
    # Wait for tasks to finish
    await async_tasks.wait()


# Start executing code
asyncio.run(main())
