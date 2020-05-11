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
FONTSCALE = (0.1, 0.1, 0.1)
FONTCOLOR = (200, 200, 200)
TILT_THRESHOLD = 0.2
TILT_MS = 150

users = {}  # dictionary of user instances
args = None


class Mode(Enum):
    EDIT = "edit"  # edit is default
    MOVE = "move"
    CREATE = "create"
    DELETE = "delete"

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


class User:
    def __init__(self, camname):
        self.camname = camname
        self.tilt_lock = False
        self.cam_timestamp = datetime.datetime.utcnow()
        self.mode = Mode.EDIT
        self.target_id = None

        # origin object
        # TODO: origin should be like a red flashing light
        arena.Object(objType=arena.Shape.cube, objName="arb-origin",
                     data='{"material": {"transparent": true, "opacity": 0.3}}',
                     location=(0, 0, 0), color=(255, 0, 0), scale=(0.1, 0.1, 0.1), persist=False)

        # set HUD to each user
        # TODO: construction helmet
        self.clipboard = set_clipboard(camname)
        self.clipboard.delete()  # workaround for non-empty object
        self.hudTextLeft = arena.Object(objName=(HUD_TLEFT + "_" + camname), objType=arena.Shape.text, parent=camname, data='{"text":"' + getModeName(self.mode) + '"}',
                                        location=(-0.15, 0.15, -0.5), color=(FONTCOLOR), scale=(FONTSCALE))
        self.hudTextRight = arena.Object(objName=(HUD_TRIGHT + "_" + camname), objType=arena.Shape.text, parent=camname, data='{"text":""}',
                                         location=(0.15, 0.15, -0.5), color=(FONTCOLOR), scale=(FONTSCALE))
        self.hudTextStatus = arena.Object(objName=(HUD_TSTATUS + "_" + camname), objType=arena.Shape.text, parent=camname, data='{"text":""}',
                                          location=(0, -0.1, -0.5), color=(FONTCOLOR), scale=(FONTSCALE))
        # TODO: better icons for mode toggle
        self.hudButtonLeft = arena.Object(objName=(HUD_BLEFT + "_" + camname), objType=arena.Shape.image, parent=camname,
                                          url="images/conix-x.png",
                                          data='{"material": {"transparent": true, "opacity": 0.7}}',
                                          location=(-0.15, 0.25, -0.5), scale=(0.1, 0.1, 0.1), clickable=True)
        self.hudButtonRight = arena.Object(objName=(HUD_BRIGHT + "_" + camname), objType=arena.Shape.image, parent=camname,
                                           url="images/conix-x.png",
                                           data='{"material": {"transparent": true, "opacity": 0.7}}',
                                           location=(0.15, 0.25, -0.5), scale=(0.1, 0.1, 0.1), clickable=True)


# TODO: https://oz.andrew.cmu.edu/persist/<scene>/<object_id>
# TODO: https://xr.andrew.cmu.edu/go/ interface to add AR builder
# TODO: https://xr.andrew.cmu.edu/build.html go to page from edit function

# TODO: cleanup of scene method
# TODO: gui select objects
# TODO: Add args for broker and realm.

# order of modes
#    LEFT-MODE   MOUSECLICK     RIGHT-ACTION
# --------------------------------------------
#    edit*       build.html?
#    move        copy/update    location nudge
#    create      create obj     next new obj
#    delete      delete obj
# --------------------------------------------
# * default mode


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


def set_clipboard(camname,
                  type=arena.Shape.sphere,
                  rotation=(0, 0, 0, 1),
                  scale=(0.05, 0.05, 0.05),
                  color=(255, 255, 255),
                  ):
    return arena.Object(
        persist=False,
        objName=(CLIPBOARD + "_" + camname),
        objType=type,
        color=color,
        location=(0.0, 0.0, -1),
        rotation=rotation,
        parent=camname,
        scale=scale,
        data='{"material": {"transparent": true, "opacity": 0.3}}',
        # data='{"goto-url": "on: mousedown; url://' + BROKER + '/persist/' +
        # SCENE + '/' + object_id + ';"}',
        clickable=True,
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
    # print(json.dumps(MESSAGE))  # TODO: not relocating?
    print("Relocated " + object_id)


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
    print("Rotated " + object_id)


def deleteObj(object_id):
    MESSAGE = {
        "object_id": object_id,
        "action": "delete"
    }
    arena.arena_publish(REALM + "/s/" + SCENE, MESSAGE)
    print("Deleted " + object_id)


def doModeChange(camname, mode):
    global users

    # make/unmake camera tracking objects
    if mode == Mode.EDIT:
        users[camname].clipboard.delete()
        users[camname].hudTextRight.update(data='{"text":""}')
    elif mode == Mode.CREATE:
        users[camname].clipboard = set_clipboard(camname)
        users[camname].hudTextRight.update(
            data='{"text":"' + "Change Color" + '"}')
    elif mode == Mode.DELETE:
        users[camname].clipboard.delete()
        users[camname].hudTextRight.update(data='{"text":""}')

    users[camname].hudTextLeft.update(
        data='{"text":"' + getModeName(mode) + '"}')


def getModeName(mode):
    return str(mode)


def getClickLocation(jsonMsg):
    click = jsonMsg["data"]["position"]
    pos_x = click["x"]
    pos_y = click["y"]
    pos_z = click["z"]
    return (pos_x, pos_y, pos_z)


def doMoveSelect(camname, object_id):
    global users
    prop = getNetworkPersistedObject(object_id)
    users[camname].target_id = object_id
    rotation = (prop[0]["attributes"]["rotation"]["x"],
                prop[0]["attributes"]["rotation"]["y"],
                prop[0]["attributes"]["rotation"]["z"],
                prop[0]["attributes"]["rotation"]["w"])
    scale = (prop[0]["attributes"]["scale"]["x"],
             prop[0]["attributes"]["scale"]["y"],
             prop[0]["attributes"]["scale"]["z"])
    hClr = prop[0]["attributes"]["color"].lstrip('#')
    color = tuple(int(hClr[i:i + 2], 16) for i in (0, 2, 4))
    users[camname].clipboard = set_clipboard(camname,
                                             type=arena.Shape(
                                                 prop[0]["attributes"]["object_type"]),
                                             rotation=rotation,
                                             scale=scale,
                                             color=color,
                                             )


def doMoveRelocate(camname, jsonMsg):
    global users
    newlocation = getClickLocation(jsonMsg)
    moveObj(users[camname].target_id, newlocation)
    users[camname].clipboard.delete()
    users[camname].target_id = None


def doCreateRight(camname):
    global users
    # TODO: this should cycle through shapes...
    # for now just change clip color
    users[camname].clipboard = set_clipboard(camname, color=randcolor())


def createObj(clipboard, jsonMsg):
    # first way, place object at clickable clipboard
    location = getClickLocation(jsonMsg)

    randstr = str(random.randrange(0, 1000000))
    # make a copy of static object in place
    newObj = arena.Object(persist=True,
                          objName=clipboard.objType.name + "_" + randstr,
                          objType=clipboard.objType,
                          location=location,
                          rotation=clipboard.rotation,
                          scale=clipboard.scale,
                          color=clipboard.color,
                          data='{"material": {"transparent": false}}',
                          clickable=True)
    print("Created " + newObj.objName)


def scene_callback(msg):
    # This is the MQTT message callback function for the scene
    global users

    jsonMsg = json.loads(msg)
    # print(msg)

    # camera updates are useful to detect AR-counter/clockwise tilts
    if jsonMsg["action"] == "create" and jsonMsg["data"]["object_type"] == "camera":
        # camera updates define users present
        camname = jsonMsg["object_id"]
        if camname not in users:
            users[camname] = User(camname)

        tilt = jsonMsg["data"]["rotation"]["z"]
        now_timestamp = datetime.datetime.strptime(
            jsonMsg["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
        duration = now_timestamp - users[camname].cam_timestamp
        timediff = duration.microseconds / 1000
        if (not users[camname].tilt_lock) and (timediff < TILT_MS):
            if tilt > TILT_THRESHOLD:  # left
                users[camname].tilt_lock = True
                users[camname].hudButtonLeft.fireEvent(
                    event=arena.EventType.mousedown, source=camname)
            elif tilt < -TILT_THRESHOLD:  # right
                users[camname].tilt_lock = True
                users[camname].hudButtonRight.fireEvent(
                    event=arena.EventType.mousedown, source=camname)
        else:
            if tilt < TILT_THRESHOLD and tilt > -TILT_THRESHOLD:  # back to center
                users[camname].tilt_lock = False

        users[camname].cam_timestamp = now_timestamp

    # mouse event
    elif jsonMsg["action"] == "clientEvent":
        # camera updates define users present
        camname = jsonMsg["data"]["source"]
        if camname not in users:
            users[camname] = User(camname)

        # show objects with events
        if jsonMsg["type"] == "mouseenter":
            users[camname].hudTextStatus.update(
                data='{"text":"' + jsonMsg["object_id"] + '"}')
        elif jsonMsg["type"] == "mouseleave":
            users[camname].hudTextStatus.update(data='{"text":"' + "" + '"}')

        # handle click
        elif jsonMsg["type"] == "mousedown":

            # Left Option: change modes
            if jsonMsg["object_id"] == users[camname].hudButtonLeft.objName:
                try:
                    users[camname].mode = users[camname].mode.next()
                except StopIteration:
                    users[camname].mode = users[camname].mode.first()
                doModeChange(camname, users[camname].mode)

            # Right Option: mode-dependent action
            elif jsonMsg["object_id"] == users[camname].hudButtonRight.objName:
                if users[camname].mode == Mode.EDIT:
                    pass  # TODO: doEditRight(camname)
                elif users[camname].mode == Mode.CREATE:
                    doCreateRight(camname)
                elif users[camname].mode == Mode.DELETE:
                    pass  # TODO: doDeleteRight(camname)
                elif users[camname].mode == Mode.MOVE:
                    pass  # TODO: doMoveRight(camname)

            # clicked self HUD clipboard
            elif jsonMsg["object_id"] == users[camname].clipboard.objName:
                if users[camname].mode == Mode.CREATE:
                    createObj(users[camname].clipboard, jsonMsg)
                elif users[camname].mode == Mode.MOVE:
                    doMoveRelocate(camname, jsonMsg)

            # clicked another scene object
            elif len(jsonMsg["object_id"]) > 0:
                if users[camname].mode == Mode.EDIT:
                    pass  # doEditClick(jsonMsg["object_id"])
                elif users[camname].mode == Mode.DELETE:
                    deleteObj(jsonMsg["object_id"])
                elif users[camname].mode == Mode.MOVE:
                    doMoveSelect(camname, jsonMsg["object_id"])


def getNetworkPersistedObject(object_id):
    data = urllib.request.urlopen(
        'https://' + BROKER + '/persist/' + SCENE + '/' + object_id).read()
    output = json.loads(data)
    # print(output)  # TODO: not relocating?
    return output


initArgs()
random.seed()

arena.init(BROKER, REALM, SCENE, scene_callback)
arena.handle_events()
