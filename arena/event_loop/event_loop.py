import os
import signal
import asyncio

class EventLoop(object):
    """
    Wrapper for an asyncio event loop.
    """
    def __init__(self, shutdown_func=None):
        self.tasks = []
        self.loop = asyncio.get_event_loop()
        if os.name == 'nt': # Windows doesnt have SIGHUP signal
            self.signals = (signal.SIGTERM, signal.SIGINT)
        else:
            self.signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        self.shutdown_func = shutdown_func

    async def _shutdown(self):
        if self.shutdown_func:
            self.shutdown_func()
        self.future.cancel()
        self.loop.stop()

    def add_task(self, worker):
        self.tasks += [worker.run()]

    def shutdown_wrapper(self, *args):
        asyncio.ensure_future(self._shutdown())

    def create_future(self):
        return self.loop.create_future()

    def run(self):
        # cancellation of Future ensures all tasks (even if not completed) are cancelled
        self.future = asyncio.gather(*self.tasks)

        # register signals
        for s in self.signals:
            if os.name == 'nt': # Windows does not add_signal_handler implemented
                signal.signal(s, self.shutdown_wrapper)
            else:
                self.loop.add_signal_handler(
                    s, self.shutdown_wrapper
                )

        # run event loop
        try:
            self.loop.run_forever()
        except asyncio.exceptions.CancelledError:
            pass
        finally:
            self.loop.close()

    def stop(self):
        self.loop.stop()
