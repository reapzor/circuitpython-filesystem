import asyncio
from adafruit_ticks import ticks_ms as ticks, ticks_add, ticks_diff, ticks_less


class STask:
    def __init__(self, task, args=None, kwargs=None, interval=1000):
        self.task = task
        self.args = args or []
        self.kwargs = kwargs or {}
        self.interval = interval

    async def run_task(self):
        cur_time = ticks()
        next_time = ticks_add(cur_time, self.interval)
        await self.task(*self.args, **self.kwargs)
        cur_time = ticks()
        if ticks_less(cur_time, next_time):
            time_dif = ticks_diff(next_time, cur_time)
        else:
            print(f"STask off by {ticks_diff(cur_time, next_time)}ms")
            time_dif = self.interval
        await asyncio.sleep_ms(time_dif)


class Scheduler:

    def __init__(self):
        self.tasks = []
        self.runner_task = None
        self.started = False

    def schedule(self, task, args=None, kwargs=None, interval=1000):
        self.tasks.append(STask(task, args, kwargs, interval=interval))
        self.start()

    async def schedule_loop(self):
        while len(self.tasks) > 0:
            task = self.tasks.pop(0)
            await task.run_task()
        self.started = False
        self.runner_task = None

    def start(self):
        if self.started:
            return
        self.started = True
        self.runner_task = asyncio.create_task(self.schedule_loop())

    async def stop(self):
        if self.started:
            self.started = False
            await asyncio.gather(self.runner_task)
            self.runner_task = None
