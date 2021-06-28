from .worker import Worker
import time

class PersistentWorker(Worker):
    """
    Wrapper for an ARENA task that runs at a periodic interval.
    """
    def __init__(self, event_loop, func, event=None, interval=1000, *args, **kwargs):
        super().__init__(event_loop, func, event, *args, **kwargs)
        self.interval = interval / 1000 # ms -> s

    async def run(self):
        if self.event: await self.event.wait()
        while True:
            start = time.time()
            try:
                self.func(*self.args, **self.kwargs)
            except Exception as e:
                func_name = self.func.__name__
                Worker.print_traceback(func_name)
                return
            end = time.time()
            target_time = max(0, self.interval - (end - start))
            await self.sleep(target_time)
