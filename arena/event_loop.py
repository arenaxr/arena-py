import time
import signal
import asyncio

class Worker(object):
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    async def run(self):
        self.func(*self.args, **self.kwargs)

class Timer(object):
    def __init__(self, func, interval, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.interval = interval

    async def run(self):
        while True:
            self.func(*self.args, **self.kwargs)
            await self.sleep(self.interval)

    async def sleep(self, interval):
        await asyncio.sleep(interval)

class EventLoop(object):
    def __init__(self, shutdown_func=None):
        self.tasks = []
        self.loop = asyncio.get_event_loop()
        signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        for s in signals:
            self.loop.add_signal_handler(
                    s, lambda s=s: asyncio.create_task(self._shutdown(self.loop, s, shutdown_func))
                )

    async def _shutdown(self, loop, signal, shutdown_func):
        if shutdown_func:
            shutdown_func()

        tasks = [t for t in asyncio.all_tasks() if t is not
                asyncio.current_task()]
        for task in tasks: task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self.loop.stop()

    def add_task(self, worker):
        self.tasks += [worker.run()]

    def run(self):
        try:
            self.loop.run_until_complete(asyncio.wait(self.tasks))
        except asyncio.exceptions.CancelledError:
            pass
        finally:
            self.loop.close()

    async def sleep(self, interval):
        await asyncio.sleep(interval)
