from .worker import Worker

class AsyncWorker(Worker):
    """
    Wrapper for an ARENA task that is user-defined asyncio function.
    """
    async def run(self):
        if self.event: await self.event.wait()
        try:
            await self.func(*self.args, **self.kwargs)
        except Exception as e:
            func_name = self.func.__name__
            Worker.print_traceback(func_name)
            return
