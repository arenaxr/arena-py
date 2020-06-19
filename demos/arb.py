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

# pylint: disable=missing-docstring
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


import argparse
import enum
import json
import math
import random
import urllib.request

import arena

BROKER = "oz.andrew.cmu.edu"
REALM = "realm"
SCENE = ""  # no default scene, arb works on any scene

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
          arena.Shape.triangle.value]
MODELS = []
MANIFEST = [{  # default model, if none loaded
    "name": "duck",
    "url_gltf": "models/Duck.glb",
}]

USERS = {}  # dictionary of user instances


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

        init_origin()

        # set HUD to each user
        self.clipboard = set_clipboard(camname)
        self.clipboard.delete()  # workaround for non-empty object
        self.hudtext_left = self.make_hudtext(
            camname, "hudTextLeft", (-0.15, 0.15, -0.5), str(self.mode))
        self.hudtext_right = self.make_hudtext(
            camname, "hudTextRight", (0.15, 0.15, -0.5), "")
        self.hudtext_mouse = self.make_hudtext(
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
        followname = self.follow.objName
        self.dbuttons = []
        buttons = [
            [Mode.LOCK, "lock", 0, 0, True],
            [Mode.SCALE, "scale", 0, -1, False],
            [Mode.CREATE, "create", 1, 1, True],
            [Mode.DELETE, "delete", 1, 0, True],
            [Mode.MODEL, "model", 0, 1, True],
            [Mode.MOVE, "move", -1, 0, True],
            [Mode.NUDGE, "nudge", -1, 1, True],
            [Mode.COLOR, "color", 1, -1, True],
            [Mode.OCCLUDE, "occlude", -1, -1, False],
            [Mode.ROTATE, "rotate", -2, 0, False],
            [Mode.EDIT, "edit", -2, -1, False],
            [Mode.COLLAPSE, "collapse", -2, 1, False],
        ]
        for but in buttons:
            pbutton = Button(camname, but[0], but[1], but[2], but[3], enable=but[4],
                             parent=followname, callback=panel_callback)
            self.panel[pbutton.button.objName] = pbutton

        # panic button, to reset
        self.panic = Button(camname, Mode.PANIC, "Panic",
                            callback=panic_callback)

    def make_hudtext(self, camname, label, location, text):
        return arena.Object(
            objName=(label + "_" + camname),
            objType=arena.Shape.text,
            parent=camname,
            data='{"text":"' + text + '"}',
            location=location,
            color=CLR_HUDTEXT,
            scale=(0.1, 0.1, 0.1),
        )

    def set_textleft(self, mode):
        self.hudtext_left.update(data='{"text":"' + str(mode) + '"}')

    def set_textright(self, text, color=CLR_HUDTEXT):
        self.hudtext_right.update(data='{"text":"' + text + '"}', color=color)


class Button:
    def __init__(self, camname, mode, label, x=0, y=0, parent=None,
                 drop=None, color=CLR_ENABLED, enable=True, callback=None):
        if parent is None:
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
            obj_name = "button_" + mode.value + "_" + camname
        else:
            obj_name = "button_" + mode.value + "_" + drop + "_" + camname
        self.button = arena.Object(  # cube is main button
            objName=obj_name,
            objType=arena.Shape.cube,
            parent=parent,
            data=('{"material":{"transparent":true,"shader":"flat","opacity":0.4}}'),
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

    def set_on(self, on):
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


def init_args():
    global SCENE, MODELS, MANIFEST

    parser = argparse.ArgumentParser(description='ARENA AR Builder.')
    parser.add_argument('scene', type=str, help='ARENA scene name')
    parser.add_argument('-m', '--models', type=str, nargs=1,
                        help='JSON GLTF manifest')
    args = parser.parse_args()

    print(args)
    SCENE = args.scene

    if args.models is not None:
        mfile = open(args.models[0])
        data = json.load(mfile)
        MODELS = []
        for i in data['models']:
            print(i)
        mfile.close()
        MANIFEST = data['models']

    for i in MANIFEST:
        MODELS.append(i['name'])


def init_origin():
    # origin object, construction cone
    size = [0.2, 0.4, 0.2]
    arena.Object(  # 370mm x 370mm # 750mm
        objType=arena.Shape.cone, objName="arb-origin",
        data='{"material": {"transparent":true,"shader":"flat","opacity":0.8}}',
        color=(255, 114, 33),
        location=(0, size[1] / 2, 0),
        scale=(size[0] / 2, size[1], size[2] / 2))
    arena.Object(
        objType=arena.Shape.cone, objName="arb-origin-hole",
        data='{"material":{"colorWrite":false},"render-order":"0"}',
        location=(0, size[1] - (size[1] / 2 / 15), 0),
        scale=(size[0] / 15, size[1] / 10, size[2] / 15))
    arena.Object(
        objType=arena.Shape.cube, objName="arb-origin-base",
        data='{"material": {"transparent":true,"shader":"flat","opacity":0.8}}',
        color=(0, 0, 0),
        location=(0, size[1] / 20, 0),
        scale=(size[0], size[1] / 10, size[2]))


def set_clipboard(camname,
                  obj_type=arena.Shape.sphere,
                  rotation=(0, 0, 0, 1),
                  scale=(0.05, 0.05, 0.05),
                  color=CLR_ENABLED,
                  url=""):
    return arena.Object(
        objName=("clipboard_" + camname),
        objType=obj_type,
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


def update_persisted_obj(object_id, label, action="update", data=None):
    msg = {
        "object_id": object_id,
        "action": action,
    }
    if action == "update":
        msg["type"] = "object"
        msg["persist"] = "true"
        msg["data"] = data

    arena.arena_publish(REALM + "/s/" + SCENE + "/" + object_id, msg)
    print(label + " " + object_id)


def color_obj(object_id, hcolor):
    data = {"material": {"color": "#" + hcolor}}
    update_persisted_obj(object_id, "Recolored", data=data)


def scale_obj(object_id, scale):
    data = {
        "scale": {
            "x": scale[0],
            "y": scale[1],
            "z": scale[2],
        },
    }
    update_persisted_obj(object_id, "Resized", data=data)


def move_obj(object_id, position):
    data = {
        "position": {
            "x": position[0],
            "y": position[1],
            "z": position[2],
        },
    }
    update_persisted_obj(object_id, "Relocated", data=data)


def rotate_obj(object_id, rotation):
    data = {
        "rotation": {
            "x": rotation[0],
            "y": rotation[1],
            "z": rotation[2],
            "w": rotation[3],
        },
    }
    update_persisted_obj(object_id, "Rotated", data=data)


def delete_obj(object_id):
    update_persisted_obj(object_id, "Deleted", action="delete")


def panel_callback(event=None):
    global USERS
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[2] + "_" + obj[3] + "_" + obj[4]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    objid = event.object_id

    # ignore disabled
    if not USERS[camname].panel[objid].enabled:
        return

    mode = USERS[camname].panel[objid].mode
    if mode == USERS[camname].mode:
        # button click is same, then goes off and NONE
        USERS[camname].panel[objid].set_on(False)
        USERS[camname].mode = Mode.NONE
    else:
        # if button goes on, last button must go off
        prev_objid = "button_" + USERS[camname].mode.value + "_" + camname
        if prev_objid in USERS[camname].panel:
            USERS[camname].panel[prev_objid].set_on(False)
        USERS[camname].panel[objid].set_on(True)
        USERS[camname].mode = mode

    USERS[camname].set_textleft(USERS[camname].mode)
    USERS[camname].set_textright("")
    USERS[camname].target_id = None
    USERS[camname].clipboard.delete()

    # always clear last dropdown
    for but in USERS[camname].dbuttons:
        but.delete()
    USERS[camname].dbuttons.clear()

    # make/unmake camera tracking objects
    if mode == Mode.CREATE:
        update_dropdown(camname, objid, mode, SHAPES, 2, shapes_callback)
        USERS[camname].clipboard = set_clipboard(
            camname, obj_type=arena.Shape(USERS[camname].target_style))
    elif mode == Mode.MODEL:
        update_dropdown(camname, objid, mode, MODELS, 2, models_callback)
        idx = MODELS.index(USERS[camname].target_style)
        url = MANIFEST[idx]['url_gltf']
        USERS[camname].clipboard = set_clipboard(
            camname, obj_type=arena.Shape.gltf_model, scale=SCL_GLTF,
            url=url)
    elif mode == Mode.COLOR:
        update_dropdown(camname, objid, mode, COLORS, -2, colors_callback)
    elif mode == Mode.LOCK:
        USERS[camname].follow_lock = not USERS[camname].follow_lock
        USERS[camname].panel[objid].set_on(USERS[camname].follow_lock)
        # TODO: after lock ensure original ray keeps lock button in reticle


def update_dropdown(camname, objid, mode, options, row, callback):
    global USERS
    # show new dropdown
    if USERS[camname].panel[objid].on:
        followname = USERS[camname].follow.objName
        drop_button_offset = -math.floor(len(options) / 2)
        for i, option in enumerate(options):
            if mode is Mode.COLOR:
                bcolor = tuple(int(option[c:c + 2], 16) for c in (0, 2, 4))
            else:
                bcolor = CLR_SELECT
            dbutton = Button(camname, mode,
                             option, i + drop_button_offset, row,
                             parent=followname, color=bcolor,
                             drop=option, callback=callback)
            USERS[camname].dbuttons.append(dbutton)
        # make default selection
        if mode is Mode.COLOR:
            rcolor = tuple(int(options[0][c:c + 2], 16) for c in (0, 2, 4))
        else:
            rcolor = CLR_HUDTEXT
        USERS[camname].set_textright(options[0], color=rcolor)
        USERS[camname].target_style = options[0]


def models_callback(event=None):
    global USERS
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[3] + "_" + obj[4] + "_" + obj[5]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    model = obj[2]
    idx = MODELS.index(model)
    url = MANIFEST[idx]['url_gltf']
    USERS[camname].clipboard = set_clipboard(
        camname, obj_type=arena.Shape.gltf_model, scale=SCL_GLTF,
        url=url)
    USERS[camname].set_textright(model)
    USERS[camname].target_style = model


def shapes_callback(event=None):
    global USERS
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[3] + "_" + obj[4] + "_" + obj[5]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    shape = obj[2]
    USERS[camname].clipboard = set_clipboard(
        camname, obj_type=arena.Shape(shape))
    USERS[camname].set_textright(shape)
    USERS[camname].target_style = shape


def colors_callback(event=None):
    global USERS
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[3] + "_" + obj[4] + "_" + obj[5]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    hcolor = obj[2]
    color = tuple(int(hcolor[c:c + 2], 16) for c in (0, 2, 4))
    USERS[camname].set_textright(hcolor, color=color)
    USERS[camname].target_style = hcolor


def do_move_select(camname, object_id):
    global USERS
    prop = get_network_persisted_obj(object_id)
    USERS[camname].target_id = object_id
    rotation = (prop[0]["attributes"]["rotation"]["x"],
                prop[0]["attributes"]["rotation"]["y"],
                prop[0]["attributes"]["rotation"]["z"],
                prop[0]["attributes"]["rotation"]["w"])
    scale = (prop[0]["attributes"]["scale"]["x"],
             prop[0]["attributes"]["scale"]["y"],
             prop[0]["attributes"]["scale"]["z"])
    hcolor = prop[0]["attributes"]["color"].lstrip('#')
    color = tuple(int(hcolor[c:c + 2], 16) for c in (0, 2, 4))
    USERS[camname].clipboard = set_clipboard(
        camname,
        obj_type=arena.Shape(prop[0]["attributes"]["object_type"]),
        rotation=rotation,
        scale=scale,
        color=color,
        # TODO: url=prop[0]["attributes"]["url"],
    )


def do_nudge_select(camname, object_id):
    global USERS
    USERS[camname].target_id = object_id
    # generate child 6dof non-persist, clickable lines
    make_nudgeline("x", NUDGELINE_LEN, object_id)
    make_nudgeline("x", -NUDGELINE_LEN, object_id)
    make_nudgeline("y", NUDGELINE_LEN, object_id)
    make_nudgeline("y", -NUDGELINE_LEN, object_id)
    make_nudgeline("z", NUDGELINE_LEN, object_id)
    make_nudgeline("z", -NUDGELINE_LEN, object_id)


def make_nudgeline(deg, linelen, object_id):
    endx = endy = endz = 0
    direction = "p"
    if linelen < 0:
        direction = "n"
    if deg == "x":
        endx = linelen
    elif deg == "y":
        endy = linelen
    elif deg == "z":
        endz = linelen
    arena.Object(
        objType=arena.Shape.line,
        objName=(object_id + "_nudge_" + deg + direction),
        parent=object_id,
        data=('{"start": {"x":0,"y":0,"z":0}, ' + '"end": {"x":' +
              str(endx) + ',"y":' + str(endy) + ',"z":' + str(endz) + '}}'),
        color=CLR_NUDGE,
        clickable=True,
        ttl=30,
        callback=nudge_callback,
    )


def do_move_relocate(camname, newlocation):
    global USERS
    move_obj(USERS[camname].target_id, newlocation)
    USERS[camname].clipboard.delete()
    USERS[camname].target_id = None


def nudge_p(coord):
    if (coord % NUDGE_LEN) > NUDGE_LEN:
        res = math.ceil(coord / NUDGE_LEN) * NUDGE_LEN
    else:
        res = coord + NUDGE_LEN
    return float(format(res, '.1f'))


def nudge_n(coord):
    if (coord % NUDGE_LEN) > NUDGE_LEN:
        res = math.floor(coord / NUDGE_LEN) * NUDGE_LEN
    else:
        res = coord - NUDGE_LEN
    return float(format(res, '.1f'))


def nudge_callback(event=None):
    print(event.object_id + "  " + str(event.event_action) +
          "  " + str(event.event_type))
    global USERS
    if event.event_type != arena.EventType.mousedown:
        return
    # allow any user to nudge an object
    nudge_id = event.object_id.split("_nudge_")
    object_id = nudge_id[0]
    direction = (nudge_id[1])[:2]
    prop = get_network_persisted_obj(object_id)
    loc = (prop[0]["attributes"]["position"]["x"],
           prop[0]["attributes"]["position"]["y"],
           prop[0]["attributes"]["position"]["z"])
    nudged = loc
    if direction == "xp":
        nudged = (nudge_p(loc[0]), loc[1], loc[2])
    elif direction == "xn":
        nudged = (nudge_n(loc[0]), loc[1], loc[2])
    elif direction == "yp":
        nudged = (loc[0], nudge_p(loc[1]), loc[2])
    elif direction == "yn":
        nudged = (loc[0], nudge_n(loc[1]), loc[2])
    elif direction == "zp":
        nudged = (loc[0], loc[1], nudge_p(loc[2]))
    elif direction == "zn":
        nudged = (loc[0], loc[1], nudge_n(loc[2]))
    print(str(loc) + " to " + str(nudged))
    move_obj(object_id, nudged)


def create_obj(clipboard, location):
    randstr = str(random.randrange(0, 1000000))
    # make a copy of static object in place
    new_obj = arena.Object(
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
    print("Created " + new_obj.objName)


def clipboard_callback(event=None):
    global USERS
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[1] + "_" + obj[2] + "_" + obj[3]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    location = event.position
    # clicked self HUD clipboard
    if USERS[camname].mode == Mode.CREATE or USERS[camname].mode == Mode.MODEL:
        create_obj(USERS[camname].clipboard, location)
    elif USERS[camname].mode == Mode.MOVE:
        do_move_relocate(camname, location)


def panic_callback(event=None):
    global USERS
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[2] + "_" + obj[3] + "_" + obj[4]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    # control panel panic button
    USERS[camname].locky = LOCK_YOFF
    USERS[camname].lockx = LOCK_XOFF
    USERS[camname].follow_lock = False


def scene_callback(msg):
    # This is the MQTT message callback function for the scene
    global USERS

    json_msg = json.loads(msg)
    # print(msg)

    if json_msg["action"] == "create" and json_msg["data"]["object_type"] == "camera":
        # camera updates define users present
        camname = json_msg["object_id"]
        if camname not in USERS:
            USERS[camname] = User(camname)

        rx = json_msg["data"]["rotation"]["x"]
        ry = json_msg["data"]["rotation"]["y"]
        # print ("rx " + str(rx) + " ry " + str(ry) +
        #       " | ory " + str(users[camname].locky))

        # floating panic button
        l = USERS[camname].panic.button.location
        tx = -(rx + 0.7) / 0.7 * math.pi / 2
        px = l[0]
        py = PANEL_RADIUS * math.sin(tx)
        pz = PANEL_RADIUS * -math.cos(tx)
        USERS[camname].panic.button.position(location=(px, py, pz))
        # floating controller
        if not USERS[camname].follow_lock:
            l = USERS[camname].follow.location
            ty = -(ry + USERS[camname].locky) / 0.7 * math.pi / 2
            tx = -(rx + USERS[camname].lockx) / 0.7 * math.pi / 2
            px = PANEL_RADIUS * -math.cos(ty)
            py = PANEL_RADIUS * math.sin(tx)
            pz = PANEL_RADIUS * math.sin(ty)
            USERS[camname].follow.position(location=(px, py, pz))
        # else: # TODO: panel lock location drop is inaccurate
            #users[camname].lockx = rx + LOCK_XOFF
            #users[camname].locky = -(ry * math.pi) - LOCK_YOFF

    # mouse event
    elif json_msg["action"] == "clientEvent":
        print(json_msg["object_id"] + "  " +
              json_msg["action"] + "  " + json_msg["type"])
        # camera updates define users present
        camname = json_msg["data"]["source"]
        if camname not in USERS:
            USERS[camname] = User(camname)

        # show objects with events
        if json_msg["type"] == "mouseenter":
            USERS[camname].hudtext_mouse.update(
                data='{"text":"' + json_msg["object_id"] + '"}')
        elif json_msg["type"] == "mouseleave":
            USERS[camname].hudtext_mouse.update(data='{"text":"' + "" + '"}')

        # handle click
        elif json_msg["type"] == "mousedown":
            objid = json_msg["object_id"]

            # clicked on persisted object to modify
            if USERS[camname].mode == Mode.DELETE:
                delete_obj(objid)
            elif USERS[camname].mode == Mode.MOVE:
                do_move_select(camname, objid)
            elif USERS[camname].mode == Mode.NUDGE:
                do_nudge_select(camname, objid)
            elif USERS[camname].mode == Mode.COLOR:
                color_obj(objid, USERS[camname].target_style)


def get_network_persisted_obj(object_id):
    data = urllib.request.urlopen(
        'https://' + BROKER + '/persist/' + SCENE + '/' + object_id).read()
    output = json.loads(data)
    return output


init_args()
random.seed()

arena.init(BROKER, REALM, SCENE, scene_callback)
arena.handle_events()
