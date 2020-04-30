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

BROKER = "oz.andrew.cmu.edu"
REALM = "realm"
SCENE = ""  # no default scene, arb works on any scene

CLIPBOARD = "clipboard"
HUD_LEFT = "hudLeft"
HUD_RIGHT = "hudRight"


class Mode(Enum):
    EDIT = 0  # edit is default
    CREATE = 1


tilt_threshhold = 0.3
args = None
mode = Mode.EDIT

# TODO: https://oz.andrew.cmu.edu/persist/<scene>
# TODO: https://xr.andrew.cmu.edu/go/ interface to add AR builder
# TODO: https://xr.andrew.cmu.edu/build.html go to page from edit function

# TODO: cleanup of scene method
# *TODO: gui AR click activate
# TODO: gui select objects
# TODO: Add args for broker and realm.

# *TODO: left sets mode (create, edit(default), move, delete)
# *TODO: right toggle mode function
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
        data='{"material": {"transparent": true, "opacity": 0.6}}',
        clickable=True,  # for everything?
        # url="https://xr.andrew.cmu.edu/build.html",
    )


def moveObj(object_id, position, rotation):
    MESSAGE = {
        "object_id": object_id,
        "action": "update",
        "data": {
            "position": {
                "x": position[0],
                "y": position[1],
                "z": position[2],
            },
            "rotation": {
                "x": rotation[0],
                "y": rotation[1],
                "z": rotation[2],
                "w": rotation[3],
            },
        },
    }
    arena.arena_publish(REALM + "/s/" + SCENE, MESSAGE)


# This is the MQTT message callback function for the scene
def scene_callback(msg):
    global clipboard, hudStatus, hudSet, hudLeft, hudRight

    jsonMsg = json.loads(msg)
    print(msg)

    # don't filter non-event messages
    # camera updates are useful to detect AR-counter/clockwise tilts for controls
    # TODO: only do this for this user's camera
    if jsonMsg["action"] == "create" and jsonMsg["data"]["object_type"] == "camera":
        tilt = jsonMsg["data"]["rotation"]["z"]
        if tilt > tilt_threshhold:
            hudSet.update(data='{"text":"' + "left" + '"}')
        elif tilt < -tilt_threshhold:
            hudSet.update(data='{"text":"' + "right" + '"}')
        else:
            hudSet.update(data='{"text":"' + "center" + '"}')

    if jsonMsg["action"] == "clientEvent":

        # show objects with events
        if jsonMsg["type"] == "mouseenter":
            hudStatus.update(data='{"text":"' + jsonMsg["object_id"] + '"}')
        if jsonMsg["type"] == "mouseleave":
            hudStatus.update(data='{"text":"' + "" + '"}')

        # handle click
        if jsonMsg["type"] == "mousedown":
            if jsonMsg["object_id"] == HUD_LEFT:
                clipboard = set_clipboard()
            if jsonMsg["object_id"] == HUD_RIGHT:
                clipboard = set_clipboard()

            # clicked set object
            if jsonMsg["object_id"] == CLIPBOARD:

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
                newObj = arena.Object(
                    persist=True,
                    objName="ballN_" + randstr,  # rand?
                    objType=clipboard.objType,
                    location=(pos_x, pos_y, pos_z),
                    # rotation=clipboard.rotation, #must calc.
                    scale=clipboard.scale,
                    color=clipboard.color,
                    data='{"material": {"transparent": false}}',
                    clickable=True,
                )
                print(newObj)


initArgs()
random.seed()
data = urllib.request.urlopen(
    'https://oz.andrew.cmu.edu/persist/' + SCENE).read()
output = json.loads(data)
print (output)

arena.init(BROKER, REALM, SCENE, scene_callback)

arena.Object(objType=arena.Shape.cube, objName="arb-origin",
             location=(0, 0, 0), color=(0, 0, 255), scale=(0.1, 0.1, 0.1), persist=False)

# make camera tracking object
clipboard = set_clipboard()

# TODO: set huds specific to each user
hudSet = arena.Object(objName="hudSet", objType=arena.Shape.text, parent="myCamera",
                      location=(0, 0.15, -0.5), color=(200, 200, 200), scale=(0.1, 0.1, 0.1))
hudStatus = arena.Object(objName="hudStatus", objType=arena.Shape.text, parent="myCamera",
                         location=(0, -0.15, -0.5), color=(200, 200, 200), scale=(0.1, 0.1, 0.1))
# TODO: better icons for mode toggle
hudLeft = arena.Object(objName=HUD_LEFT, objType=arena.Shape.image, parent="myCamera",
                       url="images/conix-x.png",
                       location=(-0.2, 0.35, -0.5), scale=(0.1, 0.1, 0.1), clickable=True)
hudRight = arena.Object(objName=HUD_RIGHT, objType=arena.Shape.image, parent="myCamera",
                        url="images/conix-x.png",
                        location=(0.2, 0.35, -0.5), scale=(0.1, 0.1, 0.1), clickable=True)

arena.handle_events()
