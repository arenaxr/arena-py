import arena
import random
import time
import signal
import json
import sys
import os
import numpy as np

from head import Head
from utils import extract_user_id

avatars = {} # dictionary of avatars mapped to heads

def callback(msg):
    global avatars

    msg_json = json.loads(msg)

    if "hasAvatar" in msg_json:
        user = extract_user_id(msg_json["object_id"])
        if msg_json["hasAvatar"]:
            if user not in avatars:
                avatars[user] = Head(user)
            avatars[user].rig_on()
        else:
            if user in avatars:
                avatars[user].rig_off()
                del avatars[user]

    elif "hasFace" in msg_json and msg_json["hasFace"]:
        user = extract_user_id(msg_json["object_id"])
        if user in avatars and avatars[user].rig_enabled:
            if not avatars[user].has_face:
                avatars[user].add_face(msg_json)
            else:
                avatars[user].update_face(msg_json)

if (os.environ.get('SCENE') is not None) and (os.environ.get('REALM') is not None) and (os.environ.get('MQTTH') is not None):
    SCENE = os.environ["SCENE"]
    HOST = os.environ["MQTTH"]
    REALM = os.environ["REALM"]
    print("Loading: " + SCENE + ", " + REALM + ", " + HOST)
else:
    print( "You need to set SCENE, MQTTH and REALM as environmental variables to specify the program target")
    exit(-1)

arena.init(HOST, REALM, SCENE, callback=callback)
arena.handle_events()
