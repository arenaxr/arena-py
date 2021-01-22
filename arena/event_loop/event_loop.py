import signal
import asyncio

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
