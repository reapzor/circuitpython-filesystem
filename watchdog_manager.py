from async_tasks import async_tasks
from microcontroller import watchdog
from watchdog import WatchDogMode


class WatchdogManager:

    def __init__(self):
        # 10 minutes
        self.timeout = 60 * 10
        self.feed_task = None

    def start(self):
        watchdog.timeout = self.timeout
        watchdog.mode = WatchDogMode.RAISE
        watchdog.feed()

    def feed(self):
        watchdog.feed()

    def auto_feed(self):
        if not self.feed_task:
            self.feed_task = async_tasks.every(10000, self.__auto_feed)

    async def __auto_feed(self):
        self.feed()


watchdog_manager = WatchdogManager()
