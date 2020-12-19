import time
import signal
import asyncio

class Worker(object):
    """
    Wrapper for async function for single ARENA tasks.
    """
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    async def run(self):
        self.func(*self.args, **self.kwargs)

    async def sleep(self, interval):
        await asyncio.sleep(interval)

class SingleWorker(Worker):
    """
    Wrapper for an ARENA task that runs once at startup.
    """
    async def run(self):
        self.func(*self.args, **self.kwargs)

class LazyWorker(Worker):
    """
    Wrapper for an ARENA task that after an interval (ms).
    """
    def __init__(self, func, interval, *args, **kwargs):
        super().__init__(func, *args, **kwargs)
        self.interval = interval

    async def run(self):
        await self.sleep(self.interval)
        self.func(*self.args, **self.kwargs)

class AsyncWorker(Worker):
    """
    Wrapper for an ARENA task that is user-defined asyncio function.
    """
    async def run(self):
        await self.func(*self.args, **self.kwargs)

class PersistantWorker(Worker):
    """
    Wrapper for an ARENA task that runs oat a fixed interval.
    """
    def __init__(self, func, interval, *args, **kwargs):
        super().__init__(func, *args, **kwargs)
        self.interval = interval

    async def run(self):
        while True:
            self.func(*self.args, **self.kwargs)
            await self.sleep(self.interval)

class EventLoop(object):
    """
    Wrapper for an asyncio event loop.
    """
    def __init__(self, shutdown_func=None):
        self.tasks = []
        self.loop = asyncio.get_event_loop()
        signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        for s in signals:
            self.loop.add_signal_handler(
                    s, lambda s=s: asyncio.create_task(self._shutdown(self.loop, s, shutdown_func))
                )

    async def _shutdown(self, loop, signal, shutdown_func):
        if shutdown_func: shutdown_func()
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
