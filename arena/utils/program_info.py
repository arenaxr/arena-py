from datetime import datetime
import os
import sys

from ..event_loop import PersistentWorker
from ..base_object import BaseObject
from ..env import (
    ENV_DEFAULTS,
    PROGRAM_STATS_UPDATE_INTERVAL_MS,
    _get_env
)

class ProgramRunInfo(BaseObject):
    """
    Program Run Info
    """
    
    object_type = "run_info"

    def __init__(self, evt_loop=None, update_callback=None, update_interval_ms=os.environ.get(PROGRAM_STATS_UPDATE_INTERVAL_MS, ENV_DEFAULTS[PROGRAM_STATS_UPDATE_INTERVAL_MS])):
        # program args, env
        self.filename=sys.argv[0]
        self.args=str(sys.argv[1:])
        self.env=_get_env()
        
        # run stats
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
        """Update stats; Execute callback if defined """
        elapsed = datetime.now() - self._msg_rate_time_start
        if elapsed.seconds > 0:
            self.rcv_msgs_per_sec = round(self.rcv_msgs  / elapsed.seconds, 2)
            self.pub_msgs_per_sec = round(self.pub_msgs  / elapsed.seconds, 2)
        if self._update_callback: self._update_callback(self)
        
    def msg_rcv(self):
        self.last_rcv_time = datetime.utcnow().isoformat()[:-3]+"Z"
        self.rcv_msgs = self.rcv_msgs + 1
        self.last_active_time = self.last_rcv_time

    def msg_publish(self):
        self.last_pub_time = datetime.utcnow().isoformat()[:-3]+"Z"
        self.pub_msgs = self.pub_msgs + 1
        self.last_active_time = self.last_pub_time
        
    def get_info(self, **kwargs):
        """ Return run info dictionary to publish; public members only """              
        obj = {k: v for k, v in vars(self).items() if k.startswith("_") == False}
        obj.update(kwargs)
        return obj
    
    def add_program_info(self, adict):
        """ Add program info to another dictionary """
        adict[ProgramRunInfo.object_type] = self.get_info()
        return adict
        