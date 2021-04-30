from .worker import Worker

class SingleWorker(Worker):
    """
    Wrapper for an ARENA task that runs once at startup.
    """
