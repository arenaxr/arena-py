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
scene = Scene(host="arenaxr.org", scene="avatar")


def user_join_callback(scene, camera, msg):
    global avatars

    user_id = extract_user_id(camera.object_id)
    if user_id and user_id not in avatars:
        avatars[user_id] = HeadRig(scene, user_id, camera)


def on_msg_callback(scene, obj, msg):
    global avatars

    user_id = extract_user_id(obj.object_id)
    if user_id is None:
        return

    if user_id in avatars:
        avatar = avatars[user_id]
        if avatar.has_avatar:
            avatar.rig_on()
            avatar.update()
        else:
            avatar.rig_off()

        if avatar.faceObj is None and "type" in obj and "face-features" == msg["type"]:
            avatar.add_face(obj)


scene.on_msg_callback = on_msg_callback
scene.user_join_callback = user_join_callback

scene.run_tasks()
