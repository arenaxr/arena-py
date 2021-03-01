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
scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="avatar")


def user_join_callback(camera):
    global avatars

    user_id = extract_user_id(camera.object_id)
    if user_id and user_id not in avatars:
        avatars[user_id] = HeadRig(scene, user_id, camera)


def new_obj_callback(msg):
    global avatars

    user_id = extract_user_id(msg["object_id"])
    if user_id is None: return

    if "type" in msg and "face-features" == msg["type"] and user_id in avatars:
        if user_id not in avatars:
            avatars[user_id] = HeadRig(scene, user_id, Camera(**msg))
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


scene.on_msg_callback = on_msg_callback
scene.new_obj_callback = new_obj_callback
scene.user_join_callback = user_join_callback

scene.run_tasks()
