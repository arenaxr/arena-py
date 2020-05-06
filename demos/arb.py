# arb.py
#
# AR Builder
# Pass in args for scene name and/or broker and realm.
# Left click/tilt: cycle builder modes.
# Right click/tilt: cycle mode options.
# Mouse/reticle click/tap: activate mode action.

import arena
import random
import json
import urllib.request
import argparse
from enum import Enum
import datetime

BROKER = "oz.andrew.cmu.edu"
REALM = "realm"
SCENE = ""  # no default scene, arb works on any scene

CLIPBOARD = "clipboard"
HUD_BLEFT = "hudButtonLeft"
HUD_BRIGHT = "hudButtonRight"
HUD_TLEFT = "hudTextLeft"
HUD_TRIGHT = "hudTextRight"
HUD_TSTATUS = "hudTextStatus"


class Mode(Enum):
    EDIT = 0  # edit is default
    CREATE = 1

    def first(self):
        cls = self.__class__
        return list(cls)[0]

    def next(self):
        cls = self.__class__
        members = list(cls)
        index = members.index(self) + 1
        if index >= len(members):
            raise StopIteration('end of Mode reached')
        return members[index]

    def prev(self):
        cls = self.__class__
        members = list(cls)
        index = members.index(self) - 1
        if index < 0:
            raise StopIteration('beginning of Mode reached')
        return members[index]


fontScale = (0.1, 0.1, 0.1)
fontColor = (200, 200, 200)
tilt_z_threshhold = 0.2
tilt_ms = 150
tilt_lock = False
cam_timestamp = datetime.datetime.utcnow()
args = None
mode = Mode.EDIT

# TODO: https://oz.andrew.cmu.edu/persist/<scene>/<object_id>
# TODO: https://xr.andrew.cmu.edu/go/ interface to add AR builder
# TODO: https://xr.andrew.cmu.edu/build.html go to page from edit function

# TODO: cleanup of scene method
# TODO: gui select objects
# TODO: Add args for broker and realm.

# *TODO: move source into functions

# order of modes
#    LEFT-MODE   MOUSECLICK     RIGHT-ACTION
# --------------------------------------------
#    move       copy/update    location/rotation
#    create      create obj     next new obj
#    edit*        build.html
#    delete      delete obj
# --------------------------------------------
# * default mode

# TODO: clip edit = invisible

# TODO: ALL: Left -> Next mode (display current)

# TODO: CREATE: Click -> Create object at click
# TODO: CREATE: Right -> Next clipboard obj in manifest

# TODO: EDIT: Click -> Select (highlight)
# TODO: EDIT: Right -> Go to edit page

# TODO: MOVE: Click -> Copy (to clipboard)
# TODO: MOVE: Right -> ...


def initArgs():
    global SCENE

    parser = argparse.ArgumentParser(description='ARENA AR Builder.')
    parser.add_argument('scene', type=str, help='ARENA scene name')

    args = parser.parse_args()
    print(args)
    SCENE = args.scene


def randcolor():
    x = random.randint(0, 255)
    y = random.randint(0, 255)
    z = random.randint(0, 255)
    return(x, y, z)


def set_clipboard():
    return arena.Object(
        persist=False,
        objName=CLIPBOARD,
        objType=arena.Shape.sphere,
        color=randcolor(),
        location=(0.0, 0.0, -1),
        parent="myCamera",
        scale=(0.05, 0.05, 0.05),
        data='{"material": {"transparent": true, "opacity": 0.3}}',
        clickable=True,  # for everything?
    )


def moveObj(object_id, position):
    MESSAGE = {
        "object_id": object_id,
        "action": "update",
        "data": {
            "position": {
                "x": position[0],
                "y": position[1],
                "z": position[2],
            },
        },
    }
    arena.arena_publish(REALM + "/s/" + SCENE, MESSAGE)


def rotateObj(object_id, rotation):
    MESSAGE = {
        "object_id": object_id,
        "action": "update",
        "data": {
            "rotation": {
                "x": rotation[0],
                "y": rotation[1],
                "z": rotation[2],
                "w": rotation[3],
            },
        },
    }
    arena.arena_publish(REALM + "/s/" + SCENE, MESSAGE)


def deleteObj(object_id):
    MESSAGE = {
        "object_id": object_id,
        "action": "delete"
    }
    arena.arena_publish(REALM + "/s/" + SCENE, MESSAGE)


def doModeChange():
    global mode, clipboard
    try:
        mode = mode.next()
    except StopIteration:
        mode = mode.first()

    # make/unmake camera tracking object
    if mode == Mode.EDIT:
        clipboard.delete()
        hudTextRight.update(data='{"text":""}')
    elif mode == Mode.CREATE:
        clipboard = set_clipboard()
        hudTextRight.update(data='{"text":"' + "Change Color" + '"}')

    hudTextLeft.update(data='{"text":"' + getModeName(mode) + '"}')


def getModeName(mode):
    return str(mode)


def doCreateRight():
    global clipboard
    # TODO: implement me!
    # for now just change clip color
    clipboard = set_clipboard()


def doEditRight():
    # TODO: implement me!
    return


def doCreateClick(clipboard, jsonMsg):
    # first way, place object at clickable clipboard
    click = jsonMsg["data"]["position"]
    pos_x = click["x"]
    pos_y = click["y"]
    pos_z = click["z"]
    # second way, place object at calculated vector from cam
    # TODO: almost there, need to calc slope of cam rotation
    # cam = jsonMsg["data"]["clickPos"]
    # pos_x = cam["x"] + clipboard.location[0]
    # pos_y = cam["y"] + clipboard.location[1]
    # pos_z = cam["z"] + clipboard.location[2]
    randstr = str(random.randrange(0, 1000000))
    # make a copy of static object in place
    newObj = arena.Object(persist=True,
                          objName="ballN_" + randstr,  # rand?
                          objType=clipboard.objType,
                          location=(pos_x, pos_y, pos_z),
                          # rotation=clipboard.rotation, #must calc.
                          scale=clipboard.scale,
                          color=clipboard.color,
                          data='{"material": {"transparent": false}}',
                          clickable=True)
    print (newObj)


# This is the MQTT message callback function for the scene
def scene_callback(msg):
    global mode, hudTextStatus, hudTextLeft, tilt_lock, cam_timestamp

    jsonMsg = json.loads(msg)
    print(msg)

    # camera updates are useful to detect AR-counter/clockwise tilts for controls
    # TODO: only do this for this user's camera
    if jsonMsg["action"] == "create" and jsonMsg["data"]["object_type"] == "camera":
        tilt = jsonMsg["data"]["rotation"]["z"]
        now_timestamp = datetime.datetime.strptime(
            jsonMsg["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
        duration = now_timestamp - cam_timestamp
        timediff = duration.microseconds / 1000
        print (timediff)
        if (not tilt_lock) and (timediff < tilt_ms):
            if tilt > tilt_z_threshhold:  # left
                tilt_lock = True
                hudButtonLeft.fireEvent(arena.EventType.mousedown)
            elif tilt < -tilt_z_threshhold:  # right
                tilt_lock = True
                hudButtonRight.fireEvent(arena.EventType.mousedown)
        else:
            if tilt < tilt_z_threshhold and tilt > -tilt_z_threshhold:  # back to center
                tilt_lock = False

        cam_timestamp = now_timestamp

    elif jsonMsg["action"] == "clientEvent":

        # show objects with events
        if jsonMsg["type"] == "mouseenter":
            hudTextStatus.update(
                data='{"text":"' + jsonMsg["object_id"] + '"}')
        elif jsonMsg["type"] == "mouseleave":
            hudTextStatus.update(data='{"text":"' + "" + '"}')

        # handle click
        elif jsonMsg["type"] == "mousedown":

            # Left Option: change modes
            if jsonMsg["object_id"] == HUD_BLEFT:
                doModeChange()

            # Right Option: mode-dependant action
            elif jsonMsg["object_id"] == HUD_BRIGHT:
                if mode == Mode.EDIT:
                    doEditRight()
                elif mode == Mode.CREATE:
                    doCreateRight()

            # clicked cursor
            elif jsonMsg["object_id"] == CLIPBOARD:
                if mode == Mode.EDIT:
                    doEditClick()
                elif mode == Mode.CREATE:
                    doCreateClick(clipboard, jsonMsg)


initArgs()
random.seed()
# data = urllib.request.urlopen(
#     'https://oz.andrew.cmu.edu/persist/' + SCENE).read()
# output = json.loads(data)
# print (output)

arena.init(BROKER, REALM, SCENE, scene_callback)

# origin object
arena.Object(objType=arena.Shape.cube, objName="arb-origin",
             location=(0, 0, 0), color=(0, 0, 255), scale=(0.1, 0.1, 0.1), persist=False)

# TODO: set huds specific to each user
hudTextLeft = arena.Object(objName=HUD_TLEFT, objType=arena.Shape.text, parent="myCamera", data='{"text":"' + getModeName(mode) + '"}',
                           location=(-0.15, 0.15, -0.5), color=(fontColor), scale=(fontScale))
hudTextRight = arena.Object(objName=HUD_TRIGHT, objType=arena.Shape.text, parent="myCamera", data='{"text":""}',
                            location=(0.15, 0.15, -0.5), color=(fontColor), scale=(fontScale))
hudTextStatus = arena.Object(objName=HUD_TSTATUS, objType=arena.Shape.text, parent="myCamera",
                             location=(0, -0.15, -0.5), color=(fontColor), scale=(fontScale))

# TODO: better icons for mode toggle
hudButtonLeft = arena.Object(objName=HUD_BLEFT, objType=arena.Shape.image, parent="myCamera",
                             url="images/conix-x.png",
                             data='{"material": {"transparent": true, "opacity": 0.7}}',
                             location=(-0.15, 0.25, -0.5), scale=(0.1, 0.1, 0.1), clickable=True)
hudButtonRight = arena.Object(objName=HUD_BRIGHT, objType=arena.Shape.image, parent="myCamera",
                              url="images/conix-x.png",
                              data='{"material": {"transparent": true, "opacity": 0.7}}',
                              location=(0.15, 0.25, -0.5), scale=(0.1, 0.1, 0.1), clickable=True)

arena.handle_events()
