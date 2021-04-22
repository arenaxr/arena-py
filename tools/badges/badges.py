# badges.py
#
# Application responds to users in the scene and updates the user avatar with name and badge updates.
import argparse
import csv
import io
import json

import requests
from arena import *

BROKER = "arenaxr.org"
REALM = "realm"
SCENE = "badges-example"
ALLUSERS = {}  # static list by username
ACTUSERS = {}  # actual users by camera id


def init_args():
    global BROKER, REALM, SCENE, ALLUSERS
    parser = argparse.ArgumentParser(
        description="ARENA badges manager example.")
    parser.add_argument(
        "-u", "--userfile", type=str, help="CSV delimited user list")
    args = parser.parse_args()
    print(args)

    r = requests.get(args.userfile)
    buff = io.StringIO(r.text)
    dr = csv.DictReader(buff)
    for row in dr:
        key = row["Username"]
        ALLUSERS[key] = row
    print(ALLUSERS)


def scene_callback(scene, obj, msg):
    global ACTUSERS
    #print("on_msg_callback "+str(obj))
    cam_id = obj.object_id
    # publish actual user overrides
    # TODO: check frequency
    if cam_id in ACTUSERS:
        res = scene._publish(ACTUSERS[cam_id]["headtext"], "update")
    return


def user_join_callback(scene, obj, msg):
    global ACTUSERS
    #print("user_join_callback "+str(obj))
    cam_id = obj.object_id
    username = obj.object_id[18:]
    print(username)
    # Add our version of local avatar objects to actual users dict
    text_id = f"headtext_{cam_id}"
    #model_id = f"head-model_{cam_id}"
    #mute_id = f"muted_{cam_id}"
    ht_obj = Text(object_id=text_id, text=f"{obj.displayName} ({username})")
    if cam_id not in ACTUSERS:
        ACTUSERS[cam_id] = {"headtext": ht_obj}
    return


def user_left_callback(scene, obj, msg):
    #print("user_left_callback "+str(obj))
    return


def end_program_callback(scene, obj, msg):
    #print("end_program_callback "+str(obj))
    return


# parse args and wait for events
init_args()
kwargs = {}
scene = Scene(
    host=BROKER,
    realm=REALM,
    scene=SCENE,
    on_msg_callback=scene_callback,
    user_join_callback=user_join_callback,
    user_left_callback=user_left_callback,
    end_program_callback=end_program_callback,
    **kwargs)
scene.run_tasks()
