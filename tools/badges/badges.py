# badges.py
#
# Application responds to users in the scene and updates the user avatar with name and badge updates.
import argparse
import math
import os
import re
import time

import yaml
from arena import *

from gstable import GoogleSheetTable

DFT_CONFIG_FILENAME = './config.yaml'
HOST = "arenaxr.org"
REALM = "realm"
SCENE = "badges-example"
ALLUSERS = {}  # static list by username
ACTUSERS = {}  # actual users by camera id
config = {}


def init_args():
    global ALLUSERS, config

    parser = argparse.ArgumentParser(
        description="ARENA badges manager example.")
    parser.add_argument('-c', '--conf', dest='configfile', default=DFT_CONFIG_FILENAME, action='store', type=str,
                        help=f'The configuration file. Default is {DFT_CONFIG_FILENAME}')
    parser.add_argument('-s', dest='scenename', default=None,
                        help='Scenename of the poster session (e.g. theme1, theme2)')
    args = parser.parse_args()
    print(args)

    # load config
    with open(args.configfile) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    # save scenename in config
    if args.scenename is not None:
        config['arena']['scenename'] = args.scenename

    # check config
    if (config.get('arena') == None):
        print("Config missing 'arena' section")
        exit(1)

    if (config['arena'].get('scenename') == None):
        print("Config missing 'arena.scenename'.")
        exit(1)

    if (config.get('input_table') == None):
        print("Config missing 'input_table' section")
        exit(1)

    if (config['input_table'].get('spreadsheetid') == None):
        print("Config missing 'input_table.spreadsheetid'.")
        exit(1)

    if (config['input_table'].get('named_range') == None):
        print("Config missing 'input_table.named_range'.")
        exit(1)

    if (config.get('icons') == None):
        print("Config missing 'icons' section")
        exit(1)

    # get data from google spreadsheet table
    print('Getting data...')
    gst = GoogleSheetTable()
    data = gst.aslist(config['input_table']['spreadsheetid'],
                      config['input_table']['named_range'])

    # filter by scenename in config
    filtered = list(
        filter(lambda v: v['scene'] == config['arena']['scenename'], data))


def scene_callback(scene, obj, msg):
    global ACTUSERS
    # TODO: TBD
    return


def user_join_callback(scene, obj, msg):
    global ACTUSERS
    cam_id = obj.object_id
    username = obj.object_id[18:]
    print(username)
    # Add our version of local avatar objects to actual users dict
    text_id = f"headtext_{cam_id}"
    #model_id = f"head-model_{cam_id}"
    #mute_id = f"muted_{cam_id}"
    ht_obj = Text(object_id=text_id, parent=cam_id,
                  text=f"{obj.displayName} ({username})")
    print(f"{cam_id} headtext stored as '{ht_obj.data.text}'")
    if cam_id not in ACTUSERS:
        ACTUSERS[cam_id] = {"headtext": ht_obj}
    # publish all overrides so new users will see them
    for user in ACTUSERS:
        scene.update_object(ACTUSERS[user]["headtext"])
        print(f"{user} headtext published")
    return


def user_left_callback(scene, obj, msg):
    # TODO: TBD
    return


def end_program_callback(scene, obj, msg):
    # TODO: TBD
    return


# parse args and wait for events
init_args()
kwargs = {}
scene = Scene(
    host=HOST,
    realm=REALM,
    scene=SCENE,
    on_msg_callback=scene_callback,
    user_join_callback=user_join_callback,
    user_left_callback=user_left_callback,
    end_program_callback=end_program_callback,
    **kwargs)
#scene = Scene(host=config['arena']['host'], realm=config['arena']['realm'], scene=config['arena']['scenename'])


ball1 = Sphere(
    object_id="ball1",
    persist=True,
    clickable=True,
    position=(-2, 2, -7),
    scale=(0.25, 0.25, 0.25),
    material=Material(color="#ff00a5"))
cube1 = Box(
    object_id="cube1",
    persist=True,
    clickable=True,
    position=(0, 2, -7),
    scale=(0.5, 0.5, 0.5),
    material=Material(color="#00ff00"))
cone1 = Cone(
    object_id="cone1",
    persist=True,
    clickable=True,
    position=(2, 2, -7),
    scale=(0.25, 0.5, 0.25),
    material=Material(color="#0000ff"))
scene.add_object(ball1)
scene.add_object(cube1)
scene.add_object(cone1)


scene.run_tasks()
