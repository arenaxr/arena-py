from .worker import Worker

class LazyWorker(Worker):
    """
    Wrapper for an ARENA task that runs after an interval (ms).
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
            func_name = self.func.__name__
            Worker.print_traceback(func_name)
            return
