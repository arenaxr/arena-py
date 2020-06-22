# arb.py
#
# AR Builder
# Pass in args for scene name and/or broker and realm.

# future:
#    worklight on/off
#    rotate
#    level meter 3dof
#    rotate controls to camera
#    subscribe to all mouseenter/leave
#    highlight mouseenter to avoid click

# pylint: disable=fixme
# pylint: disable=missing-docstring
# TODO: arena: https://xr.andrew.cmu.edu/go/ interface to add AR builder
# TODO: arena: https://xr.andrew.cmu.edu/build.html go to page from edit function
# TODO: arena: Send kill signal to display on exit or crash?
# TODO: arena: add ability to catch all mousemoves, even w/o click-listener
# TODO: arena: move relative position lock into server js to...
# TODO: ...prevent latency follow lock outside click/reticle
# TODO: arena: enable data:source in callback for ClickEvent
# TODO: arena: Dead man switch timer ttl revealed when not
# TODO: arena: Show light sources
# TODO: arena: what is source of origin reset in XR?
# TODO: arena: why is AR click sometimes hard to fire?
# TODO: arena: nudge-line unclickable in AR
# TODO: arb: cleanup of scene method
# TODO: arb: Add args for broker and realm.
# TODO: *arb: fix follow unlock position relative, not default
# TODO: arb: handle click-listener objects with 1.1 x scale shield?
# TODO: arb: Latency bottom corner camera control updates
# TODO: arb: Is camera inside a shape?
# TODO: *arb: document theory/structure of builder
# TODO: *arb: add easy doc overlay for each button operation
# TODO: *arb: models in clipboard origin may be outside reticle

import argparse
import enum
import json
import math
import random
import urllib.request
import string

import arena

BROKER = "oz.andrew.cmu.edu"
REALM = "realm"
SCENE = ""  # no default scene, arb works on any scene

CLICKLINE_LEN = 1
CLICKLINE_SCL = (1, 1, 1)
FLOOR_Y = 0.01
GRIDLEN = 20
NUDGE_INCR = 0.1
SCALE_INCR = 0.1
WALL_WIDTH = 0.2
CLIP_RADIUS = 1.25
PANEL_RADIUS = 1
LOCK_XOFF = 0
LOCK_YOFF = 0.7
TTL_TEMP = 30
CLR_HUDTEXT = (200, 200, 200)
CLR_NUDGE = (255, 255, 0)
CLR_SCALE = (0, 0, 255)
CLR_SELECT = (255, 255, 0)
CLR_ENABLED = (255, 255, 255)
CLR_DISABLED = (128, 128, 128)
SCL_GLTF = (0.5, 0.5, 0.5)


def get_keys():
    keys = []
    keys.extend(list(string.digits))
    keys.extend(list(string.ascii_lowercase))
    keys.append('back')
    return keys


KEYS = get_keys()
BOOLS = ["on", "off"]
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
    RENAME = "rename"
    MOVE = "move"
    NUDGE = "nudge"
    MODEL = "model"
    CREATE = "create"
    DELETE = "delete"
    COLOR = "color"
    SCALE = "scale"
    OCCLUDE = "occlude"
    ROTATE = "rotate"
    REDPILL = "redpill"
    WALL = "wall"


class User:
    def __init__(self, camname):
        self.camname = camname
        self.mode = Mode.NONE
        self.target_id = self.location = None
        self.target_style = self.typetext = ""
        self.locky = LOCK_YOFF
        self.lockx = LOCK_XOFF
        self.wall_start = self.wall_end = None
        init_origin()

        # set HUD to each user
        self.clipboard = set_clipboard(camname)
        self.clipboard.delete()  # workaround for non-empty object
        self.hudtext_left = self.make_hudtext(
            camname, "hudTextLeft", (-0.15, 0.15, -0.5), str(self.mode))
        self.hudtext_right = self.make_hudtext(
            camname, "hudTextRight", (0.15, 0.15, -0.5), "")
        self.hudtext_status = self.make_hudtext(
            camname, "hudTextStatus", (0, -0.15, -0.5), "")

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
            [Mode.SCALE, "scale", 2, 1, True],
            [Mode.CREATE, "create", 1, 1, True],
            [Mode.DELETE, "delete", 1, 0, True],
            [Mode.MODEL, "model", 0, 1, True],
            [Mode.MOVE, "move", -1, 0, True],
            [Mode.NUDGE, "nudge", -1, 1, True],
            [Mode.COLOR, "color", 1, -1, True],
            [Mode.OCCLUDE, "occlude", -1, -1, True],
            [Mode.ROTATE, "rotate", -2, 0, False],
            [Mode.RENAME, "rename", 0, -1, True],
            [Mode.REDPILL, "redpill", -2, 1, True],
            [Mode.WALL, "wall", 2, 0, False],
        ]
        for but in buttons:
            pbutton = Button(camname, but[0], but[1], but[2], but[3], enable=but[4],
                             parent=followname, callback=panel_callback)
            self.panel[pbutton.button.objName] = pbutton

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

    def set_textstatus(self, text):
        self.hudtext_status.update(data='{"text":"' + text + '"}')


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


class ObjectPersistence:
    """Converts persistence database object into python without using MQTT.
    """
    object_id = ""
    object_Type = arena.Shape.cube
    position = (0, 0, 0)
    rotation = (0, 0, 0, 1)
    scale = (1, 1, 1)
    color = (255, 255, 255)
    ttl = 0
    parent = ""
    persist = False
    physics = arena.Physics.none
    clickable = False
    url = ""
    transparent_occlude = False
    line = None
    thickline = None
    collision_listener = False
    transparency = None
    impulse = None
    animation = None
    data = ""

    def __init__(self, jData):
        self.object_id = jData["object_id"]
        self.persist = True  # by nature
        self.object_type = arena.Shape(jData["attributes"]["object_type"])
        self.position = (jData["attributes"]["position"]["x"],
                         jData["attributes"]["position"]["y"],
                         jData["attributes"]["position"]["z"])
        self.rotation = (jData["attributes"]["rotation"]["x"],
                         jData["attributes"]["rotation"]["y"],
                         jData["attributes"]["rotation"]["z"],
                         jData["attributes"]["rotation"]["w"])
        self.scale = (jData["attributes"]["scale"]["x"],
                      jData["attributes"]["scale"]["y"],
                      jData["attributes"]["scale"]["z"])
        hcolor = jData["attributes"]["color"].lstrip('#')
        self.color = tuple(int(hcolor[c:c + 2], 16) for c in (0, 2, 4))
        if "url" in jData["attributes"]:
            self.url = jData["attributes"]["url"]
        if "material" in jData["attributes"] and "colorWrite" in jData["attributes"]["material"]:
            self.transparent_occlude = not jData["attributes"]["material"]["colorWrite"]
        if "parent" in jData["attributes"]:
            self.parent = jData["attributes"]["parent"]
        if "click-listener" in jData["attributes"]:
            self.clickable = True
        if "dynamic-body" in jData["attributes"]:
            self.physics = arena.Physics(
                jData["attributes"]["dynamic-body"]["type"])
        # self.text self.transparency self.data self.ttl


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
        data='{"material": {"transparent":true,"shader":"flat","opacity":0.5}}',
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
        data='{"material": {"transparent":true,"shader":"flat","opacity":0.5}}',
        color=(0, 0, 0),
        location=(0, size[1] / 20, 0),
        scale=(size[0], size[1] / 10, size[2]))


def set_clipboard(camname,
                  callback=None,
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
        callback=callback,
    )


def update_persisted_obj(object_id, label, action="update", data=None,
                         persist="true", ttl=None):
    msg = {
        "object_id": object_id,
        "action": action,
    }
    if action == "update":
        msg["type"] = "object"
        msg["persist"] = persist
        msg["ttl"] = ttl
        msg["data"] = data
    arena.arena_publish(REALM + "/s/" + SCENE + "/" + object_id, msg)
    print(label + " " + object_id)


def occlude_obj(object_id, occlude):
    data = {"material": {"colorWrite": occlude == BOOLS[1]}}
    update_persisted_obj(object_id, "Occluded", data=data)


def color_obj(object_id, hcolor):
    data = {"material": {"color": "#" + hcolor}}
    update_persisted_obj(object_id, "Recolored", data=data)


def scale_obj(object_id, scale):
    data = {"scale": {"x": scale[0], "y": scale[1], "z": scale[2]}}
    update_persisted_obj(object_id, "Resized", data=data)


def move_obj(object_id, pos):
    data = {"position": {"x": pos[0], "y": pos[1], "z": pos[2]}}
    update_persisted_obj(object_id, "Relocated", data=data)


def rotate_obj(object_id, rot):
    data = {"rotation": {"x": rot[0], "y": rot[1], "z": rot[2], "w": rot[3]}}
    update_persisted_obj(object_id, "Rotated", data=data)


def delete_obj(object_id):
    update_persisted_obj(object_id, "Deleted", action="delete")


def panel_callback(event=None):
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
    if mode == Mode.NONE:
        pass  # skip over
    elif mode == Mode.CREATE:
        update_dropdown(camname, objid, mode, SHAPES, 2, shapes_callback)
        USERS[camname].clipboard = set_clipboard(
            camname, callback=clipboard_callback,
            obj_type=arena.Shape(USERS[camname].target_style))
    elif mode == Mode.MODEL:
        update_dropdown(camname, objid, mode, MODELS, 2, models_callback)
        idx = MODELS.index(USERS[camname].target_style)
        url = MANIFEST[idx]['url_gltf']
        USERS[camname].clipboard = set_clipboard(
            camname, callback=clipboard_callback, obj_type=arena.Shape.gltf_model,
            scale=SCL_GLTF, url=url)
    elif mode == Mode.COLOR:
        update_dropdown(camname, objid, mode, COLORS, -2, colors_callback)
    elif mode == Mode.LOCK:  # TODO: implement boolean
        USERS[camname].follow_lock = not USERS[camname].follow_lock
        USERS[camname].panel[objid].set_on(USERS[camname].follow_lock)
        # TODO: after lock ensure original ray keeps lock button in reticle
    elif mode == Mode.OCCLUDE:
        update_dropdown(camname, objid, mode, BOOLS, -2, bool_callback)
    elif mode == Mode.REDPILL:  # TODO: implement boolean
        show_redpill_scene()
    elif mode == Mode.RENAME:
        USERS[camname].typetext = ""
        update_dropdown(camname, objid, mode, KEYS, -2, rename_callback)
        USERS[camname].set_textright(USERS[camname].typetext)
    elif mode == Mode.WALL:
        USERS[camname].clipboard = set_clipboard(
            camname, obj_type=arena.Shape.cube, callback=wall_callback)


def update_dropdown(camname, objid, mode, options, row, callback):
    # show new dropdown
    if USERS[camname].panel[objid].on:
        followname = USERS[camname].follow.objName
        maxwidth = min(len(options), 10)
        drop_button_offset = -math.floor(maxwidth / 2)
        for i, option in enumerate(options):
            if mode is Mode.COLOR:
                bcolor = tuple(int(option[c:c + 2], 16) for c in (0, 2, 4))
            else:
                bcolor = CLR_SELECT
            dbutton = Button(camname, mode, option, (i % maxwidth) + drop_button_offset,
                             row, parent=followname, color=bcolor, drop=option, callback=callback)
            USERS[camname].dbuttons.append(dbutton)
            if (i + 1) % maxwidth == 0:  # next row
                if row < 0:
                    row -= 1
                else:
                    row += 1
        # make default selection
        if mode is Mode.COLOR:
            rcolor = tuple(int(options[0][c:c + 2], 16) for c in (0, 2, 4))
        else:
            rcolor = CLR_HUDTEXT
        USERS[camname].set_textright(options[0], color=rcolor)
        USERS[camname].target_style = options[0]


def models_callback(event=None):
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
        camname, callback=clipboard_callback, obj_type=arena.Shape.gltf_model,
        scale=SCL_GLTF, url=url)
    USERS[camname].set_textright(model)
    USERS[camname].target_style = model


def shapes_callback(event=None):
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[3] + "_" + obj[4] + "_" + obj[5]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    shape = obj[2]
    USERS[camname].clipboard = set_clipboard(
        camname, callback=clipboard_callback, obj_type=arena.Shape(shape))
    USERS[camname].set_textright(shape)
    USERS[camname].target_style = shape


def colors_callback(event=None):
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


def bool_callback(event=None):
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[3] + "_" + obj[4] + "_" + obj[5]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    boolean = obj[2]
    USERS[camname].set_textright(boolean)
    USERS[camname].target_style = boolean


def rename_callback(event=None):
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[3] + "_" + obj[4] + "_" + obj[5]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    key = obj[2]
    USERS[camname].set_textright(key)
    USERS[camname].target_style = key
    if key == 'back':
        if USERS[camname].typetext:
            USERS[camname].typetext = USERS[camname].typetext[:-1]
    else:
        USERS[camname].typetext = USERS[camname].typetext + key
    USERS[camname].set_textright(USERS[camname].typetext)


def show_redpill_scene():
    # any scene changes must not persist
    # show gridlines
    for z in range(-GRIDLEN, GRIDLEN+1):
        arena.Object(objType=arena.Shape.line, ttl=TTL_TEMP,
                     line=arena.Line((-GRIDLEN, FLOOR_Y, z), (GRIDLEN, FLOOR_Y, z), 1, '#00ff00'))
    for x in range(-GRIDLEN, GRIDLEN+1):
        arena.Object(objType=arena.Shape.line, ttl=TTL_TEMP,
                     line=arena.Line((x, FLOOR_Y, -GRIDLEN), (x, FLOOR_Y, GRIDLEN), 1, '#00ff00'))
    pobjs = get_network_persisted_scene()
    for pobj in pobjs:
        obj = ObjectPersistence(pobj)
        # show occulded objects
        if obj.transparent_occlude:
            # data = {
            #    "material": {
            #        "colorWrite": True,
            #        "transparent": True,
            #        "opacity": 0.5}}
            # update_persisted_obj(obj.object_id, "Temp unoccluded", data=data,
            #                     persist="false", ttl=TTL_TEMP)
            arena.Object(
                objName="redpill_" + obj.object_id,
                objType=obj.object_type,
                location=obj.position,
                rotation=obj.rotation,
                scale=obj.scale,
                color=obj.color,
                persist=False,
                ttl=TTL_TEMP,
                clickable=True,
                url=obj.url,
                data=(
                    '{"material":{"colorWrite":true,"transparent":true,"opacity":0.5}}')
            )
            print("Wrapping occlusion " + obj.object_id)


def do_rename(old_id, new_id):
    pobjs = get_network_persisted_obj(old_id)
    if not pobjs:
        return
    obj = ObjectPersistence(pobjs[0])
    arena.Object(
        objName=new_id,
        objType=obj.object_type,
        location=obj.position,
        rotation=obj.rotation,
        scale=obj.scale,
        color=obj.color,
        persist=obj.persist,
        clickable=obj.clickable,
        url=obj.url,
        ttl=obj.parent,
        parent=obj.parent,
        physics=obj.physics,
        transparentOcclude=obj.transparent_occlude,
        line=obj.line,
        thickline=obj.thickline,
        collision_listener=obj.collision_listener,
        transparency=obj.transparency,
        impulse=obj.impulse,
        animation=obj.animation,
        # data=obj.data,
    )
    print("Duplicating " + old_id + " to " + new_id)
    delete_obj(old_id)


def show_redpill_obj(camname, object_id):
    # any scene changes must not persist
    pobjs = get_network_persisted_obj(object_id)
    if not pobjs:
        return
    obj = ObjectPersistence(pobjs[0])
    # enable mouse enter/leave pos/rot/scale
    USERS[camname].set_textstatus(object_id + ' p' + str(obj.position) +
                                  ' r' + str(obj.rotation) + ' s' + str(obj.scale))


def do_move_select(camname, object_id):
    pobjs = get_network_persisted_obj(object_id)
    if not pobjs:
        return
    obj = ObjectPersistence(pobjs[0])
    USERS[camname].target_id = object_id
    USERS[camname].clipboard = set_clipboard(
        camname,
        callback=clipboard_callback,
        obj_type=obj.object_type,
        rotation=obj.rotation,
        scale=obj.scale,
        color=obj.color,
        url=obj.url,
    )


def do_nudge_select(object_id):
    pobjs = get_network_persisted_obj(object_id)
    if not pobjs:
        return
    obj = ObjectPersistence(pobjs[0])
    color = CLR_NUDGE
    delim = "_nudge_"
    callback = nudgeline_callback
    # generate child 6dof non-persist, clickable lines
    make_clickline("x", 1, object_id, delim, color, callback, obj.position)
    make_clickline("x", -1, object_id, delim, color, callback, obj.position)
    make_clickline("y", 1, object_id, delim, color, callback, obj.position)
    make_clickline("y", -1, object_id, delim, color, callback, obj.position)
    make_clickline("z", 1, object_id, delim, color, callback, obj.position)
    make_clickline("z", -1, object_id, delim, color, callback, obj.position)
    arena.Object(  # follow spot on ground
        objType=arena.Shape.circle,
        objName=(object_id + delim+"spot"),
        scale=obj.scale,
        color=color,
        location=(obj.position[0], FLOOR_Y, obj.position[2]),
        rotation=(-0.7, 0, 0, 1),
        ttl=TTL_TEMP,
        data=('{"material": {"transparent":true,"opacity":0.5}}'),
    )


def do_scale_select(object_id):
    pobjs = get_network_persisted_obj(object_id)
    if not pobjs:
        return
    obj = ObjectPersistence(pobjs[0])
    color = CLR_SCALE
    delim = "_scale_"
    callback = scaleline_callback
    # generate 2 child non-persist, clickable lines
    make_clickline("y", 1, object_id, delim, color, callback, obj.position)
    make_clickline("y", -1, object_id, delim, color, callback, obj.position)


def make_clickline(deg, linelen, object_id, delimiter, color, callback, start):
    endx = endy = endz = 0
    direction = "p"
    if linelen < 0:
        direction = "n"
    if deg == "x":
        endx = linelen*CLICKLINE_LEN
    elif deg == "y":
        endy = linelen*CLICKLINE_LEN
    elif deg == "z":
        endz = linelen*CLICKLINE_LEN
    arena.Object(
        objType=arena.Shape.line,
        objName=(object_id + delimiter + deg + direction),
        color=color,
        clickable=True,
        ttl=TTL_TEMP,
        callback=callback,

        # as parent, tight clickable region, no AR mousedown
        parent=object_id,
        data=('{"start": {"x":0,"y":0,"z":0}, ' +
              '"end": {"x":' + str(endx * 10) +
              ',"y":' + str(endy * 10) +
              ',"z":' + str(endz * 10) + '}}'),

        # as independent, too wide clickable region, good AR mousedown
        # data=('{"start": {"x":' + str(start[0]) +
        #       ',"y":' + str(start[1]) +
        #       ',"z":' + str(start[2]) + '}, ' +
        #       '"end": {"x":' + str(start[0]+endx) +
        #       ',"y":' + str(start[1]+endy) +
        #       ',"z":' + str(start[2]+endz) + '}}'),
        # scale=SCL_NUDGE,
        # scale=(0.00000001, 0.00000001, 0.00000001),
    )


def do_move_relocate(camname, newlocation):
    move_obj(USERS[camname].target_id, newlocation)
    USERS[camname].clipboard.delete()
    USERS[camname].target_id = None


def incr_pos(coord, incr):
    if (coord % incr) > incr:
        res = math.ceil(coord / incr) * incr
    else:
        res = coord + incr
    return float(format(res, '.1f'))


def incr_neg(coord, incr):
    if (coord % incr) > incr:
        res = math.floor(coord / incr) * incr
    else:
        res = coord - incr
    return float(format(res, '.1f'))


def nudgeline_callback(event=None):
    # print(event.object_id + "  " + str(event.event_action) +
    #      "  " + str(event.event_type))
    # allow any user to nudge an object
    if event.event_type != arena.EventType.mousedown:
        return
    nudge_id = event.object_id.split("_nudge_")
    object_id = nudge_id[0]
    direction = (nudge_id[1])[:2]
    pobjs = get_network_persisted_obj(object_id)
    if not pobjs:
        return
    obj = ObjectPersistence(pobjs[0])
    nudged = loc = obj.position
    inc = NUDGE_INCR
    if direction == "xp":
        nudged = (incr_pos(loc[0], inc), loc[1], loc[2])
    elif direction == "xn":
        nudged = (incr_neg(loc[0], inc), loc[1], loc[2])
    elif direction == "yp":
        nudged = (loc[0], incr_pos(loc[1], inc), loc[2])
    elif direction == "yn":
        nudged = (loc[0], incr_neg(loc[1], inc), loc[2])
    elif direction == "zp":
        nudged = (loc[0], loc[1], incr_pos(loc[2], inc))
    elif direction == "zn":
        nudged = (loc[0], loc[1], incr_neg(loc[2], inc))
    print(str(loc) + " to " + str(nudged))
    move_obj(object_id, nudged)
    do_nudge_select(object_id)  # update nudgelines


def scaleline_callback(event=None):
    # allow any user to scale an object
    if event.event_type != arena.EventType.mousedown:
        return
    scale_id = event.object_id.split("_scale_")
    object_id = scale_id[0]
    direction = (scale_id[1])[:2]
    pobjs = get_network_persisted_obj(object_id)
    if not pobjs:
        return
    obj = ObjectPersistence(pobjs[0])
    scaled = sca = obj.scale
    inc = SCALE_INCR
    if direction == "yp":
        scaled = (incr_pos(sca[0], inc), incr_pos(
            sca[1], inc), incr_pos(sca[2], inc))
    elif direction == "yn":
        scaled = (incr_neg(sca[0], inc), incr_neg(
            sca[1], inc), incr_neg(sca[2], inc))
    if scaled[0] == 0 or scaled[1] == 0 or scaled[2] == 0:
        return
    print(str(sca) + " to " + str(scaled))
    scale_obj(object_id, scaled)
    do_scale_select(object_id)  # update scalelines


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


def wall_callback(event=None):
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[1] + "_" + obj[2] + "_" + obj[3]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    if not USERS[camname].wall_start:
        USERS[camname].wall_start = USERS[camname].location
    else:
        USERS[camname].wall_end = USERS[camname].location
        randstr = str(random.randrange(0, 1000000))
        # make a copy of static object in place
        # arena.Object( #TODO calculate wall
        #     persist=True,
        #     objName="wall_" + randstr,
        #     objType=arena.Shape.cube,
        #     location=location,
        #     rotation=(0, 0, 0, 1),
        #     scale=scale,
        # )
        print("wall_" + randstr+" from "+str(USERS[camname].wall_start) +
              " to "+str(USERS[camname].wall_end))
        USERS[camname].wall_start = None  # reset


def scene_callback(msg):
    # This is the MQTT message callback function for the scene
    json_msg = json.loads(msg)
    if json_msg["action"] == "create" and json_msg["data"]["object_type"] == "camera":
        # camera updates define users present
        camname = json_msg["object_id"]
        if camname not in USERS:
            USERS[camname] = User(camname)

        # save camera's location in the world
        USERS[camname].location = (json_msg["data"]["position"]["x"],
                                   json_msg["data"]["position"]["y"],
                                   json_msg["data"]["position"]["z"])

        rx = json_msg["data"]["rotation"]["x"]
        ry = json_msg["data"]["rotation"]["y"]
        # print ("rx " + str(rx) + " ry " + str(ry) +
        #       " | ory " + str(users[camname].locky))

        # floating controller
        if not USERS[camname].follow_lock:
            ty = -(ry + USERS[camname].locky) / 0.7 * math.pi / 2
            tx = -(rx + USERS[camname].lockx) / 0.7 * math.pi / 2
            px = PANEL_RADIUS * -math.cos(ty)
            py = PANEL_RADIUS * math.sin(tx)
            pz = PANEL_RADIUS * math.sin(ty)
            USERS[camname].follow.position(location=(px, py, pz))
        # else: # TODO: panel lock location drop is inaccurate
            # users[camname].lockx = rx + LOCK_XOFF
            # users[camname].locky = -(ry * math.pi) - LOCK_YOFF

    # mouse event
    elif json_msg["action"] == "clientEvent":
        # print(json_msg["object_id"] + "  " +
        #      json_msg["action"] + "  " + json_msg["type"])
        objid = json_msg["object_id"]
        # camera updates define users present
        camname = json_msg["data"]["source"]
        if camname not in USERS:
            USERS[camname] = User(camname)

        # show objects with events
        if json_msg["type"] == "mouseenter":
            if USERS[camname].mode == Mode.REDPILL:
                show_redpill_obj(camname, objid)
            else:
                USERS[camname].set_textstatus(objid)
        elif json_msg["type"] == "mouseleave":
            USERS[camname].set_textstatus("")

        # handle click
        elif json_msg["type"] == "mousedown":
            # clicked on persisted object to modify
            if USERS[camname].mode == Mode.DELETE:
                delete_obj(objid)
            elif USERS[camname].mode == Mode.MOVE:
                do_move_select(camname, objid)
            elif USERS[camname].mode == Mode.NUDGE:
                do_nudge_select(objid)
            elif USERS[camname].mode == Mode.SCALE:
                do_scale_select(objid)
            elif USERS[camname].mode == Mode.COLOR:
                color_obj(objid, USERS[camname].target_style)
            elif USERS[camname].mode == Mode.OCCLUDE:
                occlude_obj(objid, USERS[camname].target_style)
            elif USERS[camname].mode == Mode.RENAME:
                new_id = USERS[camname].typetext
                USERS[camname].typetext = ""
                do_rename(objid, new_id)


def get_network_persisted_obj(object_id):
    data = urllib.request.urlopen(
        'https://' + BROKER + '/persist/' + SCENE + '/' + object_id).read()
    output = json.loads(data)
    return output


def get_network_persisted_scene():
    data = urllib.request.urlopen(
        'https://' + BROKER + '/persist/' + SCENE).read()
    output = json.loads(data)
    return output


# parse args and wait for events
init_args()
random.seed()
arena.init(BROKER, REALM, SCENE, scene_callback)
arena.handle_events()
