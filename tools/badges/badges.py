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
USERS = {}


def init_args():
    global BROKER, REALM, SCENE, USERS
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
        USERS[key] = row
    print(USERS)


def scene_callback(scene, obj, msg):
    print("on_msg_callback "+str(obj))


def user_join_callback(scene, obj, msg):
    print("user_join_callback "+str(obj))


def user_left_callback(scene, obj, msg):
    print("user_left_callback "+str(obj))


def end_program_callback(scene, obj, msg):
    print("end_program_callback "+str(obj))


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
