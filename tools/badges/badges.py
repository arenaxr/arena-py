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
ALLUSERS = {}  # static list by username
ACTUSERS = {}  # actual users by camera id
config = {}
data = []


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

    if (config.get('badge_icons') == None):
        print("Config missing 'icons' section")
        exit(1)

    if (config.get('role_icons') == None):
        print("Config missing 'icons' section")
        exit(1)

    if (config.get('badge') == None):
        print("Config missing 'icons' section")
        exit(1)

    if (config.get('role') == None):
        print("Config missing 'icons' section")
        exit(1)


def scene_callback(scene, obj, msg):
    # TODO: TBD
    return


def user_join_callback(scene, obj, msg):
    global ACTUSERS, config
    cam_id = obj.object_id
    username = obj.object_id[18:]
    print(username)
    # Add our version of local avatar objects to actual users dict
    if cam_id not in ACTUSERS:
        sheet_user = next(filter(lambda x: x['username'] == username, data))
        if sheet_user:
            text_id = f"headtext_{cam_id}"
            role_icon_id = f"roleicon_{cam_id}"
            ACTUSERS[cam_id] = {}
            if 'role' in sheet_user:
                role = sheet_user['role']
                if role in config['role_texts']:
                    ACTUSERS[cam_id]["headtext"] = Text(
                        object_id=text_id,
                        parent=cam_id,
                        text=f"{obj.displayName} {config['role_texts'][role]}")
                if role in config['role_icons']:
                    ACTUSERS[cam_id]["roleicon"] = Image(
                        object_id=role_icon_id,
                        parent=cam_id,
                        position=(0, 0.6, 0.045),
                        rotation=(0, 1, 0, 0),
                        scale=(0.2, 0.2, 0.02),
                        src=f'url({config["role_icons"][role]})')

    # publish all overrides so new user will see them
    for user in ACTUSERS:
        if 'headtext' in ACTUSERS[user]:
            scene.update_object(ACTUSERS[user]["headtext"])
            print(f"{user} headtext published")
        if 'roleicon' in ACTUSERS[user]:
            scene.add_object(ACTUSERS[user]["roleicon"])
            print(f"{user} roleicon published")
    return


def user_left_callback(scene, obj, msg):
    # TODO: TBD
    return


def end_program_callback(scene, obj, msg):
    # TODO: TBD
    return


# parse args and config
init_args()
# establish shared Sheets auth
gst = GoogleSheetTable()

# get data from google spreadsheet table
print('Getting data...')
data = gst.aslist(config['input_table']['spreadsheetid'],
                  config['input_table']['named_range'])

# filter by scenename in config
# filtered = list(
#     filter(lambda v: v['scene'] == config['arena']['scenename'], data))

# establish shared ARENA auth
scene = Scene(
    host=config['arena']['host'],
    realm=config['arena']['realm'],
    scene=config['arena']['scenename'],
    on_msg_callback=scene_callback,
    user_join_callback=user_join_callback,
    user_left_callback=user_left_callback,
    end_program_callback=end_program_callback)

# TODO: launch separate threads for each scene

scene.run_tasks()
