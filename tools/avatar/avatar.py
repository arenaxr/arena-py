import random
import time
import signal
import json
import sys
import os
import numpy as np

from head_rig import HeadRig
from utils import extract_user_id

from arena import *


avatars = {}
arena = Arena(host="arena.andrew.cmu.edu", realm="realm", scene="avatar")


def new_obj_callback(msg):
    global avatars

    user_id = extract_user_id(msg["object_id"])
    if user_id is None: return

    if "camera" in msg["object_id"]:
        avatars[user_id] = HeadRig(arena, user_id, Camera(**msg))

    if "type" in msg and "face-features" == msg["type"] and user_id in avatars:
        avatars[user_id].add_face(Object(**msg))


def on_msg_callback(msg):
    global avatars

    user_id = extract_user_id(msg["object_id"])
    if user_id is None: return

    if user_id in avatars:
        avatar = avatars[user_id]
        if avatar.has_avatar:
            avatar.rig_on()
            avatar.update()
        else:
            avatar.rig_off()


arena.on_msg_callback = on_msg_callback
arena.new_obj_callback = new_obj_callback

arena.run_tasks()
