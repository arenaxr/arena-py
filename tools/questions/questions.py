# questions.py
#
# Gives user ability to turn a question mark on or offover their avatar.
import argparse

import yaml
from arena import Image, Material, Scene

DFT_CONFIG_FILENAME = './config.yaml'
ACTUSERS = {}  # actual users by camera id
config = {}
data = []


def init_args():
    global config

    parser = argparse.ArgumentParser(
        description="ARENA questions manager example.")
    parser.add_argument('-c', '--conf', dest='configfile', default=DFT_CONFIG_FILENAME, action='store', type=str,
                        help=f'The configuration file. Default is {DFT_CONFIG_FILENAME}')
    parser.add_argument('-b', dest='host', default=None,
                        help='Hostname/broker for Questions')
    parser.add_argument('-r', dest='realm', default=None,
                        help='Realm for Questions')
    parser.add_argument('-n', dest='namespace', default=None,
                        help='Namespace for Questions')
    parser.add_argument('-s', dest='scenename', default=None,
                        help='Scenename for Questions (e.g. theme1, theme2)')
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


def publish_badge(_scene, badge_idx, cam_id, badge_icon):
    # update arena viewers of this scene
    global config
    if badge_icon not in config["badge_icons"]:
        return
    badge_icon_id = f"badge{badge_idx}_{cam_id}"
    # if badge_icon_id in _scene.all_objects:
    #     return  # already published
    offset = 0.03
    if (badge_idx % 2) == 0:  # alternate badge sides
        pos = (badge_idx / 2 * -offset)  # even
    else:
        pos = (badge_idx / 2 * offset) + (offset / 2)  # odd
    badge = Image(
        object_id=badge_icon_id,
        parent=cam_id,
        clickable=True,
        position=(pos, -0.15, -0.35),
        rotation=(0, 1, 0, 0),
        scale=(0.02, 0.02, 0.02),
        material=Material(
            transparent=False,
            alphaTest=0.5,
            shader='flat',
            side='double'),
        url=config["badge_icons"][badge_icon])
    _scene.add_object(badge)
    print(f"{badge_icon_id} published")
    # TODO: push config into parsable yaml


def scene_callback(_scene, obj, msg):
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
                # strip camera_00123456789_ for username
                username = cam_id[18:]
                if cam_id not in ACTUSERS:
                    ACTUSERS[cam_id] = {}
                if "questions" not in ACTUSERS[cam_id]:
                    ACTUSERS[cam_id]["questions"] = []
                # check if update to data model is needed, or if this is a dupe
                if object_id not in ACTUSERS[cam_id]["questions"]:
                    ACTUSERS[cam_id]["questions"].append(object_id)
                    badge_idx = len(ACTUSERS[cam_id]["questions"])-1
                    publish_badge(_scene=_scene,
                                  badge_idx=badge_idx,
                                  cam_id=cam_id,
                                  badge_icon=object_id)


def user_left_callback(_scene, obj, msg):
    global ACTUSERS
    cam_id = obj.object_id
    username = cam_id[18:]  # strip camera_00123456789_ for username
    print(f"{username} left")
    if cam_id in ACTUSERS:
        del ACTUSERS[cam_id]


def user_join_callback(_scene, obj, msg):
    global ACTUSERS, config, data
    cam_id = obj.object_id
    username = cam_id[18:]  # strip camera_00123456789_ for username
    print(f"{username} joined")
    # Add our version of local avatar objects to actual users dict
    if cam_id not in ACTUSERS:
        sheet_user = next(
            filter(lambda x: x['username'] == username, data), None)
        if sheet_user:
            role_icon_id = f"roleicon_{cam_id}"
            ACTUSERS[cam_id] = {}
            ACTUSERS[cam_id]['questions'] = []
            idx = 0
            while f'badge{idx}' in sheet_user:
                ACTUSERS[cam_id]['questions'].append(sheet_user[f'badge{idx}'])
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
            _scene.add_object(ACTUSERS[user]["roleicon"])
            print(f"{user} roleicon published")
        if 'questions' in ACTUSERS[user]:
            for i in range(len(ACTUSERS[user]["questions"])):
                publish_badge(_scene=_scene,
                              badge_idx=i,
                              cam_id=user,
                              badge_icon=ACTUSERS[user]["questions"][i])


def end_program_callback(_scene: Scene):
    # remove icons
    for user in ACTUSERS:
        if 'roleicon' in ACTUSERS[user]:
            _scene.delete_object(ACTUSERS[user]["roleicon"])
        if 'questions' in ACTUSERS[user]:
            for i in range(len(ACTUSERS[user]["questions"])):
                obj = _scene.all_objects[ACTUSERS[user]["questions"][i]]
                _scene.delete_object(obj)


# parse args and config
init_args()

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
    user_left_callback=user_left_callback,
    end_program_callback=end_program_callback,
    ** kwargs)

scene.run_tasks()
