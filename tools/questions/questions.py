# questions.py
#
# Gives user ability to turn a question mark on or offover their avatar.
import argparse

import yaml
from arena import Image, Material, Scene

DFT_CONFIG_FILENAME = "./config.yaml"
ACTUSERS = {}  # actual users by camera id
config = {}
data = []


def init_args():
    global config

    parser = argparse.ArgumentParser(
        description="ARENA question manager example.")
    parser.add_argument("-c", "--conf", dest="configfile", default=DFT_CONFIG_FILENAME, action="store", type=str,
                        help=f"The configuration file. Default is {DFT_CONFIG_FILENAME}")
    parser.add_argument("-b", dest="host", default=None,
                        help="Hostname/broker for Question")
    parser.add_argument("-r", dest="realm", default=None,
                        help="Realm for Question")
    parser.add_argument("-n", dest="namespace", default=None,
                        help="Namespace for Question")
    parser.add_argument("-s", dest="scenename", default=None,
                        help="Scenename for Question (e.g. theme1, theme2)")
    args = parser.parse_args()
    print(args)

    # load config
    with open(args.configfile) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    # override config
    if args.host is not None:
        config["arena"]["host"] = args.host
    if args.realm is not None:
        config["arena"]["realm"] = args.realm
    if args.namespace is not None:
        config["arena"]["namespace"] = args.namespace
    if args.scenename is not None:
        config["arena"]["scenename"] = args.scenename

    # check config
    if (config.get("arena") == None):
        print("Config missing 'arena' section")
        exit(1)

    if (config["arena"].get("scenename") == None):
        print("Config missing 'arena.scenename'.")
        exit(1)

    if (config.get("badge_icons") == None):
        print("Config missing 'icons' section")
        exit(1)

    if (config.get("role_icons") == None):
        print("Config missing 'icons' section")
        exit(1)

    if (config.get("badge") == None):
        print("Config missing 'icons' section")
        exit(1)

    if (config.get("role") == None):
        print("Config missing 'icons' section")
        exit(1)


def publish_badge(_scene: Scene, cam_id, badge_icon, active=False):
    # update arena viewers of this scene
    global config
    if badge_icon not in config["badge_icons"]:
        return
    badge_icon_id = f"badge_{cam_id}"
    if active:
        opacity = 1.0
        transparent = True
    else:
        opacity = 0.25
        transparent = True
    badge = Image(
        object_id=badge_icon_id,
        parent=cam_id,
        clickable=True,
        evt_handler=question_callback,
        position=(0, -0.1, -0.2),  # fit just behind video screen
        rotation=(0, 0, 0),
        scale=(0.02, 0.02, 0.02),
        material=Material(
            transparent=transparent,
            opacity=opacity,
            alphaTest=0.2,
            shader="flat",
            side="double"),
        url=config["badge_icons"][badge_icon])
    _scene.add_object(badge)
    ACTUSERS[cam_id]["badge"] = badge
    print(f"{badge_icon_id} added")

    # TODO: push config into parsable yaml


def publish_roleicon(_scene: Scene, cam_id, role_icon, active=False):
    global config
    if role_icon not in config["role_icons"]:
        return
    role_icon_id = f"roleicon_{cam_id}"
    role = ACTUSERS[cam_id]["roleicon"] = Image(
        object_id=role_icon_id,
        parent=cam_id,
        position=(0, 0.625, 0.045),
        rotation=(0, 180, 0),
        scale=(0.2, 0.2, 0.02),
        material=Material(
            transparent=False,
            alphaTest=0.5,
            shader="flat",
            side="double"),
        url=config["role_icons"][role_icon])
    if active:
        _scene.add_object(role)
        ACTUSERS[cam_id]["roleicon"] = role
        print(f"{role_icon_id} added")
    else:
        _scene.delete_object(role)
        if "roleicon" in ACTUSERS[cam_id]:
            del ACTUSERS[cam_id]["roleicon"]
        print(f"{role_icon_id} removed")


def question_callback(_scene: Scene, event, msg):
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

    # TODO: handle only clicking you own buttons
    if action == "clientEvent":
        # handle click
        if msg_type == "mousedown":
            cam_id = msg["data"]["source"]
            if cam_id in ACTUSERS:
                active = not ("roleicon" in ACTUSERS[cam_id])
                publish_badge(_scene=_scene, cam_id=cam_id,
                              badge_icon="question", active=active)
                publish_roleicon(_scene=_scene, cam_id=cam_id,
                                 role_icon="question", active=active)


def user_left_callback(_scene: Scene, obj, msg):
    global ACTUSERS
    cam_id = obj.object_id
    username = cam_id[18:]  # strip camera_00123456789_ for username
    print(f"{username} left")
    if cam_id in ACTUSERS:
        del ACTUSERS[cam_id]


def user_join_callback(_scene: Scene, obj, msg):
    global ACTUSERS, config, data
    cam_id = obj.object_id
    username = cam_id[18:]  # strip camera_00123456789_ for username
    print(f"{username} joined")
    # publish all overrides so new user will see them
    if cam_id not in ACTUSERS:
        ACTUSERS[cam_id] = {}
    for user in ACTUSERS:
        active = ("roleicon" in ACTUSERS[user])
        publish_badge(_scene=_scene, cam_id=user,
                      badge_icon="question", active=active)
        publish_roleicon(_scene=_scene, cam_id=user,
                         role_icon="question", active=active)


def end_program_callback(_scene: Scene):
    # remove icons
    for user in ACTUSERS:
        if "roleicon" in ACTUSERS[user]:
            _scene.delete_object(ACTUSERS[user]["roleicon"])
        if "badge" in ACTUSERS[user]:
            _scene.delete_object(ACTUSERS[user]["badge"])


# parse args and config
init_args()

# establish shared ARENA auth
kwargs = {}
if "namespace" in config["arena"]:
    kwargs["namespace"] = config["arena"]["namespace"]
scene = Scene(
    host=config["arena"]["host"],
    realm=config["arena"]["realm"],
    scene=config["arena"]["scenename"],
    user_join_callback=user_join_callback,
    user_left_callback=user_left_callback,
    end_program_callback=end_program_callback,
    ** kwargs)

scene.run_tasks()
