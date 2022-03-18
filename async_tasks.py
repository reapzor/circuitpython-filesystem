from adafruit_ticks import ticks_ms as ticks, ticks_diff, ticks_add, ticks_less
import asyncio


class AsyncTasks:

    def __init__(self):
        self.tasks = []
        self.running = False
        self.monitor_task = None
        self.waiting = False

    async def __monitor_tasks(self):
        if self.running:
            for task in self.tasks:
                if not task.running:
                    self.tasks.remove(task)
        else:
            for task in self.tasks:
                if task.running:
                    await task.stop()
            self.tasks.clear()

    def add(self,
            task,
            args=None,
            kwargs=None,
            interval=0,
            count=0,
            initial_delay=0):
        task = TimerTask(task=task,
                         args=args,
                         kwargs=kwargs,
                         interval=interval,
                         count=count,
                         initial_delay=initial_delay)
        self.tasks.append(task)
        if self.running:
            task.start()
        return task

    def after(self,
              initial_delay,
              task,
              args=None,
              kwargs=None,
              count=1):
        self.add(task,
                 args=args,
                 kwargs=kwargs,
                 count=count,
                 initial_delay=initial_delay)

    def every(self,
              interval,
              task,
              args=None,
              kwargs=None,
              initial_delay=0):
        self.add(task,
                 args=args,
                 kwargs=kwargs,
                 interval=interval,
                 initial_delay=initial_delay)

    def repeat(self,
               task,
               args=None,
               kwargs=None,
               initial_delay=0):
        self.add(task,
                 args=args,
                 kwargs=kwargs,
                 initial_delay=initial_delay)

    def repeat_for(self,
                   count,
                   task,
                   args=None,
                   kwargs=None,
                   initial_delay=0):
        self.add(task,
                 args=args,
                 kwargs=kwargs,
                 initial_delay=initial_delay,
                 count=count)

    def start(self):
        if self.monitor_task is None:
            self.running = True
            self.monitor_task = TimerTask(self.__monitor_tasks, interval=2000)
            for task in self.tasks:
                task.start()
            self.monitor_task.start()

    async def stop(self):
        if self.monitor_task is not None:
            self.running = False
            while len(self.tasks) > 0:
                await asyncio.sleep_ms(1)
            await self.monitor_task.stop()
            self.monitor_task = None

    async def wait(self):
        if self.monitor_task is not None:
            while len(self.tasks) > 0:
                await asyncio.sleep_ms(1)
            self.running = False
            await self.monitor_task.stop()
            self.monitor_task = None


class TimerTask:

    def __init__(self,
                 task,
                 args=None,
                 kwargs=None,
                 interval=0,
                 count=0,
                 initial_delay=0):
        self.interval = interval
        self.count = count
        self.current_count = 0
        self.initial_delay = initial_delay
        self.running = False
        self.task = task
        self.task_id = None
        if args is None:
            self.args = []
        else:
            self.args = args
        if kwargs is None:
            self.kwargs = {}
        else:
            self.kwargs = kwargs

    async def __task(self):
        if self.initial_delay > 0:
            await asyncio.sleep_ms(self.initial_delay)
        next_time_base = ticks()
        while self.running:
            self.current_count += 1
            await self.task(*self.args, **self.kwargs)
            if not self.running or (self.count != 0 and self.current_count >= self.count):
                break
            if self.interval == 0:
                await asyncio.sleep_ms(0)
                continue
            next_time = ticks_add(next_time_base, self.interval)
            cur_time = ticks()
            if ticks_less(cur_time, next_time):
                time_dif = ticks_diff(next_time, cur_time)
            else:
                time_dif = 1
            await asyncio.sleep_ms(time_dif)
            cur_time = ticks()
            next_time_sync = ticks_diff(cur_time, next_time)
            if next_time_sync > self.interval:
                print(f"Task off by {next_time_sync - self.interval}, Interval: {self.interval}")
                next_time_sync = 0
            next_time_base = ticks_diff(cur_time, next_time_sync)
        self.running = False
        self.current_count = 0

    def start(self):
        if self.task_id is None:
            self.running = True
            self.task_id = asyncio.create_task(self.__task())

    async def stop(self):
        self.running = False
        await self.wait()

    async def wait(self):
        await asyncio.gather(self.task_id)
        self.task_id = None


async_tasks = AsyncTasks()
