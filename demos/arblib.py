# arblib.py
#
# AR Builder Library
# Utility classes and methods for AR Builder.

# pylint: disable=missing-docstring

import enum
import json
import urllib.request

from scipy.spatial.transform import Rotation

import arena

CLICKLINE_LEN = 1  # meters
CLICKLINE_SCL = (1, 1, 1)  # meters
FLOOR_Y = 0.001  # meters
GRIDLEN = 20  # meters
CLIP_RADIUS = 1  # meters
PANEL_RADIUS = 1  # meters
LOCK_XOFF = 0  # quaternion vector
LOCK_YOFF = 0.7  # quaternion vector
TTL_TEMP = 30  # seconds
CLR_HUDTEXT = (200, 200, 200)  # light gray
CLR_NUDGE = (255, 255, 0)  # yellow
CLR_SCALE = (0, 0, 255)  # blue
CLR_STRETCH = (255, 0, 0)  # red
CLR_ROTATE = (255, 165, 0)  # orange
CLR_SELECT = (255, 255, 0)  # yellow
CLR_GRID = (0, 255, 0)  # green
CLR_ENABLED = (255, 255, 255)  # white
CLR_DISABLED = (128, 128, 128)  # gray
SCL_GLTF = (0.1, 0.1, 0.1)  # meters
QUAT_VEC_RGTS = [-0.7, -0.5, 0, 0.5, 0.7, 1]
QUAT_DEV_RGT = 0.075
WALL_WIDTH = 0.1  # meters

GAZES = [
    [(0, 0, 0, 1), (0, 0, -0.7, 0.7), (0, 0, 1, 0), (0, 0, 0.7, 0.7),  # F
     (0, 1, 0, 0), (-0.7, -0.7, 0, 0), (0.7, 0.7, 0, 0), (1, 0, 0, 0)],  # B
    [(0, 0.7, 0, 0.7), (-0.5, 0.5, -0.5, 0.5), (0.5, 0.5, 0.5, 0.5), (0.7, 0, 0.7, 0),  # L
     (0, -0.7, 0, 0.7), (0.5, -0.5, -0.5, 0.5), (-0.5, -0.5, 0.5, 0.5), (-0.7, 0, 0.7, 0)],  # R
    [(-0.7, 0, 0, 0.7), (-0.5, 0.5, 0.5, 0.5), (-0.5, -0.5, -0.5, 0.5), (0, 0.7, 0.7, 0),  # D
     (0.7, 0, 0, 0.7), (0.5, 0.5, -0.5, 0.5), (0.5, -0.5, 0.5, 0.5), (0, -0.7, 0.7, 0)],  # U
]


def get_keys():
    keys = []
    keys.extend(list("1234567890"))
    keys.extend(list("qwertyuiop"))
    keys.extend(list("asdfghjkl"))
    keys.append('underline')
    keys.extend(list("zxcvbnm-"))
    keys.append('apriltag')
    keys.append('back')
    return keys


KEYS = get_keys()
BOOLS = ["on", "off"]
METERS = ["mm", "cm", "dm", "m"]
DEGREES = ["1", "5", "10", "45", "90"]
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
DEF_MANIFEST = [{  # default model, if none loaded
    "name": "duck",
    "url_gltf": "models/Duck.glb",
}]


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
    LAMP = "lamp"
    STRETCH = "stretch"
    PARENT = "parent"


class ButtonType(enum.Enum):
    ACTION = "action"
    TOGGLE = "toggle"


class User:
    def __init__(self, camname, panel_callback):
        self.camname = camname
        self.mode = Mode.NONE
        self.target_id = self.location = self.rotation = None
        self.target_style = self.typetext = ""
        self.locky = LOCK_YOFF
        self.lockx = LOCK_XOFF
        self.wloc_start = self.wloc_end = None
        self.wrot_start = self.wrot_end = None
        self.lamp = None
        init_origin()

        # set HUD to each user
        self.clipboard = arena.Object(scale=(0, 0, 0))
        self.clipboard.delete()  # workaround for non-empty object
        self.hudtext_left = self.make_hudtext(
            "hudTextLeft", (-0.15, 0.15, -0.5), str(self.mode))
        self.hudtext_right = self.make_hudtext(
            "hudTextRight", (0.1, 0.15, -0.5), "")
        self.hudtext_status = self.make_hudtext(
            "hudTextStatus", (0.02, -0.15, -0.5), "")  # workaround x=0 bad?

        # AR Control Panel
        self.follow_lock = False
        self.follow = arena.Object(
            objName=("follow_" + camname),
            objType=arena.Shape.cube,
            parent=camname,
            transparency=arena.Transparency(True, 0),
            location=(0, 0, -PANEL_RADIUS * 0.1),
            scale=(0.1, 0.01, 0.1),
            rotation=(0.7, 0, 0, 0.7),
        )
        self.redpill = False
        self.panel = {}  # button dictionary
        followname = self.follow.objName
        self.dbuttons = []
        buttons = [
            # top row
            [Mode.ROTATE, -2, 1, True, ButtonType.ACTION],
            [Mode.NUDGE, -1, 1, True, ButtonType.ACTION],
            [Mode.SCALE, 0, 1, True, ButtonType.ACTION],
            [Mode.STRETCH, 1, 1, True, ButtonType.ACTION],
            [Mode.MODEL, 2, 1, True, ButtonType.ACTION],
            [Mode.CREATE, 3, 1, True, ButtonType.ACTION],
            # center row
            [Mode.REDPILL, -2, 0, True, ButtonType.TOGGLE],
            [Mode.MOVE, -1, 0, True, ButtonType.ACTION],
            [Mode.LOCK, 0, 0, True, ButtonType.TOGGLE],
            [Mode.DELETE, 1, 0, True, ButtonType.ACTION],
            [Mode.PARENT, 2, 0, True, ButtonType.ACTION],
            # bottom row
            [Mode.WALL, -2, -1, True, ButtonType.ACTION],
            [Mode.OCCLUDE, -1, -1, True, ButtonType.ACTION],
            [Mode.RENAME, 0, -1, True, ButtonType.ACTION],
            [Mode.COLOR, 1, -1, True, ButtonType.ACTION],
            [Mode.LAMP, 2, -1, True, ButtonType.TOGGLE],
        ]
        for but in buttons:
            pbutton = Button(camname, but[0], but[1], but[2], enable=but[3], btype=but[4],
                             parent=followname, callback=panel_callback)
            self.panel[pbutton.button.objName] = pbutton

    def make_hudtext(self, label, location, text):
        return arena.Object(
            objName=(label + "_" + self.camname),
            objType=arena.Shape.text,
            parent=self.camname,
            text=text,
            location=location,
            color=CLR_HUDTEXT,
            scale=(0.1, 0.1, 0.1),
        )

    def set_textleft(self, mode):
        self.hudtext_left.update(text=str(mode))

    def set_textright(self, text, color=CLR_HUDTEXT):
        self.hudtext_right.update(text=text, color=color)

    def set_textstatus(self, text):
        self.hudtext_status.update(text=text)

    def set_lamp(self, enabled):
        if enabled:
            self.lamp = arena.Object(
                objName="lamp_" + self.camname,
                objType=arena.Shape.light,
                parent=self.camname,
                color=(144, 144, 173),
                data='{"light":{"type":"point","intensity":"0.75"}}',
            )
        elif self.lamp:
            self.lamp.delete()


class Button:
    def __init__(self, camname, mode, x=0, y=0, label="", parent=None,
                 drop=None, color=CLR_ENABLED, enable=True, callback=None,
                 btype=ButtonType.ACTION):
        if label == "":
            label = mode.value
        if parent is None:
            parent = camname
            scale = (0.1, 0.1, 0.01)
        else:
            scale = (1, 1, 1)
        self.type = btype
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
        self.active = False
        if drop is None:
            obj_name = "button_" + mode.value + "_" + camname
        else:
            obj_name = "button_" + mode.value + "_" + drop + "_" + camname
        shape = arena.Shape.cube
        if btype == ButtonType.TOGGLE:
            shape = arena.Shape.cylinder
            scale = (scale[0] / 2, scale[1], scale[2] / 2)
        self.button = arena.Object(  # cube is main button
            objName=obj_name,
            objType=shape,
            parent=parent,
            data='{"material":{"transparent":true,"opacity":0.4,"shader":"flat"}}',
            location=(x * 1.1, PANEL_RADIUS, y * -1.1),
            scale=scale,
            color=self.colorbut,
            clickable=True,
            callback=callback,
        )
        scale = (1, 1, 1)
        if btype == ButtonType.TOGGLE:
            scale = (scale[0] * 2, scale[1] * 2, scale[2])
        self.text = arena.Object(  # text child of button
            objName=("text_" + self.button.objName),
            objType=arena.Shape.text,
            parent=self.button.objName,
            text=self.label,
            location=(0, -0.1, 0),  # location inside to prevent ray events
            rotation=(-0.7, 0, 0, 0.7),
            scale=scale,
            color=self.colortxt,
        )

    def set_active(self, active):
        self.active = active
        if active:
            self.button.update(color=CLR_SELECT)
        else:
            self.button.update(color=CLR_ENABLED)
            self.text.update(color=self.colortxt)

    def delete(self):
        """Delete method so that child text object also gets deleted."""
        self.text.delete()
        self.button.delete()


class ObjectPersistence:
    """Converts persistence database object into python without using MQTT."""
    object_id = ""
    object_Type = arena.Shape.cube
    position = (0, 0, 0)
    rotation = (0, 0, 0, 1)
    scale = (1, 1, 1)
    color = (255, 255, 255)
    color_material = None
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
        # Warning: We may lose some object detail, not useful for full copy.
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
        self.color = hex2rgb(jData["attributes"]["color"])
        if "url" in jData["attributes"]:
            self.url = jData["attributes"]["url"]
        if "material" in jData["attributes"]:
            if "colorWrite" in jData["attributes"]["material"]:
                self.transparent_occlude = not jData["attributes"]["material"]["colorWrite"]
            if "color" in jData["attributes"]["material"]:
                self.color_material = hex2rgb(
                    jData["attributes"]["material"]["color"])
        if "parent" in jData["attributes"]:
            self.parent = jData["attributes"]["parent"]
        if "click-listener" in jData["attributes"]:
            self.clickable = True
        if "dynamic-body" in jData["attributes"]:
            if "type" in jData["attributes"]["dynamic-body"]:
                self.physics = arena.Physics(
                    jData["attributes"]["dynamic-body"]["type"])
        # self.text self.transparency self.data self.ttl


def init_origin():
    """Origin object, construction cone, so user knows ARB is running."""
    size = [0.2, 0.4, 0.2]
    arena.Object(  # 370mm x 370mm # 750mm
        objType=arena.Shape.cone, objName="arb-origin",
        data='{"material":{"transparent":true,"opacity":0.5,"shader":"flat"}}',
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
        data='{"material":{"transparent":true,"opacity":0.5,"shader":"flat"}}',
        color=(0, 0, 0),
        location=(0, size[1] / 20, 0),
        scale=(size[0], size[1] / 10, size[2]))


def set_clipboard(camname,
                  callback=None,
                  obj_type=arena.Shape.sphere,
                  scale=(0.05, 0.05, 0.05),
                  color=CLR_ENABLED,
                  url=""):
    clip = arena.Object(
        objName=("clipboard_" + camname),
        objType=obj_type,
        color=color,
        location=(0, 0, -CLIP_RADIUS),
        parent=camname,
        scale=scale,
        transparency=arena.Transparency(True, 0.4),
        url=url,
        clickable=True,
        callback=callback,
    )
    target_scale = (clip.scale[0]/10, clip.scale[1]/10, clip.scale[2]/10)
    arena.Object(
        objName=("cliptarget_" + camname),
        objType=arena.Shape.sphere,
        color=color,
        location=(0, 0, 0),
        parent=clip.objName,
        scale=target_scale,
        transparency=arena.Transparency(True, 0.4),
        clickable=True,
        callback=callback,
    )
    return clip


def update_persisted_obj(realm, scene, object_id, label,
                         action="update", data=None, persist="true", ttl=None):
    msg = {
        "object_id": object_id,
        "action": action,
    }
    if action == "update":
        msg["type"] = "object"
        msg["persist"] = persist
        msg["ttl"] = ttl
        msg["data"] = data
    arena.arena_publish(realm + "/s/" + scene + "/" + object_id, msg)
    print(label + " " + object_id)


def occlude_obj(realm, scene, object_id, occlude):
    data = {"material": {"colorWrite": occlude == BOOLS[1]}, "render-order": 0}
    update_persisted_obj(realm, scene, object_id, "Occluded", data=data)


def color_obj(realm, scene, object_id, hcolor):
    # NOTE: "color" updates base color, NOT reflected live.
    # "material":{"color"} updates raw color, IS reflected live.
    data = {"color": "#" + hcolor, "material": {"color": "#" + hcolor}}
    update_persisted_obj(realm, scene, object_id, "Recolored", data=data)


def stretch_obj(realm, scene, object_id, scale, position):
    data = {"scale": {
        "x": arena.agran(scale[0]),
        "y": arena.agran(scale[1]),
        "z": arena.agran(scale[2])
    }, "position": {
        "x": arena.agran(position[0]),
        "y": arena.agran(position[1]),
        "z": arena.agran(position[2])
    }}
    update_persisted_obj(realm, scene, object_id, "Stretched", data=data)


def scale_obj(realm, scene, object_id, scale):
    data = {"scale": {
        "x": arena.agran(scale[0]),
        "y": arena.agran(scale[1]),
        "z": arena.agran(scale[2])
    }}
    update_persisted_obj(realm, scene, object_id, "Resized", data=data)


def move_obj(realm, scene, object_id, position):
    data = {"position": {
        "x": arena.agran(position[0]),
        "y": arena.agran(position[1]),
        "z": arena.agran(position[2])
    }}
    update_persisted_obj(realm, scene, object_id, "Relocated", data=data)


def rotate_obj(realm, scene, object_id, rotation):
    data = {"rotation": {
        "x": arena.agran(rotation[0]),
        "y": arena.agran(rotation[1]),
        "z": arena.agran(rotation[2]),
        "w": arena.agran(rotation[3])
    }}
    update_persisted_obj(realm, scene, object_id, "Rotated", data=data)


def parent_obj(realm, scene, object_id, parent_id):
    data = {"parent": parent_id}
    update_persisted_obj(realm, scene, object_id, "Parent set", data=data)


def delete_obj(realm, scene, object_id):
    update_persisted_obj(realm, scene, object_id, "Deleted", action="delete")


def rgb2hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])


def hex2rgb(hcolor):
    hcolor = hcolor.lstrip('#')
    return tuple(int(hcolor[c:c + 2], 16) for c in (0, 2, 4))


def temp_loc_marker(location, color):
    return arena.Object(objType=arena.Shape.sphere, ttl=120, color=color,
                        transparency=arena.Transparency(True, 0.5),
                        location=location, scale=(0.02, 0.02, 0.02), clickable=True)


def temp_rot_marker(location, rotation):
    return arena.Object(objType=arena.Shape.cube, ttl=120, rotation=rotation,
                        location=location, scale=(0.02, 0.01, 0.15), clickable=True)


def rotation_quat2euler(quat):
    rotq = Rotation.from_quat(list(quat))
    return tuple(rotq.as_euler('xyz', degrees=True))


def rotation_euler2quat(euler):
    rote = Rotation.from_euler('xyz', list(euler), degrees=True)
    return tuple(rote.as_quat())


def probable_quat(num):
    # if reasonably close to 90 deg, align to right angle quaternion
    lst = QUAT_VEC_RGTS
    closest = lst[min(range(len(lst)), key=lambda i: abs(lst[i] - num))]
    if abs(num - closest) < QUAT_DEV_RGT:
        return closest
    return num


def get_network_persisted_obj(object_id, broker, scene):
    data = urllib.request.urlopen(
        'https://' + broker + '/persist/' + scene + '/' + object_id).read()
    output = json.loads(data)
    return output


def get_network_persisted_scene(broker, scene):
    data = urllib.request.urlopen(
        'https://' + broker + '/persist/' + scene).read()
    output = json.loads(data)
    return output
