""" 
Collect information about the program execution, such as 
activity times and number of messages sent/received.
"""

from datetime import datetime
import os
import sys

from ..event_loop import PersistentWorker
from ..base_object import BaseObject
from ..env import (
    PROGRAM_STATS_UPDATE_INTERVAL_MS,
    _get_env,
    _get_arena_env
)

class GetPublicAttrsMixin():
    def get_attrs(self, **kwargs):
        """ Return object public members only """              
        obj = {k: v for k, v in vars(self).items() if k.startswith("_") == False}
        obj.update(kwargs)
        return obj
        
class QueueStats(dict):
    def __init__(self, rcv_queue_len, pub_queue_len):
        self.rcv_queue_len = rcv_queue_len
        self.pub_queue_len = pub_queue_len
    
class ProgramRunInfo(BaseObject, GetPublicAttrsMixin):
    """Program Run Information; collect program execution information. """
        
    object_type = "run_info"

    def __init__(self, evt_loop=None, queue_len_callable=None, update_callback=None, update_interval_ms=_get_env(PROGRAM_STATS_UPDATE_INTERVAL_MS), **kwargs):
        """
        Returns a `ProgramRunInfo`. If an event loop is passed, will setup a periodic task to 
        update execution stats and perform a callback to notify of this update
        
        Args:
            evt_loop: an event loop to which we add a periodic task to update program stats
            queue_len_callable: callable that returns a queue stats object
            update_callback: callback when stats are updated
            update_interval_ms: interval of the periodic task to update program stats
            kwargs: additional attributes to add to the program info, e.g. web host, scene, namespace
        """
        # add additional arguments 
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # program args, env
        self.filename=sys.argv[0]
        self.args=sys.argv[1:]
        self.env=_get_arena_env()
        
        # run stats
        self.create_time =  datetime.utcnow().isoformat()[:-3]+"Z"
        self.last_active_time =  datetime.utcnow().isoformat()[:-3]+"Z"
        self.rcv_msgs = 0
        self.pub_msgs = 0
        # init when a message is sent/received (so we can see if messages were never sent/received)
        self.last_rcv_time = None
        self.last_pub_time = None
        # init when avg is computed
        self.avg_rcv_msgs_per_sec = None
        self.avg_pub_msgs_per_sec = None
        
        self._update_callback = update_callback
        self._get_queue_len = queue_len_callable            

        self._msg_rate_time_start = datetime.now()
        self._rcv_msgs_start = self.rcv_msgs
        self._pub_msgs_start = self.rcv_msgs
        self._update_count = 0
        
        if evt_loop:
            # update stats periodically if event loop is given
            t = PersistentWorker(evt_loop, self._update_stats, interval=update_interval_ms)
            evt_loop.add_task(t)
    
    def _update_stats(self):
        """Update stats (called by periodic task); Execute callback if defined """
        elapsed = datetime.now() - self._msg_rate_time_start
        if elapsed.seconds < 1: 
            return
        
        # compute moving avg of rcv and pub messages
        N=5 # window
        rcv_msgs = self.rcv_msgs - self._rcv_msgs_start
        pub_msgs = self.pub_msgs - self._pub_msgs_start
        self._rcv_msgs_start=self.rcv_msgs
        self._pub_msgs_start=self.rcv_msgs
        if elapsed.seconds > 0:
            rcv_msgs_per_sec = rcv_msgs  / elapsed.seconds
            pub_msgs_per_sec = pub_msgs  / elapsed.seconds
            if self._update_count < N: 
                if self.avg_rcv_msgs_per_sec == None:
                    self.avg_rcv_msgs_per_sec = 0
                    self.avg_pub_msgs_per_sec = 0
                self._update_count = self._update_count + 1
                N=self._update_count
            self.avg_rcv_msgs_per_sec = round(self.avg_rcv_msgs_per_sec + (rcv_msgs_per_sec - self.avg_rcv_msgs_per_sec) / N, 2)
            self.avg_pub_msgs_per_sec = round(self.avg_pub_msgs_per_sec + (pub_msgs_per_sec - self.avg_pub_msgs_per_sec) / N, 2)
                    
            # update queue lens if callable given
            if self._get_queue_len:
                for key, value in self._get_queue_len().items(): setattr(self, key, value)
                
            # update callback if given
            if self._update_callback: 
                self._update_callback(self)
        
    def msg_rcv(self):
        """Update stats when a message is received """
        self.last_rcv_time = datetime.utcnow().isoformat()[:-3]+"Z"
        self.rcv_msgs = self.rcv_msgs + 1
        self.last_active_time = self.last_rcv_time

    def msg_publish(self):
        """Update stats when a message is published """
        self.last_pub_time = datetime.utcnow().isoformat()[:-3]+"Z"
        self.pub_msgs = self.pub_msgs + 1
        self.last_active_time = self.last_pub_time
            
    def add_program_info(self, adict):
        """ Add program info to another dictionary """
        adict[ProgramRunInfo.object_type] = self.get_attrs()
        return adict
        