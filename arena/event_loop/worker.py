import signal, os
import asyncio
import traceback

class Worker(object):
    """
    Wrapper for async function for single ARENA tasks.
    """
    def __init__(self, event_loop, func, event=None, *args, **kwargs):
        self.event_loop = event_loop
        self.func = func
        self.event = event
        self.args = args
        self.kwargs = kwargs

    async def run(self):
        if self.event: await self.event.wait()
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as e:
            func_name = self.func.__name__
            Worker.print_traceback(func_name)

            # disconnect and stop running the program
            self.event_loop.shutdown_wrapper()

    async def sleep(self, interval):
        await asyncio.sleep(interval)

    @classmethod
    def print_traceback(cls, func_name):
        print(
            f"Something went wrong!\n"
            f"-----------------------------\n"
            f"Source:\n{traceback.format_exc()}\n\n"
            f"-----------------------------\n"
        )
