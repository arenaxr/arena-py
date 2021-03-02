# arblib.py
#
# AR Builder Library
# Utility classes and methods for AR Builder.

# pylint: disable=missing-docstring

import enum
import re

import webcolors
from arena import (Box, Circle, Cone, Cylinder, Dodecahedron, Icosahedron,
                   Light, Material, Object, Octahedron, Physics, Plane, Ring,
                   Scene, Sphere, Tetrahedron, Text, Torus, TorusKnot,
                   Triangle)
from scipy.spatial.transform import Rotation

CLICKLINE_LEN = 1  # meters
CLICKLINE_SCL = (1, 1, 1)  # meters
FLOOR_Y = 0  # meters
GRIDLEN = 20  # meters
PANEL_RADIUS = 1  # meters
CLIP_RADIUS = PANEL_RADIUS + 0.25  # meters
LOCK_XOFF = 0  # quaternion vector
LOCK_YOFF = 0.7  # quaternion vector
CLR_HUDTEXT = (128, 128, 128)  # gray
CLR_NUDGE = (255, 255, 0)  # yellow
CLR_SCALE = (0, 0, 255)  # blue
CLR_STRETCH = (255, 0, 0)  # red
CLR_ROTATE = (255, 165, 0)  # orange
CLR_SELECT = (255, 255, 0)  # yellow
CLR_GRID = (0, 255, 0)  # green
CLR_BUTTON = (200, 200, 200)  # white-ish
CLR_BUTTON_DISABLED = (128, 128, 128)  # gray
CLR_BUTTON_TEXT = (0, 0, 0)  # black
OPC_BUTTON = 0.1  # % opacity
OPC_BUTTON_HOVER = 0.25  # % opacity
OPC_CLINE = 0.1  # % opacity
OPC_CLINE_HOVER = 0.9  # % opacity
TTL_TEMP = 30  # seconds
QUAT_VEC_RGTS = [-1, -0.7, -0.5, 0, 0.5, 0.7, 1]
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
ROTATE_CONES = {
    "xp": [(0.7, 0, 0, 0.7), (-0.7, 0, 0, 0.7)],
    "yp": [(0, 0, -0.7, 0.7), (0, 0, 0.7, 0.7)],
    "zp": [(0, 0, 0.7, 0.7), (0, 0, -0.7, 0.7)],
}
DIRECT_CONES = {
    "xp": [(0, 0, -0.7, 0.7), (0, 0, 0.7, 0.7)],
    "xn": [(0, 0, 0.7, 0.7), (0, 0, -0.7, 0.7)],
    "yp": [(0, 0, 0, 1), (-1, 0, 0, 0)],
    "yn": [(-1, 0, 0, 0), (0, 0, 0, 1)],
    "zp": [(0.7, 0, 0, 0.7), (-0.7, 0, 0, 0.7)],
    "zn": [(-0.7, 0, 0, 0.7), (0.7, 0, 0, 0.7)],
}


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
SHAPES = [Sphere()['data']['object_type'],
          Box()['data']['object_type'],
          Cone()['data']['object_type'],
          Cylinder()['data']['object_type'],
          Dodecahedron()['data']['object_type'],
          Icosahedron()['data']['object_type'],
          Octahedron()['data']['object_type'],
          Tetrahedron()['data']['object_type'],
          Torus()['data']['object_type'],
          TorusKnot()['data']['object_type'],
          Circle()['data']['object_type'],
          Plane()['data']['object_type'],
          Ring()['data']['object_type'],
          Triangle()['data']['object_type']]
DEF_MANIFEST = [{  # default model, if none loaded
    "name": "duck",
    "url_gltf": "models/Duck.glb",
    "scale": 0.1
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
    def __init__(self, scene: Scene, camname, panel_callback):
        self.scene = scene
        self.camname = camname
        self.mode = Mode.NONE
        self.clipboard = self.cliptarget = None
        self.target_id = self.location = self.rotation = None
        self.target_style = self.typetext = ""
        self.locky = LOCK_YOFF
        self.lockx = LOCK_XOFF
        self.wloc_start = self.wloc_end = None
        self.wrot_start = self.wrot_end = None
        self.lamp = None
        init_origin(self.scene)

        # set HUD to each user
        self.hudtext_left = self.make_hudtext(
            "hudTextLeft", (-0.15, 0.15, -0.5), str(self.mode))
        self.hudtext_right = self.make_hudtext(
            "hudTextRight", (0.1, 0.15, -0.5), "")
        self.hudtext_status = self.make_hudtext(
            "hudTextStatus", (0.02, -0.15, -0.5), "")  # workaround x=0 bad?

        # AR Control Panel
        self.follow_lock = False
        self.follow = Box(
            object_id=("follow_" + camname),
            parent=camname,
            material=Material(transparent=True, opacity=0),
            location=(0, 0, -PANEL_RADIUS * 0.1),
            scale=(0.1, 0.01, 0.1),
            rotation=(0.7, 0, 0, 0.7),
        )
        self.scene.add_object(self.follow)
        self.redpill = False
        self.panel = {}  # button dictionary
        followname = self.follow.object_id
        self.dbuttons = {}
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
            pbutton = Button(
                scene, camname, but[0], but[1], but[2], enable=but[3], btype=but[4],
                parent=followname, evt_handler=panel_callback)
            self.panel[pbutton.button.object_id] = pbutton

    def make_hudtext(self, label, location, text):
        return Text(
            object_id=(label + "_" + self.camname),
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
            self.lamp = Light(
                object_id=self.camname+"_lamp",
                parent=self.camname,
                color=(144, 144, 173),
                data='{"light":{"type":"point","intensity":"0.75"}}',
            )
            self.scene.add_object(self.lamp)
        elif self.lamp:
            self.scene.delete_object(self.lamp)

    def set_clipboard(self,
                      evt_handler=None,
                      object_type=Sphere()['data']['object_type'],
                      scale=(0.05, 0.05, 0.05),
                      location=(0, 0, -CLIP_RADIUS),
                      color=(255, 255, 255),
                      url=""):
        self.clipboard = Object(  # show item to be created
            object_id=(self.camname+"_clipboard"),
            object_type=object_type,
            location=location,
            color=color,
            parent=self.camname,
            scale=scale,
            material=Material(transparent=True, opacity=0.4),
            url=url,
            clickable=True,
            evt_handler=evt_handler)
        self.cliptarget = Circle(  # add helper target object to find true origin
            object_id=(self.camname+"_cliptarget"),
            location=location,
            parent=self.camname,
            scale=(0.005, 0.005, 0.005),
            material=Material(transparent=True, opacity=0.4),
            clickable=True,
            evt_handler=evt_handler)

    def del_clipboard(self):
        if self.cliptarget:
            self.scene.delete_object(self.cliptarget)
        if self.clipboard:
            self.scene.delete_object(self.clipboard)


class Button:
    def __init__(self, scene: Scene, camname, mode, x=0, y=0, label="", parent=None,
                 drop=None, color=CLR_BUTTON, enable=True, evt_handler=None,
                 btype=ButtonType.ACTION):
        self.scene = scene
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
        else:
            self.colorbut = CLR_BUTTON_DISABLED
        self.colortxt = CLR_BUTTON_TEXT
        if len(label) > 8:  # easier to read
            self.label = label[:6] + "..."
        else:
            self.label = label
        self.mode = mode
        self.dropdown = drop
        self.active = False
        if drop is None:
            obj_name = camname + "_button_" + mode.value
        else:
            obj_name = camname + "_button_" + mode.value + "_" + drop
        shape = Box()['data']['object_type']
        if btype == ButtonType.TOGGLE:
            shape = Cylinder()['data']['object_type']
            scale = (scale[0] / 2, scale[1], scale[2] / 2)
        self.button = Object(  # cube is main button
            object_id=obj_name,
            object_type=shape,
            parent=parent,
            material=Material(
                transparent=True,
                opacity=OPC_BUTTON,
                shader="flat"),
            location=(x * 1.1, PANEL_RADIUS, y * -1.1),
            scale=scale,
            color=self.colorbut,
            clickable=True,
            evt_handler=evt_handler,
        )
        scale = (1, 1, 1)
        if btype == ButtonType.TOGGLE:
            scale = (scale[0] * 2, scale[1] * 2, scale[2])
        self.text = Text(  # text child of button
            object_id=(self.button.object_id + "_text"),
            parent=self.button.object_id,
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
            self.button.update(color=CLR_BUTTON)
            self.text.update(color=self.colortxt)

    def set_hover(self, hover):
        if hover:
            opacity = OPC_BUTTON_HOVER
        else:
            opacity = OPC_BUTTON
        self.button.update(
            material=Material(
                transparent=True,
                opacity=opacity,
                shader="flat"))

    def delete(self):
        """Delete method so that child text object also gets deleted."""
        self.scene.delete_object(self.text)
        self.scene.delete_object(self.button)


class ObjectPersistence:
    """Converts persistence database object into python without using MQTT."""
    object_id = ""
    object_type = Box()['data']['object_type']
    location = (0, 0, 0)
    rotation = (0, 0, 0, 1)
    scale = (1, 1, 1)
    color = (255, 255, 255)
    color_material = None
    ttl = 0
    parent = ""
    persist = False
    physics = ""
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
        if "object_type" in jData["attributes"]:
            self.object_type = jData["attributes"]["object_type"]
        if "location" in jData["attributes"]:
            self.location = (jData["attributes"]["location"]["x"],
                             jData["attributes"]["location"]["y"],
                             jData["attributes"]["location"]["z"])
        if "rotation" in jData["attributes"]:
            self.rotation = (jData["attributes"]["rotation"]["x"],
                             jData["attributes"]["rotation"]["y"],
                             jData["attributes"]["rotation"]["z"],
                             jData["attributes"]["rotation"]["w"])
        if "scale" in jData["attributes"]:
            self.scale = (jData["attributes"]["scale"]["x"],
                          jData["attributes"]["scale"]["y"],
                          jData["attributes"]["scale"]["z"])
        if "color" in jData["attributes"]:
            self.color = arena_color2rgb(jData["attributes"]["color"])
        if "url" in jData["attributes"]:
            self.url = jData["attributes"]["url"]
        if "material" in jData["attributes"]:
            if "colorWrite" in jData["attributes"]["material"]:
                self.transparent_occlude = not jData["attributes"]["material"]["colorWrite"]
            if "color" in jData["attributes"]["material"]:
                self.color_material = arena_color2rgb(
                    jData["attributes"]["material"]["color"])
        if "parent" in jData["attributes"]:
            self.parent = jData["attributes"]["parent"]
        if "click-listener" in jData["attributes"]:
            self.clickable = True
        if "dynamic-body" in jData["attributes"]:
            if "type" in jData["attributes"]["dynamic-body"]:
                self.physics = Physics(
                    jData["attributes"]["dynamic-body"]["type"])
        # self.text self.transparency self.data self.ttl


def init_origin(scene: Scene):
    """Origin object, construction cone, so user knows ARB is running."""
    size = [0.2, 0.4, 0.2]
    scene.add_object(Cone(  # 370mm x 370mm # 750mm
        object_id="arb-origin",
        material=Material(
            transparent=True,
            opacity=0.5,
            shader="flat"),
        color=(255, 114, 33),
        location=(0, size[1] / 2, 0),
        scale=(size[0] / 2, size[1], size[2] / 2)))
    scene.add_object(Cone(
        object_id="arb-origin-hole",
        material=Material(
            colorWrite=False,
            # render-order=0, #TODO: resolve render-order
        ),
        location=(0, size[1] - (size[1] / 2 / 15), 0),
        scale=(size[0] / 15, size[1] / 10, size[2] / 15)))
    scene.add_object(Box(
        object_id="arb-origin-base",
        material=Material(
            transparent=True,
            opacity=0.5,
            shader="flat"),
        color=(0, 0, 0),
        location=(0, size[1] / 20, 0),
        scale=(size[0], size[1] / 10, size[2])))


def update_persisted_obj(scene: Scene, object_id, label,
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
    scene._publish(obj=msg, action=action)
    print(label + " " + object_id)


def opaque_obj(scene: Scene, object_id, opacity):
    data = {"material": {"transparent": True, "opacity": opacity}}
    update_persisted_obj(scene, object_id, "Opaqued", data=data)


def occlude_obj(scene: Scene, object_id, occlude):
    # NOTE: transparency does not allow occlusion so remove transparency here.
    data = {"material": {"colorWrite": occlude == BOOLS[1],
                         "transparent": False,
                         "opacity": 1},
            "render-order": 0}
    update_persisted_obj(scene, object_id, "Occluded", data=data)


def color_obj(scene: Scene, object_id, hcolor):
    # NOTE: "color" updates base color, NOT reflected live.
    # "material":{"color"} updates raw color, IS reflected live.
    data = {"color": "#" + hcolor, "material": {"color": "#" + hcolor}}
    update_persisted_obj(scene, object_id, "Colored", data=data)


def stretch_obj(scene: Scene, object_id, scale, location):
    data = {"scale": {
        "x": scale[0],
        "y": scale[1],
        "z": scale[2]
    }, "location": {
        "x": location[0],
        "y": location[1],
        "z": location[2]
    }}
    update_persisted_obj(scene, object_id, "Stretched", data=data)


def scale_obj(scene: Scene, object_id, scale):
    data = {"scale": {
        "x": scale[0],
        "y": scale[1],
        "z": scale[2]
    }}
    update_persisted_obj(scene, object_id, "Scaled", data=data)


def move_obj(scene: Scene, object_id, location):
    data = {"location": {
        "x": location[0],
        "y": location[1],
        "z": location[2]
    }}
    update_persisted_obj(scene, object_id, "locationed", data=data)


def rotate_obj(scene: Scene, object_id, rotation):
    data = {"rotation": {
        "x": rotation[0],
        "y": rotation[1],
        "z": rotation[2],
        "w": rotation[3]
    }}
    update_persisted_obj(scene, object_id, "Rotated", data=data)


def parent_obj(scene: Scene, object_id, parent_id):
    data = {"parent": parent_id}
    update_persisted_obj(scene, object_id,
                         parent_id + " adopted", data=data)


def delete_obj(scene: Scene, object_id):
    update_persisted_obj(scene, object_id, "Deleted", action="delete")


def rgb2hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])


def arena_color2rgb(color):
    color = color.lstrip('#')
    hexcolor = re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', color)
    if not hexcolor:
        wcrgb = webcolors.name_to_rgb(color)
        return (wcrgb.red, wcrgb.green, wcrgb.blue)
    return tuple(int(color[c:c + 2], 16) for c in (0, 2, 4))


def temp_loc_marker(location, color):
    return Sphere(ttl=120, color=color,
                  material=Material(transparent=True, opacity=0.5),
                  location=location, scale=(0.02, 0.02, 0.02), clickable=True)


def temp_rot_marker(location, rotation):
    return Box(ttl=120, rotation=rotation,
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
