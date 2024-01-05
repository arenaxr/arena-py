from datetime import datetime
from ..event_loop import PersistentWorker
from ..base_object import BaseObject

UPDATE_INTERVAL_MS=5000

class ProgramStats(BaseObject):
    """
    Program Stats
    """

    def __init__(self, evt_loop=None, update_callback=None, update_interval_ms=UPDATE_INTERVAL_MS):
        self.create_time =  datetime.utcnow().isoformat()[:-3]+"Z"
        self.last_active_time =  datetime.utcnow().isoformat()[:-3]+"Z"
        self.last_rcv_time = None
        self.last_pub_time = None
        self.rcv_msgs = 0
        self.pub_msgs= 0
        self.rcv_msgs_per_sec = 0.0
        self.pub_msgs_per_sec = 0.0
        
        self._msg_rate_time_start = datetime.now()
        self._update_callback = update_callback
        
        if evt_loop:
            # update stats periodically
            t = PersistentWorker(evt_loop, self._update_stats, interval=update_interval_ms)
            evt_loop.add_task(t)
    
    def _update_stats(self):
        """Update stats"""
        elapsed = datetime.now() - self._msg_rate_time_start
        if elapsed.seconds > 0:
            self.rcv_msgs_per_sec = round(self.rcv_msgs  / elapsed.seconds, 2)
            self.pub_msgs_per_sec = round(self.pub_msgs  / elapsed.seconds, 2)
        if self._update_callback: self._update_callback()
        
    def msg_rcv(self):
        self.last_rcv_time = datetime.utcnow().isoformat()[:-3]+"Z"
        self.rcv_msgs = self.rcv_msgs + 1
        self.last_active_time = self.last_rcv_time

    def msg_publish(self):
        self.last_pub_time = datetime.utcnow().isoformat()[:-3]+"Z"
        self.pub_msgs = self.pub_msgs + 1
        self.last_active_time = self.last_pub_time
        
    def get_stats(self, **kwargs):
        # return only public members                
        obj = {k: v for k, v in vars(self).items() if k.startswith("_") == False}
        obj.update(kwargs)
        return obj
    