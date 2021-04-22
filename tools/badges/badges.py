# badges.py
#
# Application responds to users in the scene and updates the user avatar with name and badge updates.
import argparse
import csv

import requests
from arena import *

BROKER = "arenaxr.org"
REALM = "realm"
SCENE = "badges-example"


def init_args():
    global BROKER, REALM, SCENE
    parser = argparse.ArgumentParser(description="ARENA example badges manager.")
    parser.add_argument(
        "-u", "--userfile", type=str, help="CSV delimited user list")
    args = parser.parse_args()
    print(args)

    with requests.Session() as s:
        download = s.get(args.userfile)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        for row in my_list:
            print(row)


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
    user_join_callback = user_join_callback,
    user_left_callback = user_left_callback,
    end_program_callback=end_program_callback,
    **kwargs)
scene.run_tasks()
