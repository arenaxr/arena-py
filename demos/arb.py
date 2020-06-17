# arb.py
#
# AR Builder
# Pass in args for scene name and/or broker and realm.

# future:
#    occlude/unocclude scene (non-persist)
#    worklight on/off
#    rotate
#    level meter 3dof
#    rotate controls to camera
#    subscribe to all mouseenter/leave
#    highlight mouseenter to avoid click

# TODO: arena: https://xr.andrew.cmu.edu/go/ interface to add AR builder
# TODO: arena: https://xr.andrew.cmu.edu/build.html go to page from edit function
# TODO: arena: Send kill signal to display on exit or crash?
# TODO: arena: add ability to catch all mousemoves, even w/o click-listener
# TODO: arena: move relative position lock into server js to...
# TODO: ...prevent latency follow lock outside click/reticle
# TODO: arena: enable data:source in callback for ClickEvent
# TODO: arena: Dead man switch timer ttl revealed when not
# TODO: arb: cleanup of scene method
# TODO: arb: Add args for broker and realm.
# TODO: arb: what is source of origin reset in XR?
# TODO: *arb: fix follow unlock position relative, not default
# TODO: arb: why is AR click sometimes hard to fire?
# TODO: arb: handle click-listener objects with 1.1 x scale shield?
# TODO: *arb: nudge-line unclickable in AR
# TODO: arb: models panel
# TODO: *arb: Scale all with three dof
# TODO: arb: Latency bottom corner camera control updates
# TODO: arb: gridlines on floor/ceiling, circles follow position
# TODO: arb: hud update of position
# TODO: arb: Show light sources
# TODO: arb: Is camera inside a shape?
# TODO: *arb: document theory/structure of builder
# TODO: *arb: add easy doc overlay for each button operation
# TODO: arb: keep local array of persist to prevent call updates each time?
# TODO: *arb: models in clipboard origin may be outside reticle
# TODO: *arb: dropdown rows should expand for options beyond eight perhaps


import arena
import argparse
import datetime
import enum
import json
import math
import os
import random
import urllib.request

BROKER = "oz.andrew.cmu.edu"
REALM = "realm"
SCENE = ""  # no default scene, arb works on any scene
CLICK_SND = "https://xr.andrew.cmu.edu/audio/click.ogg"
TOGGLE_SND = "https://xr.andrew.cmu.edu/audio/snd_StoneStone.ogg"

NUDGELINE_LEN = 10
NUDGE_LEN = 0.1
CLIP_RADIUS = 1.25
PANEL_RADIUS = 1
LOCK_XOFF = 0
LOCK_YOFF = 0.7
CLR_HUDTEXT = (200, 200, 200)
CLR_NUDGE = (255, 255, 0)
CLR_SELECT = (255, 255, 0)
CLR_ENABLED = (255, 255, 255)
CLR_DISABLED = (128, 128, 128)
SCL_GLTF = (0.5, 0.5, 0.5)

COLORS = ["ffffff", "ff0000", "ffa500", "ffff00", "00ff00",
          "0000ff", "4b0082", "800080", "a52a2a", "000000"]
SHAPES = [arena.Shape.sphere.value,
          arena.Shape.cube.value,
          arena.Shape.cone.value,
          arena.Shape.cylinder.value,
          arena.Shape.dodecahedron.value,
          arena.Shape.icosahedron.value,
          arena.Shape.octahedron.value,
          arena.Shape.tetrahedron.value,
          arena.Shape.torus.value,
          arena.Shape.torusKnot.value,
          arena.Shape.circle.value,
          arena.Shape.plane.value,
          arena.Shape.ring.value,
          arena.Shape.triangle.value,
          ]
MODELS = []
manifest = [{  # default model, if none loaded
    "name": "duck",
    "url_gltf": "models/Duck.glb",
}]

users = {}  # dictionary of user instances


class Mode(enum.Enum):
    NONE = "none"
    LOCK = "lock"
    PANIC = "panic"
    EDIT = "edit"
    MOVE = "move"
    NUDGE = "nudge"
    MODEL = "model"
    CREATE = "create"
    DELETE = "delete"
    COLOR = "color"
    SCALE = "scale"
    OCCLUDE = "occlude"
    ROTATE = "rotate"
    COLLAPSE = "collapse"


class User:
    def __init__(self, camname):
        self.camname = camname
        self.mode = Mode.NONE
        self.target_id = None
        self.target_style = ""
        self.locky = LOCK_YOFF
        self.lockx = LOCK_XOFF

        initOrigin()

        # set HUD to each user
        self.clipboard = set_clipboard(camname)
        self.clipboard.delete()  # workaround for non-empty object
        self.hudTextLeft = self.makeHudText(
            camname, "hudTextLeft", (-0.15, 0.15, -0.5), str(self.mode))
        self.hudTextRight = self.makeHudText(
            camname, "hudTextRight", (0.15, 0.15, -0.5), "")
        self.hudTextMouse = self.makeHudText(
            camname, "hudTextMouse", (0, -0.1, -0.5), "")

        # AR Control Panel
        self.follow_lock = False
        self.follow = arena.Object(
            objName=("follow_" + camname),
            objType=arena.Shape.cube,
            parent=camname,
            data=('{"material": {"transparent":true,"opacity":0}}'),
            location=(0, 0, -PANEL_RADIUS * 0.1),
            scale=(0.1, 0.1, 0.01),
        )
        self.panel = {}  # button dictionary
        followName = self.follow.objName
        self.dbuttons = []
        buttons = [
            Button(camname, Mode.LOCK, "lock", 0, 0,
                   parent=followName, callback=panel_callback, ),
            Button(camname, Mode.SCALE, "scale", 0, -1, parent=followName, callback=panel_callback,
                   enable=False),
            Button(camname, Mode.CREATE, "create", 1, 1,
                   parent=followName, callback=panel_callback),
            Button(camname, Mode.DELETE, "delete", 1, 0,
                   parent=followName, callback=panel_callback),
            Button(camname, Mode.MODEL, "model",  0, 1,
                   parent=followName, callback=panel_callback),
            Button(camname, Mode.MOVE, "move", -1, 0,
                   parent=followName, callback=panel_callback),
            Button(camname, Mode.NUDGE, "nudge",  -1, 1,
                   parent=followName, callback=panel_callback),
            Button(camname, Mode.COLOR, "color", 1, -1,
                   parent=followName, callback=panel_callback),
            Button(camname, Mode.OCCLUDE, "occlude", -1, -1, parent=followName, callback=panel_callback,
                   enable=False),
            Button(camname, Mode.ROTATE, "rotate", -2, 0, parent=followName, callback=panel_callback,
                   enable=False),
            Button(camname, Mode.EDIT, "edit", -2, -1, parent=followName, callback=panel_callback,
                   enable=False),
            Button(camname, Mode.COLLAPSE, "collapse", -2, 1, parent=followName, callback=panel_callback,
                   enable=False),
        ]
        for b in buttons:
            self.panel[b.button.objName] = b

        # panic button, to reset
        self.panic = Button(camname, Mode.PANIC, "Panic",
                            callback=panic_callback)

    def makeHudText(self, camname, label, location, text):
        return arena.Object(
            objName=(label + "_" + camname),
            objType=arena.Shape.text,
            parent=camname,
            data='{"text":"' + text + '"}',
            location=location,
            color=CLR_HUDTEXT,
            scale=(0.1, 0.1, 0.1),
        )

    def setTextLeft(self, mode):
        self.hudTextLeft.update(data='{"text":"' + str(mode) + '"}')

    def setTextRight(self, text, color=CLR_HUDTEXT):
        self.hudTextRight.update(data='{"text":"' + text + '"}', color=color)


class Button:
    def __init__(self, camname, mode, label, x=0, y=0, parent=None,
                 drop=None, color=CLR_ENABLED, enable=True, callback=None):
        if parent == None:
            parent = camname
            scale = (0.1, 0.1, 0.01)
        else:
            scale = (1, 1, 1)
        self.enabled = enable
        if enable:
            self.colorbut = color
            self.colortxt = CLR_ENABLED
        else:
            self.colorbut = CLR_DISABLED
            self.colortxt = CLR_DISABLED
        if len(label) > 8:  # easier to read
            self.label = label[:6] + "..."
        else:
            self.label = label
        self.mode = mode
        self.dropdown = drop
        self.on = False
        if drop is None:
            objName = "button_" + mode.value + "_" + camname
        else:
            objName = "button_" + mode.value + "_" + drop + "_" + camname
        self.button = arena.Object(  # cube is main button
            objName=objName,
            objType=arena.Shape.cube,
            parent=parent,
            data=('{"material":{"transparent":true,"shader":"flat","opacity":0.4}'
                  #',"sound": {"positional":true,"poolSize":8,"volume":0.1,'
                  #'"src":"' + CLICK_SND + '","on":"mousedown"}'
                  '}'),
            location=(x * 1.1, y * 1.1, -PANEL_RADIUS),
            scale=scale,
            color=self.colorbut,
            clickable=True,
            callback=callback,
        )
        self.text = arena.Object(  # text child of button
            objName=("text_" + self.button.objName),
            objType=arena.Shape.text,
            parent=self.button.objName,
            data='{"text":"' + self.label + '"}',
            location=(0, 0, -0.1),  # location inside to prevent ray events
            color=self.colortxt,
            scale=(1, 1, 1),
        )

    def setOn(self, on):
        self.on = on
        if on:
            self.button.update(color=CLR_SELECT)
        else:
            self.button.update(color=CLR_ENABLED)
            self.text.update(color=self.colortxt)

    def delete(self):
        # provide a delete method so that child text object also gets deleted
        self.text.delete()
        self.button.delete()


def initArgs():
    global args, SCENE, MODELS, manifest

    parser = argparse.ArgumentParser(description='ARENA AR Builder.')
    parser.add_argument('scene', type=str, help='ARENA scene name')
    parser.add_argument('-m', '--models', type=str, nargs=1,
                        help='JSON GLTF manifest')
    args = parser.parse_args()

    print(args)
    SCENE = args.scene

    if args.models is not None:
        f = open(args.models[0])
        data = json.load(f)
        MODELS = []
        for i in data['models']:
            print(i)
        f.close()
        manifest = data['models']

    for i in manifest:
        MODELS.append(i['name'])


def initOrigin():
    # origin object, construction cone
    c = [0.2, 0.4, 0.2]
    cone = arena.Object(  # 370mm x 370mm # 750mm
        objType=arena.Shape.cone, objName="arb-origin", data='{"material": {"transparent":true,"shader":"flat","opacity":0.8}}',
        color=(255, 114, 33),
        location=(0, c[1] / 2, 0),
        scale=(c[0] / 2, c[1], c[2] / 2))
    hole = arena.Object(
        objType=arena.Shape.cone, objName="arb-origin-hole",
        data='{"material":{"colorWrite":false},"render-order":"0"}',
        location=(0, c[1] - (c[1] / 2 / 15), 0),
        scale=(c[0] / 15, c[1] / 10, c[2] / 15))
    base = arena.Object(
        objType=arena.Shape.cube, objName="arb-origin-base",
        data='{"material": {"transparent":true,"shader":"flat","opacity":0.8}}',
        color=(0, 0, 0),
        location=(0, c[1] / 20, 0),
        scale=(c[0], c[1] / 10, c[2]))


def randcolor():
    x = random.randint(0, 255)
    y = random.randint(0, 255)
    z = random.randint(0, 255)
    return(x, y, z)


def set_clipboard(camname,
                  type=arena.Shape.sphere,
                  rotation=(0, 0, 0, 1),
                  scale=(0.05, 0.05, 0.05),
                  color=CLR_ENABLED,
                  url="",
                  ):
    return arena.Object(
        objName=("clipboard_" + camname),
        objType=type,
        color=color,
        location=(0, 0, -CLIP_RADIUS),
        rotation=rotation,
        parent=camname,
        scale=scale,
        data='{"material": {"transparent": true, "opacity": 0.3}}',
        url=url,
        clickable=True,
        callback=clipboard_callback,
    )


def modifyPersistedObj(object_id, msg, action="update", data=None):
    MESSAGE = {
        "object_id": object_id,
        "action": action,
    }
    if action == "update":
        MESSAGE["type"] = "object"
        MESSAGE["persist"] = "true"
        MESSAGE["data"] = data

    arena.arena_publish(REALM + "/s/" + SCENE + "/" + object_id, MESSAGE)
    print(msg + " " + object_id)


def colorObj(object_id, colorHex):
    data = {"material": {"color": "#" + colorHex}}
    modifyPersistedObj(object_id, "Recolored", data=data)


def scaleObj(object_id, scale):
    data = {
        "scale": {
            "x": scale[0],
            "y": scale[1],
            "z": scale[2],
        },
    }
    modifyPersistedObj(object_id, "Resized", data=data)


def moveObj(object_id, position):
    data = {
        "position": {
            "x": position[0],
            "y": position[1],
            "z": position[2],
        },
    }
    modifyPersistedObj(object_id, "Relocated", data=data)


def rotateObj(object_id, rotation):
    data = {
        "rotation": {
            "x": rotation[0],
            "y": rotation[1],
            "z": rotation[2],
            "w": rotation[3],
        },
    }
    modifyPersistedObj(object_id, "Rotated", data=data)


def deleteObj(object_id):
    modifyPersistedObj(object_id, "Deleted", action="delete")


def panel_callback(event=None):
    global users
    if event.event_type != arena.EventType.mousedown:
        return
    o = event.object_id.split("_")
    camname = event.source
    owner = o[2] + "_" + o[3] + "_" + o[4]  # callback owner in object_id
    print(camname+" "+owner)
    if owner != camname:
        return  # only owner may activate
    objId = event.object_id

    # ignore disabled
    if not users[camname].panel[objId].enabled:
        return

    mode = users[camname].panel[objId].mode
    if mode == users[camname].mode:
        # button click is same, then goes off and NONE
        users[camname].panel[objId].setOn(False)
        users[camname].mode = Mode.NONE
    else:
        # if button goes on, last button must go off
        prevObjId = "button_" + users[camname].mode.value + "_" + camname
        if prevObjId in users[camname].panel:
            users[camname].panel[prevObjId].setOn(False)
        users[camname].panel[objId].setOn(True)
        users[camname].mode = mode

    users[camname].setTextLeft(users[camname].mode)
    users[camname].setTextRight("")
    users[camname].target_id = None
    users[camname].clipboard.delete()

    # always clear last dropdown
    for b in users[camname].dbuttons:
        b.delete()
    users[camname].dbuttons.clear()

    # make/unmake camera tracking objects
    if mode == Mode.CREATE:
        updateDropDown(camname, objId, mode, SHAPES, 2, shapes_callback)
        users[camname].clipboard = set_clipboard(
            camname, type=arena.Shape(users[camname].target_style))
    elif mode == Mode.MODEL:
        updateDropDown(camname, objId, mode, MODELS, 2, models_callback)
        idx = MODELS.index(users[camname].target_style)
        url = manifest[idx]['url_gltf']
        users[camname].clipboard = set_clipboard(
            camname, type=arena.Shape.gltf_model, scale=SCL_GLTF,
            url=url)
    elif mode == Mode.COLOR:
        updateDropDown(camname, objId, mode, COLORS, -2, colors_callback)
    elif mode == Mode.LOCK:
        users[camname].follow_lock = not users[camname].follow_lock
        users[camname].panel[objId].setOn(users[camname].follow_lock)
        # TODO: after lock ensure original ray keeps lock button in reticle


def updateDropDown(camname, objId, mode, options, row, callback):
    global users
    # show new dropdown
    if users[camname].panel[objId].on:
        followName = users[camname].follow.objName
        dropBtnOffset = -math.floor(len(options) / 2)
        for i in range(len(options)):
            if mode is Mode.COLOR:
                bcolor = tuple(int(options[i][c:c + 2], 16) for c in (0, 2, 4))
            else:
                bcolor = CLR_SELECT
            dbutton = Button(camname, mode,
                             options[i], i + dropBtnOffset, row,
                             parent=followName, color=bcolor,
                             drop=options[i], callback=callback)
            users[camname].dbuttons.append(dbutton)
        # make default selection
        if mode is Mode.COLOR:
            rcolor = tuple(int(options[0][c:c + 2], 16) for c in (0, 2, 4))
        else:
            rcolor = CLR_HUDTEXT
        users[camname].setTextRight(options[0], color=rcolor)
        users[camname].target_style = options[0]


def models_callback(event=None):
    global users
    if event.event_type != arena.EventType.mousedown:
        return
    o = event.object_id.split("_")
    camname = event.source
    owner = o[3] + "_" + o[4] + "_" + o[5]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    model = o[2]
    idx = MODELS.index(model)
    url = manifest[idx]['url_gltf']
    users[camname].clipboard = set_clipboard(
        camname, type=arena.Shape.gltf_model, scale=SCL_GLTF,
        url=url)
    users[camname].setTextRight(model)
    users[camname].target_style = model


def shapes_callback(event=None):
    global users
    if event.event_type != arena.EventType.mousedown:
        return
    o = event.object_id.split("_")
    camname = event.source
    owner = o[3] + "_" + o[4] + "_" + o[5]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    shape = o[2]
    users[camname].clipboard = set_clipboard(camname, type=arena.Shape(shape))
    users[camname].setTextRight(shape)
    users[camname].target_style = shape


def colors_callback(event=None):
    global users
    if event.event_type != arena.EventType.mousedown:
        return
    o = event.object_id.split("_")
    camname = event.source
    owner = o[3] + "_" + o[4] + "_" + o[5]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    hcolor = o[2]
    color = tuple(int(hcolor[c:c + 2], 16) for c in (0, 2, 4))
    users[camname].setTextRight(hcolor, color=color)
    users[camname].target_style = hcolor


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
    hcolor = prop[0]["attributes"]["color"].lstrip('#')
    color = tuple(int(hcolor[c:c + 2], 16) for c in (0, 2, 4))
    users[camname].clipboard = set_clipboard(
        camname,
        type=arena.Shape(prop[0]["attributes"]["object_type"]),
        rotation=rotation,
        scale=scale,
        color=color,
        # TODO: url=prop[0]["attributes"]["url"],
    )


def doNudgeSelect(camname, object_id):
    global users
    prop = getNetworkPersistedObject(object_id)
    users[camname].target_id = object_id
    # generate child 6dof non-persist, clickable lines
    makeNudgeLine("x", NUDGELINE_LEN, object_id)
    makeNudgeLine("x", -NUDGELINE_LEN, object_id)
    makeNudgeLine("y", NUDGELINE_LEN, object_id)
    makeNudgeLine("y", -NUDGELINE_LEN, object_id)
    makeNudgeLine("z", NUDGELINE_LEN, object_id)
    makeNudgeLine("z", -NUDGELINE_LEN, object_id)


def makeNudgeLine(deg, linelen, object_id):
    ex = 0
    ey = 0
    ez = 0
    dir = "p"
    if (linelen < 0):
        dir = "n"
    if (deg == "x"):
        ex = linelen
    elif (deg == "y"):
        ey = linelen
    elif (deg == "z"):
        ez = linelen
    nline = arena.Object(
        objType=arena.Shape.line,
        objName=(object_id + "_nudge_" + deg + dir),
        parent=object_id,
        data=('{"start": {"x":0,"y":0,"z":0}, ' +
              '"end": {"x":' + str(ex) + ',"y":' + str(ey) + ',"z":' + str(ez) + '}}'),
        color=CLR_NUDGE,
        clickable=True,
        ttl=30,
        callback=nudge_callback,
    )
    handle = arena.Object(  # TODO: temp object that is clickable in AR?
        objType=arena.Shape.sphere,
        objName=(nline.objName + "_handle"),
        parent=object_id,
        location=(ex, ey, ez),
        scale=(0.5, 0.5, 0.5),
        color=nline.color,
        clickable=True,
        ttl=30,
        callback=nudge_callback,
    )


def doMoveRelocate(camname, newlocation):
    global users
    moveObj(users[camname].target_id, newlocation)
    users[camname].clipboard.delete()
    users[camname].target_id = None


def nudge_p(n):
    if ((n % NUDGE_LEN) > NUDGE_LEN):
        r = math.ceil(n / NUDGE_LEN) * NUDGE_LEN
    else:
        r = n + NUDGE_LEN
    return float(format(r, '.1f'))


def nudge_n(n):
    if ((n % NUDGE_LEN) > NUDGE_LEN):
        r = math.floor(n / NUDGE_LEN) * NUDGE_LEN
    else:
        r = n - NUDGE_LEN
    return float(format(r, '.1f'))


def nudge_callback(event=None):
    global users
    if event.event_type != arena.EventType.mousedown:
        return
    # allow any user to nudge an object
    nudge_id = event.object_id.split("_nudge_")
    object_id = nudge_id[0]
    dir = (nudge_id[1])[:2]
    prop = getNetworkPersistedObject(object_id)
    loc = (prop[0]["attributes"]["position"]["x"],
           prop[0]["attributes"]["position"]["y"],
           prop[0]["attributes"]["position"]["z"])
    nudged = loc
    if (dir == "xp"):
        nudged = (nudge_p(loc[0]), loc[1], loc[2])
    elif (dir == "xn"):
        nudged = (nudge_n(loc[0]), loc[1], loc[2])
    elif (dir == "yp"):
        nudged = (loc[0], nudge_p(loc[1]), loc[2])
    elif (dir == "yn"):
        nudged = (loc[0], nudge_n(loc[1]), loc[2])
    elif (dir == "zp"):
        nudged = (loc[0], loc[1], nudge_p(loc[2]))
    elif (dir == "zn"):
        nudged = (loc[0], loc[1], nudge_n(loc[2]))
    print(str(loc) + " to " + str(nudged))
    moveObj(object_id, nudged)


def createObj(clipboard, location):
    randstr = str(random.randrange(0, 1000000))
    # make a copy of static object in place
    newObj = arena.Object(
        persist=True,
        objName=clipboard.objType.name + "_" + randstr,
        objType=clipboard.objType,
        location=location,
        rotation=clipboard.rotation,
        scale=clipboard.scale,
        color=clipboard.color,
        data='{"material": {"transparent": false}}',
        url=clipboard.url,
        clickable=True)
    print("Created " + newObj.objName)


def clipboard_callback(event=None):
    global users
    if event.event_type != arena.EventType.mousedown:
        return
    o = event.object_id.split("_")
    camname = event.source
    owner = o[1] + "_" + o[2] + "_" + o[3]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    location = event.position
    # clicked self HUD clipboard
    if users[camname].mode == Mode.CREATE or users[camname].mode == Mode.MODEL:
        createObj(users[camname].clipboard, location)
    elif users[camname].mode == Mode.MOVE:
        doMoveRelocate(camname, location)


def panic_callback(event=None):
    global users
    if event.event_type != arena.EventType.mousedown:
        return
    o = event.object_id.split("_")
    camname = event.source
    owner = o[2] + "_" + o[3] + "_" + o[4]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    # control panel panic button
    users[camname].locky = LOCK_YOFF
    users[camname].lockx = LOCK_XOFF
    users[camname].follow_lock = False


def scene_callback(msg):
    # This is the MQTT message callback function for the scene
    global users

    jsonMsg = json.loads(msg)
    # print(msg)

    if jsonMsg["action"] == "create" and jsonMsg["data"]["object_type"] == "camera":
        # camera updates define users present
        camname = jsonMsg["object_id"]
        if camname not in users:
            users[camname] = User(camname)

        rx = jsonMsg["data"]["rotation"]["x"]
        ry = jsonMsg["data"]["rotation"]["y"]
        # print ("rx " + str(rx) + " ry " + str(ry) +
        #       " | ory " + str(users[camname].locky))

        # floating panic button
        l = users[camname].panic.button.location
        tx = -(rx + 0.7) / 0.7 * math.pi / 2
        px = l[0]
        py = PANEL_RADIUS * math.sin(tx)
        pz = PANEL_RADIUS * -math.cos(tx)
        users[camname].panic.button.position(location=(px, py, pz))
        # floating controller
        if not users[camname].follow_lock:
            l = users[camname].follow.location
            ty = -(ry + users[camname].locky) / 0.7 * math.pi / 2
            tx = -(rx + users[camname].lockx) / 0.7 * math.pi / 2
            px = PANEL_RADIUS * -math.cos(ty)
            py = PANEL_RADIUS * math.sin(tx)
            pz = PANEL_RADIUS * math.sin(ty)
            users[camname].follow.position(location=(px, py, pz))
        # else: # TODO: panel lock location drop is inaccurate
            #users[camname].lockx = rx + LOCK_XOFF
            #users[camname].locky = -(ry * math.pi) - LOCK_YOFF

    # mouse event
    elif jsonMsg["action"] == "clientEvent":
        # camera updates define users present
        camname = jsonMsg["data"]["source"]
        if camname not in users:
            users[camname] = User(camname)

        # show objects with events
        if jsonMsg["type"] == "mouseenter":
            users[camname].hudTextMouse.update(
                data='{"text":"' + jsonMsg["object_id"] + '"}')
        elif jsonMsg["type"] == "mouseleave":
            users[camname].hudTextMouse.update(data='{"text":"' + "" + '"}')

        # handle click
        elif jsonMsg["type"] == "mousedown":
            objId = jsonMsg["object_id"]

            # clicked on persisted object to modify
            if len(objId) > 0:
                if users[camname].mode == Mode.DELETE:
                    deleteObj(objId)
                elif users[camname].mode == Mode.MOVE:
                    doMoveSelect(camname, objId)
                elif users[camname].mode == Mode.NUDGE:
                    doNudgeSelect(camname, objId)
                elif users[camname].mode == Mode.COLOR:
                    colorObj(objId, users[camname].target_style)


def getNetworkPersistedObject(object_id):
    data = urllib.request.urlopen(
        'https://' + BROKER + '/persist/' + SCENE + '/' + object_id).read()
    output = json.loads(data)
    return output


initArgs()
random.seed()

arena.init(BROKER, REALM, SCENE, scene_callback)
arena.handle_events()
