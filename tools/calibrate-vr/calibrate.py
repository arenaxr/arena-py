# calibrate.py
"""
A tool to calibrate the user's camera rig.
"""
from arena import *
import json
import os
import time
import numpy as np

env_axis = os.environ.get("FULL_AXIS")
fullAxis = bool(env_axis) if env_axis is not None else False

# Position Vector3 indices
X = 0
Y = 1
Z = 2

POSITION_INC = 0.01  # 1 cm

BIG_INC_THRESHOLD = 0.5  # seconds

persist = True

MARKER_SCALE = 0.15
OPC_ON = 0.85
OPC_OFF = 0.25
CONE_SCALE = Scale(MARKER_SCALE / 5, MARKER_SCALE / 5 * 2, MARKER_SCALE / 5)
calibrateparents = []
user_rigs = {}


def create_rot_matrix(angle_deg, axis):
    """
    Create a pose matrix representing a rotation about a given axis.
    Generated by ChatGPT-4, we make no assumptions about its correctness.

    Args:
        angle_deg (float): Rotation angle in degrees.
        axis (str): Axis to rotate about, must be one of 'X', 'Y', or 'Z'.

    Returns:
        numpy.ndarray: 4x4 pose matrix representing the rotation.
    """
    # Convert angle from degrees to radians
    angle_rad = np.deg2rad(angle_deg)

    # Define the rotation matrix based on the specified axis
    if axis == "x":
        rotation_matrix = np.array(
            [
                [1, 0, 0, 0],
                [0, np.cos(angle_rad), -np.sin(angle_rad), 0],
                [0, np.sin(angle_rad), np.cos(angle_rad), 0],
                [0, 0, 0, 1],
            ]
        )
    elif axis == "y":
        rotation_matrix = np.array(
            [
                [np.cos(angle_rad), 0, np.sin(angle_rad), 0],
                [0, 1, 0, 0],
                [-np.sin(angle_rad), 0, np.cos(angle_rad), 0],
                [0, 0, 0, 1],
            ]
        )
    elif axis == "z":
        rotation_matrix = np.array(
            [
                [np.cos(angle_rad), -np.sin(angle_rad), 0, 0],
                [np.sin(angle_rad), np.cos(angle_rad), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        )
    else:
        raise ValueError("Invalid axis. Must be one of 'X', 'Y', or 'Z'.")

    return rotation_matrix


ROTATIONS = {
    "x": {
        "pos": {
            1: create_rot_matrix(-1, "x"),
            5: create_rot_matrix(-5, "x"),
        },
        "neg": {
            1: create_rot_matrix(1, "x"),
            5: create_rot_matrix(5, "x"),
        },
    },
    "y": {
        "pos": {
            1: create_rot_matrix(-1, "y"),
            5: create_rot_matrix(-5, "y"),
        },
        "neg": {
            1: create_rot_matrix(1, "y"),
            5: create_rot_matrix(5, "y"),
        },
    },
    "z": {
        "pos": {
            1: create_rot_matrix(-1, "z"),
            5: create_rot_matrix(-5, "z"),
        },
        "neg": {
            1: create_rot_matrix(1, "z"),
            5: create_rot_matrix(5, "z"),
        },
    },
}


def end_program_callback(_scene: Scene):
    remove_obj_onoff()
    remove_obj_calibrate()


# command line options
scene = Scene(cli_args=True, end_program_callback=end_program_callback)

onoffParent = None
calibrateParent = None
ground_plane = None
ground_plane_mask = None


def user_left_callback(_scene, cam, _msg):
    global user_rigs
    if cam.object_id in user_rigs:
        del user_rigs[cam.object_id]


@scene.run_once
def main():
    add_obj_onoff()
    add_obj_calibrate()
    scene.user_left_callback = user_left_callback


def add_obj_calibrate():
    global calibrateParent, calibrateparents, ground_plane, ground_plane_mask
    # parent scene object
    calibrateParent = Object(
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
        material=Material(color=(0, 0, 0), opacity=0),
        clickable=True,
        evt_handler=ground_click_handler,
    )
    scene.add_object(ground_plane)
    calibrateparents.append(ground_plane)

    ground_plane_mask = Plane(
        persist=persist,
        object_id="click-ground-plane-mask",
        parent=calibrateParent.object_id,
        position=Position(0, -0.00, 0),
        rotation=Rotation(-90, 0, 0),
        width=0.75,
        height=0.75,
        material=Material(color=(0, 0, 0), opacity=0),
        clickable=True,
    )
    scene.add_object(ground_plane_mask)
    calibrateparents.append(ground_plane_mask)


def remove_obj_calibrate():
    global calibrateparents
    # reverse parental order allows for branch to trunk deletion
    if calibrateparents is not None:
        calibrateparents.reverse()
        for parent in calibrateparents:
            if parent.object_id in scene.all_objects:
                scene.delete_object(parent)


def add_obj_onoff():
    global onoffParent
    # parent scene object
    onoffParent = Object(
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
            position=Position(0.25, 0, 0),
            rotation=Rotation(0, 360 / 16, 0),
            height=0.1,
            radius=0.2,
            segmentsRadial=8,
            material=Material(color=Color(255, 0, 0)),
            clickable=True,
            evt_handler=off_handler,
        )
    )
    scene.add_object(
        Cylinder(
            persist=persist,
            object_id="button-on",
            parent=onoffParent.object_id,
            position=Position(-0.25, 0, 0),
            rotation=Rotation(0, -90, 0),
            height=0.1,
            radius=0.25,
            segmentsRadial=3,
            material=Material(color=Color(0, 255, 0)),
            clickable=True,
            evt_handler=on_handler,
        )
    )


def remove_obj_onoff():
    global onoffParent
    scene.delete_object(onoffParent)


def on_handler(_scene, evt, _msg):
    global user_rigs
    if evt.type == "mousedown":
        rig_matrix = np.identity(4)
        rig_pos = rig_matrix[:3, 3]
        rig_rot = rig_matrix[:3, :3]

        # Before setting up rig, check if exists
        prev_rig = user_rigs.get(evt.data.source)
        user_rigs[evt.data.source] = {
            "matrix": rig_matrix,
            "position": rig_pos,
            "rotation": rig_rot,
            "last_click": 0,
            "enabled": True,
        }
        if prev_rig is None:
            # This is a new rig to program. Just in case a previous rig existed,
            # such as one from a persistent anchor, just reset it to identity.
            publish_rig_offset(evt.data.source)

        # add_light()


def off_handler(_scene, evt, _msg):
    if evt.type == "mousedown":
        rig = user_rigs.get(evt.data.source)
        if rig is None:
            return
        rig["enabled"] = False


def get_color(axis):
    if axis == "x":
        return Color(0, 255, 0)
    elif axis == "y":
        return Color(0, 0, 255)
    elif axis == "z":
        return Color(255, 0, 0)


def add_light():
    global calibrateParent, calibrate_cone
    calibrate_cone = Cone(
        persist=persist,
        object_id="calibrate_cone",
        parent=calibrateParent.object_id,
        rotation=Rotation(0, 0, 0),
        position=Position(0, 3, 0),
        radiusBottom=0.1,
        height=0.2,
        material=Material(color=Color(255, 165, 0), opacity=0.75),
    )
    scene.add_object(calibrate_cone)
    animation = {
        "dur": 1000,
        "autoplay": True,
        "to": "0",
        "from": "360",
        "loop": True,
        "property": "rotation.x",
        "easing": "linear",
        "dir": "normal",
    }
    scene.update_object(calibrate_cone, animation=animation)

    calibrate_light = Light(
        persist=persist,
        object_id="calibrate_light",
        parent=calibrate_cone.object_id,
        rotation=Rotation(-90, 0, 0),
        color=Color(255, 165, 0),
        type="spot",
    )
    scene.add_object(calibrate_light)


def remove_light():
    global calibrate_cone
    scene.delete_object(calibrate_cone)


def add_axis(axis):
    global calibrateParent
    if axis == "x":
        position = Position(MARKER_SCALE / 2, 0, 0)
        rotation = Rotation(0, 0, -90)
    elif axis == "y":
        position = Position(0, MARKER_SCALE / 2, 0)
        rotation = Rotation(0, 0, 0)
    elif axis == "z":
        position = Position(0, 0, MARKER_SCALE / 2)
        rotation = Rotation(90, 0, 0)
    # click root
    click = Object(
        persist=persist,
        object_id=f"click-{axis}",
        parent=calibrateParent.object_id,
        rotation=rotation,
        position=position,
    )
    scene.add_object(click)
    calibrateparents.append(click)

    add_position_clicks(click.object_id, axis, "pos")
    add_position_clicks(click.object_id, axis, "neg")

    if fullAxis or axis == "y":
        add_rotation_clicks(click.object_id, axis, "pos")
        add_rotation_clicks(click.object_id, axis, "neg")


def add_position_clicks(parent, axis, direction):
    py = 1 if direction == "pos" else -1
    py2 = 2 if direction == "pos" else 1.5
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
            rotation=Rotation(-90, 0, 0),
            position=Position(
                x * MARKER_SCALE / 5, MARKER_SCALE / 10, -MARKER_SCALE / 2
            ),
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
    if rig is None or not rig["enabled"]:
        return
    obj_topic = f"{scene.root_topic}/{user_id}"
    if rig:
        qx, qy, qz, qw = Utils.matrix3_to_quat(rig["rotation"])
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
    if rig is None or not rig["enabled"]:
        return
    prev_rig_pos = rig["position"]
    new_x = prev_rig_pos[X] - evt.data.position.x
    new_z = prev_rig_pos[Z] - evt.data.position.z
    rig["position"][X] = new_x
    rig["position"][Z] = new_z
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
    if rig is None or not rig["enabled"]:
        return
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
    global user_rigs
    rig = user_rigs.get(cam_id)
    if rig is None or not rig["enabled"]:
        return
    now = time.time()
    inc = 5 if (now - rig["last_click"]) < BIG_INC_THRESHOLD else 1
    rig["last_click"] = now
    rot_matrix = ROTATIONS[axis][direction][inc]
    rig["matrix"] = rot_matrix @ rig["matrix"]
    rig["rotation"] = rig["matrix"][:3, :3]
    rig["position"] = rig["matrix"][:3, 3]
    publish_rig_offset(cam_id)


scene.run_tasks()
