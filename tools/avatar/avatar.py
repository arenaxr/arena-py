import random
import time
import signal
import json
import sys
import os
import numpy as np

from head import Head
from utils import extract_user_id

from arena import *

arena = Arena("arena.andrew.cmu.edu", "realm", "test")


avatars = {}    # dictionary of avatars mapped to heads

class Avatar(object):
    def __init__(self, camera):
        self.camera = camera
        self.head = None

    def add_head(self, head):
        self.head = head

    def remove_head(self):
        if self.has_head:
            self.head.rig_off()
        self.head = None

    @property
    def has_head(self):
        return self.head is not None

    @property
    def avatar_on(self):
        return self.camera.hasAvatar


def new_obj_callback(msg):
    global avatars

    obj_id = msg["object_id"]
    user_id = extract_user_id(obj_id)
    if "camera" in obj_id:
        avatars[user_id] = Avatar(Camera(**msg))

def on_msg_callback(msg):
    global avatars

    obj_id = msg["object_id"]
    try:
        user_id = extract_user_id(obj_id)
    except:
        return

    if user_id in avatars:
        if "face" in obj_id and avatars[user_id].avatar_on:
            if msg["hasFace"]:
                if not avatars[user_id].has_head:
                    avatars[user_id].add_head(Head(arena, user_id))
                    avatars[user_id].head.add_face(msg)
                else:
                    avatars[user_id].head.update_face(msg)

        elif "camera" in obj_id:
            if not avatars[user_id].avatar_on:
                if avatars[user_id].has_head:
                    avatars[user_id].remove_head()

arena.on_msg_callback = on_msg_callback
arena.new_obj_callback = new_obj_callback

arena.run_tasks()
