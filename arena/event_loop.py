import time
import signal
import asyncio
import traceback

class Worker(object):
    """
    Wrapper for async function for single ARENA tasks.
    """
    def __init__(self, func, event=None, *args, **kwargs):
        self.func = func
        self.event = event
        self.args = args
        self.kwargs = kwargs

    async def run(self):
        if self.event: await self.event.wait()
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exc()
            return

    async def sleep(self, interval):
        await asyncio.sleep(interval)

class SingleWorker(Worker):
    """
    Wrapper for an ARENA task that runs once at startup.
    """

class LazyWorker(Worker):
    """
    Wrapper for an ARENA task that after an interval (ms).
    """
    def __init__(self, func, event=None, interval=1000, *args, **kwargs):
        super().__init__(func, event, *args, **kwargs)
        self.interval = interval / 1000 # ms -> s

    async def run(self):
        if self.event: await self.event.wait()
        await self.sleep(self.interval)
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exc()
            return

class AsyncWorker(Worker):
    """
    Wrapper for an ARENA task that is user-defined asyncio function.
    """
    async def run(self):
        if self.event: await self.event.wait()
        try:
            await self.func(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exc()
            return

class PersistantWorker(Worker):
    """
    Wrapper for an ARENA task that runs oat a fixed interval.
    """
    def __init__(self, func, event=None, interval=1000, *args, **kwargs):
        super().__init__(func, event, *args, **kwargs)
        self.interval = interval / 1000 # ms -> s

    async def run(self):
        if self.event: await self.event.wait()
        while True:
            try:
                self.func(*self.args, **self.kwargs)
            except Exception as e:
                traceback.print_exc()
                return
            await self.sleep(self.interval)


class EventLoop(object):
    """
    Wrapper for an asyncio event loop.
    """
    def __init__(self, shutdown_func=None):
        self.tasks = []
        self.loop = asyncio.get_event_loop()
        self.signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        self.shutdown_func = shutdown_func

    async def _shutdown(self):
        if self.shutdown_func: self.shutdown_func()
        self.future.cancel()
        self.loop.stop()

    def add_task(self, worker):
        self.tasks += [worker.run()]

    def run(self):
        # cancellation of Future ensures all tasks (even if not completed) are cancelled
        self.future = asyncio.gather(*self.tasks)
        for s in self.signals:
            self.loop.add_signal_handler(
                s, lambda s=s: asyncio.ensure_future(self._shutdown())
            )

        # run event loop
        try:
            self.loop.run_forever()
        except asyncio.exceptions.CancelledError:
            pass
        finally:
            self.loop.close()
