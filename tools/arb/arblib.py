# arblib.py
#
# AR Builder Library
# Utility classes and methods for AR Builder.

# pylint: disable=missing-docstring

import enum
import math

from arena import (
    Box,
    Circle,
    Color,
    Cone,
    Cylinder,
    Dodecahedron,
    Icosahedron,
    Light,
    Material,
    Object,
    Octahedron,
    Plane,
    Position,
    Ring,
    Rotation,
    Scale,
    Scene,
    Sphere,
    Tetrahedron,
    Text,
    Torus,
    TorusKnot,
    Triangle,
)

ARB_PARENT_ID = "arb-origin-parent"
CLICKLINE_LEN_OBJ = 0.5  # meters
CLICKLINE_LEN_MOD = 0.5  # meters
CLICKLINE_SCL = Scale(1, 1, 1)  # meters
FLOOR_Y = 0.1  # meters
GRIDLEN = 20  # meters
SCL_HUD = 0.1  # meters
SCL_CLICK = 0.1  # meters — root scale for click control objects
PANEL_RADIUS = 1  # meters
CLIP_RADIUS = PANEL_RADIUS + 0.25  # meters
BUTTON_SPACING = 1.1  # multiplier for button grid spacing

# Colors
CLR_HUDTEXT = Color(128, 128, 128)  # gray
CLR_NUDGE = Color(255, 255, 0)  # yellow
CLR_SCALE = Color(0, 0, 255)  # blue
CLR_STRETCH = Color(255, 0, 0)  # red
CLR_ROTATE = Color(255, 165, 0)  # orange
CLR_SELECT = Color(255, 255, 0)  # yellow
CLR_GRID = Color(0, 255, 0)  # green
CLR_BUTTON = Color(200, 200, 200)  # white-ish
CLR_BUTTON_DISABLED = Color(128, 128, 128)  # gray
CLR_BUTTON_TEXT = Color(0, 0, 0)  # black
CLR_WALL_START = Color(255, 0, 0)  # red
CLR_WALL_END = Color(0, 255, 0)  # green
CLR_WALL_CENTER = Color(0, 0, 255)  # blue
CLR_WALL = Color(200, 200, 200)  # white-ish
CLR_ORIGIN = Color(255, 114, 33)  # safety-cone orange
CLR_ORIGIN_BASE = Color(0, 0, 0)  # black
CLR_LAMP = Color(144, 144, 173)  # pale blue-gray
CLR_WHITE = Color(255, 255, 255)  # white

# Opacity values
OPC_BUTTON = 0.1
OPC_BUTTON_HOVER = 0.25
OPC_CLINE = 0.1
OPC_CLINE_HOVER = 0.9
OPC_OVERLAY = 0.4  # clickline boxes, clipboard, followspot, cliptarget
OPC_TRANSLUCENT = 0.5  # redpill wrappers, walls, origin cone, markers

# Scale/position constants for HUD elements
SCL_CLIPBOARD = Scale(0.05, 0.05, 0.05)  # meters
SCL_CLIPTARGET = 0.005  # meters — tiny helper target circle
SCL_HUDTEXT = 0.1  # meters — HUD text element scale
POS_HUDTEXT_LEFT = Position(-0.15, 0.15, -0.5)
POS_HUDTEXT_RIGHT = Position(0.1, 0.15, -0.5)
POS_HUDTEXT_STATUS = Position(0.02, -0.15, -0.5)  # workaround: x=0 renders incorrectly
SCL_FOLLOW = Scale(0.1, 0.01, 0.1)
SCL_BUTTON = Scale(0.1, 0.1, 0.01)

# Clickline cone dimensions
SCL_CONE_RADIUS = 0.05  # meters — clickline direction cone radius
SCL_CONE_HEIGHT = 0.09  # meters — clickline direction cone height
CONE_OFFSET = 0.1  # meters — offset for negative direction cone
CLICKLINE_WIDTH = 0.005  # meters

# Wall marker/temp object constants
TTL_TEMP = 30  # seconds
TTL_MARKER = 120  # seconds
SCL_LOC_MARKER = 0.02  # meters — wall location marker sphere
SCL_ROT_MARKER = Scale(0.02, 0.01, 0.15)  # wall rotation marker box

# Origin cone dimensions (construction cone visual indicator)
ORIGIN_SIZE = [0.2, 0.4, 0.2]  # [width, height, depth] in meters
LAMP_INTENSITY = 0.75

# Quaternion values for axis-aligned rotations
# 0.7 ≈ sin(π/4) ≈ cos(π/4), representing 90° rotations
QUAT_VEC_RGTS = [-1, -0.7, -0.5, 0, 0.5, 0.7, 1]
QUAT_DEV_RGT = 0.075
# Rotation to face downward (x-axis 90°)
ROT_FACE_DOWN = Rotation(-0.7, 0, 0, 0.7)
# Rotation to face upward (x-axis 90°, for follow panel)
ROT_FACE_UP = Rotation(0.7, 0, 0, 0.7)
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
SHAPES = [Sphere.object_type,
          Box.object_type,
          Cone.object_type,
          Cylinder.object_type,
          Dodecahedron.object_type,
          Icosahedron.object_type,
          Octahedron.object_type,
          Tetrahedron.object_type,
          Torus.object_type,
          TorusKnot.object_type,
          Circle.object_type,
          Plane.object_type,
          Ring.object_type,
          Triangle.object_type]
DEF_MANIFEST = [{  # default model, if none loaded
    "name": "duck",
    "url_gltf": "store/models/Duck.glb",
    "scale": 0.1
}]
EVT_MOUSEENTER = "mouseenter"
EVT_MOUSELEAVE = "mouseleave"
EVT_MOUSEDOWN = "mousedown"
EVT_MOUSEUP = "mouseup"


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
    SLIDER = "slider"
    EDIT = "edit"


class ButtonType(enum.Enum):
    ACTION = "action"
    TOGGLE = "toggle"


class User:
    def __init__(self, scene: Scene, camname, panel_callback, userid=None):
        self.scene = scene
        self.camname = camname
        self.userid = userid  # MQTT identity for private channel routing
        self.mode = Mode.NONE
        self.clipboard = self.cliptarget = None
        self.target_id = self.target_control_id = None
        self.position = self.rotation = None
        self.position_last = self.rotation_last = None
        self.gesturing = False
        self.target_style = self.typetext = ""
        self.lock_rx = 0
        self.lock_ry = 0
        self.wloc_start = self.wloc_end = None
        self.wrot_start = self.wrot_end = None
        self.lamp = None
        self.redpill_objects = []  # track per-user redpill objects for cleanup
        init_origin(self.scene)

        # set HUD to each user (private to this user)
        self.hud = Object(
            object_id=f"hud_{camname}",
            parent=camname,
            position=Position(0, 0, 0),
            scale=Scale(SCL_HUD, SCL_HUD, SCL_HUD),
            rotation=Rotation(0, 0, 0, 1),
            private_userid=userid,
        )
        self.scene.add_object(self.hud)
        self.hudtext_left = self.make_hudtext(
            "hudTextLeft", POS_HUDTEXT_LEFT, str(self.mode))
        self.hudtext_right = self.make_hudtext(
            "hudTextRight", POS_HUDTEXT_RIGHT, "")
        self.hudtext_status = self.make_hudtext(
            "hudTextStatus", POS_HUDTEXT_STATUS, "")

        # AR Control Panel (private to this user)
        self.follow_lock = False
        self.follow = Object(
            object_id=f"follow_{camname}",
            parent=camname,
            position=Position(0, 0, -PANEL_RADIUS * SCL_HUD),
            scale=SCL_FOLLOW,
            rotation=ROT_FACE_UP,
            private_userid=userid,
        )
        self.scene.add_object(self.follow)
        self.redpill = False
        self.slider = False
        self.panel = {}  # button dictionary
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
            [Mode.EDIT, 3, 0, True, ButtonType.TOGGLE],
            # bottom row
            [Mode.WALL, -2, -1, True, ButtonType.ACTION],
            [Mode.OCCLUDE, -1, -1, True, ButtonType.ACTION],
            [Mode.RENAME, 0, -1, True, ButtonType.ACTION],
            [Mode.COLOR, 1, -1, True, ButtonType.ACTION],
            [Mode.LAMP, 2, -1, True, ButtonType.TOGGLE],
            [Mode.SLIDER, 3, -1, False, ButtonType.TOGGLE],  # TODO: adjust scale
        ]
        for but in buttons:
            pbutton = Button(
                scene, camname, but[0], but[1], but[2], enable=but[3], btype=but[4],
                parent=self.follow.object_id, callback=panel_callback,
                private_userid=userid)
            self.panel[pbutton.button.object_id] = pbutton

        # set panel state from scene-options
        self.scene_options = None
        options = scene.get_persisted_scene_option()
        if options:
            self.scene_options = options[0]
            if "attributes" in self.scene_options:
                self.panel[f"{camname}_button_{Mode.EDIT.value}"].set_active(
                    not self.scene_options["attributes"]["scene-options"]["clickableOnlyEvents"])

    def make_hudtext(self, label, position, text):
        text = Text(
            object_id=f"{label}_{self.camname}",
            parent=self.hud.object_id,
            value=text,
            position=Position(position.x/SCL_HUD,
                              position.y/SCL_HUD,
                              position.z/SCL_HUD),
            color=CLR_HUDTEXT,
            scale=Scale(SCL_HUDTEXT/SCL_HUD, SCL_HUDTEXT/SCL_HUD, SCL_HUDTEXT/SCL_HUD),
            private_userid=self.userid,
        )
        self.scene.add_object(text)
        return text

    def set_textleft(self, mode):
        self.scene.update_object(self.hudtext_left, value=str(mode))

    def set_textright(self, text, color=CLR_HUDTEXT):
        self.scene.update_object(self.hudtext_right, value=text, color=color)

    def set_textstatus(self, text):
        self.scene.update_object(self.hudtext_status, value=text)

    def set_lamp(self, enabled):
        if enabled:
            self.lamp = Light(
                object_id=f"{self.camname}_lamp",
                parent=self.hud.object_id,
                material=Material(color=CLR_LAMP),
                type="point",
                intensity=LAMP_INTENSITY,
                private_userid=self.userid)
            self.scene.add_object(self.lamp)
        elif self.lamp:
            self.scene.delete_object(self.lamp)

    def set_clipboard(self,
                      callback=None,
                      object_type=None,
                      scale=SCL_CLIPBOARD,
                      position=Position(0, 0, -CLIP_RADIUS/SCL_HUD),
                      color=CLR_WHITE,
                      url=None):
        if object_type:
            self.clipboard = Object(  # show item to be created
                object_id=f"{self.camname}_clipboard",
                object_type=object_type,
                position=position,
                parent=self.hud.object_id,
                scale=Scale(scale.x/SCL_HUD, scale.y/SCL_HUD, scale.z/SCL_HUD),
                material=Material(color=color, transparent=True, opacity=OPC_OVERLAY),
                url=url,
                clickable=True,
                evt_handler=callback,
                private_userid=self.userid)
            self.scene.add_object(self.clipboard)
        self.cliptarget = Circle(  # add helper target object to find true origin
            object_id=f"{self.camname}_cliptarget",
            position=position,
            parent=self.hud.object_id,
            scale=Scale(SCL_CLIPTARGET/SCL_HUD, SCL_CLIPTARGET/SCL_HUD, SCL_CLIPTARGET/SCL_HUD),
            material=Material(color=CLR_WHITE,
                              transparent=True, opacity=OPC_OVERLAY),
            clickable=True,
            evt_handler=callback,
            private_userid=self.userid)
        self.scene.add_object(self.cliptarget)

    def get_clipboard(self):
        obj_actual = self.clipboard
        obj_actual.data.scale = Scale(
            self.clipboard.data.scale.x*SCL_HUD,
            self.clipboard.data.scale.y*SCL_HUD,
            self.clipboard.data.scale.z*SCL_HUD)
        return obj_actual

    def del_clipboard(self):
        if self.cliptarget and self.cliptarget.object_id in self.scene.all_objects:
            self.scene.delete_object(self.cliptarget)
        if self.clipboard and self.clipboard.object_id in self.scene.all_objects:
            self.scene.delete_object(self.clipboard)

    def delete(self):
        self.scene.delete_object(self.hud)
        self.scene.delete_object(self.follow)

    def set_clickableOnlyEvents(self, edit_on):
        if self.scene_options:
            object_id = self.scene_options["object_id"]
        else:
            object_id = 'scene-options'
        opt_obj = Object(object_id=object_id, persist=True)
        opt_obj.type = 'scene-options'
        del opt_obj.data.object_type
        opt_obj.data['scene-options'] = {
            "clickableOnlyEvents": not edit_on
        }
        if self.scene_options:
            self.scene.update_object(opt_obj)
        else:
            self.scene.add_object(opt_obj)
            self.scene_options = opt_obj.__dict__


class Button:
    def __init__(self, scene: Scene, camname, mode, x=0, y=0, label="", parent=None,
                 drop=None, color=CLR_BUTTON, enable=True, callback=None,
                 btype=ButtonType.ACTION, private_userid=None):
        self.scene = scene
        self.private_userid = private_userid
        if label == "":
            label = mode.value
        if parent is None:
            parent = camname
            scale = SCL_BUTTON
        else:
            scale = Scale(1, 1, 1)
        self.type = btype
        self.enabled = enable
        if enable:
            self.colorbut = color
        else:
            self.colorbut = CLR_BUTTON_DISABLED
        self.colortxt = CLR_BUTTON_TEXT
        if len(label) > 8:  # easier to read
            self.label = f"{label[:6]}..."
        else:
            self.label = label
        self.mode = mode
        self.dropdown = drop
        self.active = False
        if drop is None:
            obj_name = f"{camname}_button_{mode.value}"
        else:
            obj_name = f"{camname}_button_{mode.value}_{drop}"
        shape = Box.object_type
        if btype == ButtonType.TOGGLE:
            shape = Cylinder.object_type
            scale = Scale(scale.x / 2, scale.y, scale.z / 2)
        self.button = Object(  # box is main button
            object_id=obj_name,
            object_type=shape,
            parent=parent,
            material=Material(
                color=self.colorbut,
                transparent=True,
                opacity=OPC_BUTTON,
                shader="flat"),
            position=Position(x * BUTTON_SPACING, PANEL_RADIUS, y * -BUTTON_SPACING),
            scale=scale,
            clickable=True,
            evt_handler=callback,
            private_userid=private_userid,
        )
        scene.add_object(self.button)
        scale = Scale(1, 1, 1)
        if btype == ButtonType.TOGGLE:
            scale = Scale(scale.x * 2, scale.y * 2, scale.z)
        self.text = Text(  # text child of button
            object_id=f"{self.button.object_id}_text",
            parent=self.button.object_id,
            value=self.label,
            # position inside to prevent ray events
            position=Position(0, -0.1, 0),
            rotation=ROT_FACE_DOWN,
            scale=scale,
            color=self.colortxt,
            private_userid=private_userid,
        )
        scene.add_object(self.text)

    def set_active(self, active):
        self.active = active
        if active:
            self.scene.update_object(
                self.button, material=Material(color=CLR_SELECT))
        else:
            self.scene.update_object(
                self.button, material=Material(color=CLR_BUTTON))
            self.scene.update_object(
                self.text, material=Material(color=self.colortxt))

    def set_hover(self, hover):
        if hover:
            opacity = OPC_BUTTON_HOVER
        else:
            opacity = OPC_BUTTON
        self.scene.update_object(
            self.button,
            material=Material(transparent=True, opacity=opacity, shader="flat"))

    def delete(self):
        """Delete method so that child text object also gets deleted."""
        self.scene.delete_object(self.text)
        self.scene.delete_object(self.button)


def init_origin(scene: Scene):
    """Origin object, construction cone, so user knows ARB is running."""
    size = ORIGIN_SIZE
    scene.add_object(Object(
        object_id=ARB_PARENT_ID,
        position=scene.args["position"],
        rotation=scene.args["rotation"],
        scale=scene.args["scale"],
    ))
    scene.add_object(Cone(  # 370mm x 370mm # 750mm
        object_id="arb-origin",
        parent=ARB_PARENT_ID,
        material=Material(
            color=CLR_ORIGIN,
            transparent=True,
            opacity=OPC_TRANSLUCENT,
            shader="flat"),
        position=Position(0, size[1] / 2, 0),
        scale=Scale(size[0] / 2, size[1], size[2] / 2)))
    scene.add_object(Cone(
        object_id="arb-origin-hole",
        parent=ARB_PARENT_ID,
        **{"material-extras": {"transparentOccluder": True}},
        position=Position(0, size[1] - (size[1] / 2 / 15), 0),
        scale=Scale(size[0] / 15, size[1] / 10, size[2] / 15)))
    scene.add_object(Box(
        object_id="arb-origin-base",
        parent=ARB_PARENT_ID,
        material=Material(
            color=CLR_ORIGIN_BASE,
            transparent=True,
            opacity=OPC_TRANSLUCENT,
            shader="flat"),
        position=Position(0, size[1] / 20, 0),
        scale=Scale(size[0], size[1] / 10, size[2])))


def opaque_obj(scene: Scene, object_id, opacity):
    if object_id in scene.all_objects:
        scene.update_object(scene.all_objects[object_id],
                            material=Material(transparent=True, opacity=opacity))
        print(f"Opaqued {object_id}")


def occlude_obj(scene: Scene, object_id, occlude):
    if object_id in scene.all_objects:
        # NOTE: transparency does not allow occlusion so remove transparency here.
        scene.update_object(scene.all_objects[object_id],
                            **{"material-extras": {"transparentOccluder": (occlude != BOOLS[1])}},
                            # material=Material(transparent=False, opacity=1)
                            )
        print(f"Occluded {object_id}")


def color_obj(scene: Scene, object_id, color):
    if object_id in scene.all_objects:
        obj = scene.all_objects[object_id]
        if "color" in obj.data and obj.data.color is not None:
            obj.data.color = None  # remove legacy
        scene.update_object(obj, material=Material(color=color))
        print(f"Colored {object_id}")


def stretch_obj(scene: Scene, object_id, scale, position):
    if object_id in scene.all_objects:
        scene.update_object(
            scene.all_objects[object_id], scale=scale, position=position)
        print(f"Stretched {object_id}")


def scale_obj(scene: Scene, object_id, scale):
    if object_id in scene.all_objects:
        scene.update_object(scene.all_objects[object_id], scale=scale)
        print(f"Scaled {object_id}")


def move_obj(scene: Scene, object_id, position):
    if object_id in scene.all_objects:
        scene.update_object(scene.all_objects[object_id], position=position)
        print(f"Relocated {object_id}")


def rotate_obj(scene: Scene, object_id, rotation):
    if object_id in scene.all_objects:
        scene.update_object(scene.all_objects[object_id], rotation=rotation)
        print(f"Rotated {object_id}")


def parent_obj(scene: Scene, object_id, parent_id):
    if object_id in scene.all_objects:
        scene.update_object(scene.all_objects[object_id], parent=parent_id)
        print(f"{parent_id} adopted {object_id}")


def delete_obj(scene: Scene, object_id):
    if object_id in scene.all_objects:
        scene.delete_object(scene.all_objects[object_id])
        print(f"Deleted {object_id}")


def temp_loc_marker(position, color):
    return Sphere(ttl=TTL_MARKER, material=Material(color=color, transparent=True, opacity=OPC_TRANSLUCENT),
                  position=position, scale=Scale(SCL_LOC_MARKER, SCL_LOC_MARKER, SCL_LOC_MARKER))


def temp_rot_marker(position, rotation):
    return Box(ttl=TTL_MARKER, rotation=rotation, material=Material(color=CLR_WHITE),
               position=position, scale=SCL_ROT_MARKER)


def rotation_quat2radian(quat):
    e = Rotation.q2e(quat)
    return (math.radians(e[0]),
            math.radians(e[1]),
            math.radians(e[2]))


def rotation_quat2euler(quat):
    return Rotation.q2e(quat)


def rotation_euler2quat(euler):
    return Rotation.e2q(euler)


def probable_quat(num):
    # if reasonably close to 90 deg, align to right angle quaternion
    lst = QUAT_VEC_RGTS
    closest = lst[min(range(len(lst)), key=lambda i: abs(lst[i] - num))]
    if abs(num - closest) < QUAT_DEV_RGT:
        return closest
    return num
