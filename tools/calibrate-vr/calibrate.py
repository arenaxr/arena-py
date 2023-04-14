# calibrate.py
"""
A tool to calibrate the user's camera rig.
"""
from arena import *
import json
import time
import numpy as np
from scipy.spatial.transform import Rotation as spRotation

# Position Vector3 indices
X = 0
Y = 1
Z = 2

POSITION_INC = 0.01  # 1 cm

# 1 degree positive rotation on Y-axis
ROTATION_INC = [
    [0.9998477, 0.0000000, 0.0174524, 0],
    [0.0000000, 1.0000000, 0.0000000, 0],
    [-0.0174524, 0.0000000, 0.9998477, 0],
    [0, 0, 0, 1],
]

# 1 degree negative rotation on Y-axis
ROTATION_DEC = [
    [0.9998477, 0.0000000, -0.0174524, 0],
    [0.0000000, 1.0000000, 0.0000000, 0],
    [0.0174524, 0.0000000, 0.9998477, 0],
    [0, 0, 0, 1],
]

# 5 degree positive rotation on Y-axis
ROTATION_INC_BIG = [
    [0.9961947, 0.0000000, 0.0871557, 0],
    [0.0000000, 1.0000000, 0.0000000, 0],
    [-0.0871557, 0.0000000, 0.9961947, 0],
    [0, 0, 0, 1],
]

# 5 degree negative rotation on Y-axis
ROTATION_DEC_BIG = [
    [0.9961947, 0.0000000, -0.0871557, 0],
    [0.0000000, 1.0000000, 0.0000000, 0],
    [0.0871557, 0.0000000, 0.9961947, 0],
    [0, 0, 0, 1],
]

BIG_INC_THRESHOLD = 0.75  # seconds

persist = True

MARKER_SCALE = 0.15
OPC_ON = 0.85
OPC_OFF = 0.25
CONE_SCALE = Scale(MARKER_SCALE / 5, MARKER_SCALE / 5 * 2, MARKER_SCALE / 5)
calibrateparents = []
user_rigs = {}


def end_program_callback(_scene: Scene):
    remove_obj_onoff()
    remove_obj_calibrate()


# command line options
scene = Scene(cli_args=True, end_program_callback=end_program_callback)


def user_join_callback(_scene, cam, _msg):
    global user_rigs
    rig_matrix = np.identity(4)
    rig_pos = rig_matrix[:3, 3]
    rig_rot = rig_matrix[:3, :3]
    user_rigs[cam.object_id] = {
        "matrix": rig_matrix,
        "position": rig_pos,
        "rotation": rig_rot,
        "last_click": 0,
    }


def user_left_callback(_scene, cam, _msg):
    global user_rigs
    del user_rigs[cam.object_id]


@scene.run_once
def main():
    add_obj_onoff()
    scene.user_join_callback = user_join_callback
    scene.user_left_callback = user_left_callback


def add_obj_calibrate():
    global calibrateParent, calibrateparents, ground_plane, ground_plane_mask
    # parent scene object
    calibrateParent = Entity(
        persist=persist,
        object_id="calibrateParent",
        position=Position(0, 0.0, 0),
    )
    scene.add_object(calibrateParent)
    calibrateparents.append(calibrateParent)

    # marker gltf
    origin_marker = GLTF(
        persist=persist,
        object_id="origin-marker",
        parent=calibrateParent.object_id,
        url="/store/public/armarker.glb",
        rotation=Rotation(w=0.70711, x=-0.70711, y=0, z=0),
        scale=Scale(MARKER_SCALE, MARKER_SCALE, MARKER_SCALE),
    )
    scene.add_object(origin_marker)
    armarker = {
        "markerid": 0,
        "markertype": "apriltag_36h11",
        "size": 150,
        "buildable": False,
        "dynamic": False,
    }
    scene.update_object(origin_marker, armarker=armarker)
    add_axis("x")
    add_axis("y")
    add_axis("z")

    ground_plane = Plane(
        persist=persist,
        object_id="click-ground-plane",
        parent=calibrateParent.object_id,
        position=Position(0, -0.01, 0),
        rotation=Rotation(-90, 0, 0),
        width=10,
        height=10,
        material=Material(color=(128, 128, 128), opacity=OPC_OFF),
        clickable=True,
        evt_handler=ground_click_handler,
    )
    scene.add_object(ground_plane)

    ground_plane_mask = Plane(
        persist=persist,
        object_id="click-ground-plane-mask",
        parent=calibrateParent.object_id,
        position=Position(0, -0.00, 0),
        rotation=Rotation(-90, 0, 0),
        width=0.5,
        height=0.5,
        material=Material(color=(64, 64, 64), opacity=0.01),
        clickable=True,
    )
    scene.add_object(ground_plane_mask)


def remove_obj_calibrate():
    global calibrateparents
    # reverse parental order allows for branch to trunk deletion
    calibrateparents.reverse()
    for parent in calibrateparents:
        scene.delete_object(parent)
    scene.delete_object(ground_plane)
    scene.delete_object(ground_plane_mask)


def add_obj_onoff():
    global onoffParent
    # parent scene object
    onoffParent = Entity(
        persist=persist,
        object_id="onoffParent",
        position=Position(0, 0, -1),
    )
    scene.add_object(onoffParent)

    scene.add_object(
        Cylinder(
            persist=persist,
            object_id="button-off",
            parent=onoffParent.object_id,
            position=Position(0.5, 0, 0),
            height=0.5,
            radius=0.25,
            segmentsRadial=8,
            material=Material(color=Color(255, 0, 0)),
            clickable=True,
            evt_handler=off_handler,
        )
    )
    scene.add_object(
        Cone(
            persist=persist,
            object_id="button-on",
            parent=onoffParent.object_id,
            position=Position(-0.5, 0, 0),
            rotation=Rotation(90, 0, 0),
            scale=Scale(0.1, 0.5, 0.1),
            material=Material(color=Color(0, 0, 255)),
            clickable=True,
            evt_handler=on_handler,
        )
    )


def remove_obj_onoff():
    global onoffParent
    scene.delete_object(onoffParent)


def on_handler(_scene, evt, _msg):
    if evt.type == "mousedown":
        add_obj_calibrate()


def off_handler(_scene, evt, _msg):
    if evt.type == "mousedown":
        remove_obj_calibrate()


def get_color(axis):
    if axis == "x":
        return Color(0, 255, 0)
    elif axis == "y":
        return Color(0, 0, 255)
    elif axis == "z":
        return Color(255, 0, 0)


def add_axis(axis):
    global calibrateParent
    if axis == "x":
        position = Position(MARKER_SCALE / 2, 0, 0)
        rotation = Rotation(0, 90, -90)
    elif axis == "y":
        position = Position(0, MARKER_SCALE / 2, 0)
        rotation = Rotation(0, 0, 0)
    elif axis == "z":
        position = Position(0, 0, MARKER_SCALE / 2)
        rotation = Rotation(90, 0, 0)
    # click root
    click = Entity(
        persist=persist,
        object_id=f"click-{axis}",
        parent=calibrateParent.object_id,
        rotation=rotation,
        position=position,
    )
    scene.add_object(click)
    calibrateparents.append(click)

    # position we don't apply to y-axis
    if axis != "y":
        add_position_clicks(click.object_id, axis, "pos")
        add_position_clicks(click.object_id, axis, "neg")
    # rotation, we ONLY apply to y-axis
    if axis == "y":
        add_rotation_clicks(click.object_id, axis, "pos")
        add_rotation_clicks(click.object_id, axis, "neg")


def add_position_clicks(parent, axis, direction):
    py = 1 if direction == "pos" else -1
    py2 = 1 if direction == "pos" else -3
    rx = 0 if direction == "pos" else 180
    scene.add_object(
        Cone(
            persist=persist,
            object_id=f"click-position-{axis}-{direction}",
            parent=parent,
            scale=CONE_SCALE,
            rotation=Rotation(rx, 0, 0),
            position=Position(0, (py2 * MARKER_SCALE / 2) + (py * MARKER_SCALE / 5), 0),
            material=Material(color=get_color(axis), opacity=OPC_OFF),
            clickable=True,
            evt_handler=mouse_handler,
        )
    )


def add_rotation_clicks(parent, axis, direction):
    x = 1 if direction == "pos" else -1
    scene.add_object(
        Cone(
            persist=persist,
            object_id=f"click-rotation-{axis}-{direction}",
            parent=parent,
            scale=CONE_SCALE,
            rotation=Rotation(x * 90, 0, 0),
            position=Position(x * MARKER_SCALE / 5, 0, 0),
            material=Material(color=get_color(axis), opacity=OPC_OFF),
            clickable=True,
            evt_handler=mouse_handler,
        )
    )


def mouse_handler(_scene, evt, _msg):
    obj = scene.all_objects[evt.object_id]
    parts = evt.object_id.split("-")
    attribute = parts[1]
    axis = parts[2]
    direction = parts[3]
    if evt.type == "mouseenter":
        scene.update_object(
            obj, material=Material(color=get_color(axis), opacity=OPC_ON)
        )
    elif evt.type == "mouseleave":
        scene.update_object(
            obj, material=Material(color=get_color(axis), opacity=OPC_OFF)
        )
    elif evt.type == "mousedown":
        if attribute == "position":
            camera_position_updater(evt.data.source, axis, direction)
        elif attribute == "rotation":
            camera_rotation_updater(evt.data.source, axis, direction)


def publish_rig_offset(user_id):
    global user_rigs
    rig = user_rigs.get(user_id)
    obj_topic = f"{scene.root_topic}/{user_id}"
    if rig:
        rotation_matrix = spRotation.from_matrix(rig["rotation"])
        qw, qx, qy, qz = rotation_matrix.as_quat()
        msg = {
            "object_id": user_id,
            "type": "rig",
            "action": "update",
            "data": {
                "position": {
                    "x": rig["position"][X],
                    "y": rig["position"][Y],
                    "z": rig["position"][Z],
                },
                "rotation": {
                    "x": qx,
                    "y": qy,
                    "z": qz,
                    "w": qw,
                },
            },
        }
        scene.mqttc.publish(obj_topic, json.dumps(msg))


def ground_click_handler(_scene, evt, _msg):
    """
    This handles clicks on the ground plane which indicate that a user is starting
    fairly far off from the origin marker. We ignore rotation completely and simply
    apply an initial inverse translation of x and z to the camera offset rig matrix,
    (since y is assumed always to be 0).
    """
    if evt.type != "mousedown":
        return
    global user_rigs
    rig = user_rigs.get(evt.data.source)
    prev_rig_pos = rig["position"]
    new_x = prev_rig_pos[X] - evt.data.position.x
    new_z = prev_rig_pos[Z] - evt.data.position.z
    rig["position"][X] = new_x
    rig["position"][Z] = new_z
    # print(f'Ground click: {evt.data.clickPos.x}, {evt.data.clickPos.z}')
    publish_rig_offset(evt.data.source)


def camera_position_updater(cam_id, axis, direction):
    """
    We use this to nudge position of camera offset rig. Bearing in mind that the rig
    offset is what is actually being modified, we once again apply the inverse value.
    We shouldn't be nudging y position, but we'll leave that code in for now.
    """
    # print(f'Camera position updater: {cam_id}, {axis}, {direction}')
    global user_rigs
    rig = user_rigs.get(cam_id)
    if axis == "x":
        rig["position"][X] += -POSITION_INC if direction == "pos" else POSITION_INC
    elif axis == "y":
        rig["position"][Y] += -POSITION_INC if direction == "pos" else POSITION_INC
    elif axis == "z":
        rig["position"][Z] += -POSITION_INC if direction == "pos" else POSITION_INC
    publish_rig_offset(cam_id)


def camera_rotation_updater(cam_id, axis, direction):
    """
    We use this to nudge rotation of camera offset rig. Bearing in mind that the rig
    offset is what is actually being modified, we once again apply the inverse value.
    We shouldn't be nudging x or z rotation, but we'll leave it in for now.
    We apply this nudge by multiplying by either a small or slightly larger rotated
    matrix (previously calculated) to the entire rig pose matrix.
    """
    # print(f'Camera rotation updater: {cam_id}, {axis}, {direction}')
    if axis != "y":
        return
    global user_rigs
    rig = user_rigs.get(cam_id)
    now = time.time()
    inc = (
        ROTATION_INC_BIG
        if (now - rig["last_click"]) < BIG_INC_THRESHOLD
        else ROTATION_INC
    )
    dec = (
        ROTATION_DEC_BIG
        if (now - rig["last_click"]) < BIG_INC_THRESHOLD
        else ROTATION_DEC
    )
    rig["last_click"] = now
    rig["matrix"] = rig["matrix"] @ dec if direction == "pos" else inc
    publish_rig_offset(cam_id)


scene.run_tasks()
