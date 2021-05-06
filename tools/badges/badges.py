# badges.py
#
# Application responds to users in the scene and updates the user avatar with name and badge updates.
import argparse

import yaml
from arena import *

from gstable import GoogleSheetTable

DFT_CONFIG_FILENAME = './config.yaml'
ACTUSERS = {}  # actual users by camera id
config = {}
data = []


def init_args():
    global config

    parser = argparse.ArgumentParser(
        description="ARENA badges manager example.")
    parser.add_argument('-c', '--conf', dest='configfile', default=DFT_CONFIG_FILENAME, action='store', type=str,
                        help=f'The configuration file. Default is {DFT_CONFIG_FILENAME}')
    parser.add_argument('-b', dest='host', default=None,
                        help='Hostname/broker for Badges')
    parser.add_argument('-r', dest='realm', default=None,
                        help='Realm for Badges')
    parser.add_argument('-n', dest='namespace', default=None,
                        help='Namespace for Badges')
    parser.add_argument('-s', dest='scenename', default=None,
                        help='Scenename for Badges (e.g. theme1, theme2)')
    args = parser.parse_args()
    print(args)

    # load config
    with open(args.configfile) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    # override config
    if args.host is not None:
        config['arena']['host'] = args.host
    if args.realm is not None:
        config['arena']['realm'] = args.realm
    if args.namespace is not None:
        config['arena']['namespace'] = args.namespace
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


def publish_badge(scene, badge_idx, cam_id, badge_icon):
    # update arena viewers of this scene
    global config
    badge_icon_id = f"badge{badge_idx}_{cam_id}"
    # if badge_icon_id in scene.all_objects:
    #     return  # already published
    offset = 0.03
    if (badge_idx % 2) == 0:  # alternate badge sides
        pos = (badge_idx / 2 * -offset)  # even
    else:
        pos = (badge_idx / 2 * offset) + (offset / 2)  # odd
    print(f"{badge_idx} {pos} {badge_icon_id}")
    badge = Image(
        object_id=badge_icon_id,
        parent=cam_id,
        position=(pos, -0.15, -0.35),
        rotation=(0, 1, 0, 0),
        scale=(0.02, 0.02, 0.02),
        material=Material(
            transparent=False,
            alphaTest=0.5,
            shader='flat',
            side='double'),
        url=config["badge_icons"][badge_icon])
    scene.add_object(badge)
    # TODO: push config into parsable yaml


def scene_callback(scene, obj, msg):
    global ACTUSERS, config, data
    object_id = action = msg_type = object_type = None
    if "object_id" in msg:
        object_id = msg["object_id"]
    if "action" in msg:
        action = msg["action"]
    if "type" in msg:
        msg_type = msg["type"]
    if "data" in msg and "object_type" in msg["data"]:
        object_type = msg["data"]["object_type"]

    # only process known object_ids for badge clicks
    if action == "clientEvent":
        # handle click
        if msg_type == "mousedown":
            # parse clicks from known badge name object ids
            if object_id in config["badge_icons"]:
                cam_id = msg["data"]["source"]
                username = cam_id[18:]  # strip camera_00123456789 for username
                print(f"{object_id} is an expected click from {username}")
                if cam_id not in ACTUSERS:
                    ACTUSERS[cam_id] = {}
                if "badges" not in ACTUSERS[cam_id]:
                    ACTUSERS[cam_id]["badges"] = []
                # check if update to data model is needed, or if this is a dupe
                if object_id not in ACTUSERS[cam_id]["badges"]:
                    ACTUSERS[cam_id]["badges"].append(object_id)
                    badge_idx = len(ACTUSERS[cam_id]["badges"])-1
                    publish_badge(scene=scene,
                                  badge_idx=badge_idx,
                                  cam_id=cam_id,
                                  badge_icon=object_id)
                    # update data model, local and remote
                    sheet_user = next(
                        filter(lambda x: x['username'] == username, data), None)
                    if not sheet_user:
                        data = gst.addrow(config['input_table']['spreadsheetid'],
                                          config['input_table']['named_range'],
                                          [username])
                    # update online badges
                    row = next((index for (index, d) in enumerate(
                        data) if d['username'] == username), None)
                    data = gst.updaterow(config['input_table']['spreadsheetid'],
                                         f"{config['input_table']['named_range']}!C{row+2}",
                                         ACTUSERS[cam_id]["badges"])


def user_join_callback(scene, obj, msg):
    # TODO: handle displayname update message
    # TODO: handle no name incoming displayname message
    global ACTUSERS, config, data
    cam_id = obj.object_id
    username = cam_id[18:]  # strip camera_00123456789 for username
    print(username)

    # get data from google spreadsheet table
    print('Getting data...')
    data = gst.aslist(config['input_table']['spreadsheetid'],
                      config['input_table']['named_range'])
    # Add our version of local avatar objects to actual users dict
    if cam_id not in ACTUSERS:
        sheet_user = next(
            filter(lambda x: x['username'] == username, data), None)
        if sheet_user:
            role_icon_id = f"roleicon_{cam_id}"
            ACTUSERS[cam_id] = {}
            ACTUSERS[cam_id]['badges'] = []
            idx = 0
            while f'badge{idx}' in sheet_user:
                ACTUSERS[cam_id]['badges'].append(sheet_user[f'badge{idx}'])
                idx += 1
            # update static user role data from table
            if 'role' in sheet_user:
                role = sheet_user['role']
                if role in config['role_icons']:
                    ACTUSERS[cam_id]["roleicon"] = Image(
                        object_id=role_icon_id,
                        parent=cam_id,
                        position=(0, 0.6, 0.045),
                        rotation=(0, 1, 0, 0),
                        scale=(0.2, 0.2, 0.02),
                        material=Material(
                            transparent=False,
                            alphaTest=0.5,
                            shader='flat',
                            side='double'),
                        url=config["role_icons"][role])

    # publish all overrides so new user will see them
    for user in ACTUSERS:
        if 'roleicon' in ACTUSERS[user]:
            scene.add_object(ACTUSERS[user]["roleicon"])
            print(f"{user} roleicon published")
        if 'badges' in ACTUSERS[user]:
            for i in range(len(ACTUSERS[user]["badges"])):
                publish_badge(scene=scene,
                              badge_idx=i,
                              cam_id=user,
                              badge_icon=ACTUSERS[user]["badges"][i])


# parse args and config
init_args()
# establish shared Sheets auth
gst = GoogleSheetTable()

# establish shared ARENA auth
kwargs = {}
if 'namespace' in config['arena']:
    kwargs["namespace"] = config['arena']['namespace']
scene = Scene(
    host=config['arena']['host'],
    realm=config['arena']['realm'],
    scene=config['arena']['scenename'],
    on_msg_callback=scene_callback,
    user_join_callback=user_join_callback,
    **kwargs)

# TODO: launch separate threads for each scene

scene.run_tasks()
