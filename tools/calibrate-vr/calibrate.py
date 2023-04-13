# callibrate.py
"""
A tool to calibrate the user's camera rig.
"""
from arena import *
import json
import time

POSITION_INC = 0.01
POSITION_INC_BIG = 0.5  # TODO: handle press-and-hold larger increments
ROTATION_INC = 1
ROTATION_INC_BIG = 5  # TODO: handle press-and-hold larger increments
BIG_INC_THRESHOLD = 0.75  # seconds

persist = True

MARKER_SCALE = 0.15
OPC_ON = 0.85
OPC_OFF = 0.25
CONE_SCALE = Scale(MARKER_SCALE / 5, MARKER_SCALE / 5 * 2, MARKER_SCALE / 5)
parents = []
user_rigs = {}


def end_program_callback(_scene: Scene):
    global parents
    # reverse parental order allows for branch to trunk deletion
    parents.reverse()
    for parent in parents:
        scene.delete_object(parent)


# command line options
scene = Scene(cli_args=True, end_program_callback=end_program_callback)


def user_join_callback(_scene, cam, _msg):
    global user_rigs
    user_rigs[cam.object_id] = {
        "position": Position(0, 0, 0),
        "rotation": Rotation(0, 0, 0),
        "last_click": 0,
    }


def user_left_callback(_scene, cam, _msg):
    global user_rigs
    del user_rigs[cam.object_id]


@scene.run_once
def main():
    addobjects()
    scene.user_join_callback = user_join_callback
    scene.user_left_callback = user_left_callback


def addobjects():
    global sceneParent, parents
    # parent scene object
    sceneParent = Entity(
        persist=persist,
        object_id="callibrateParent",
        position=Position(0, 0.1, 0),
    )
    scene.add_object(sceneParent)
    parents.append(sceneParent)

    # marker gltf
    origin_marker = GLTF(
        persist=persist,
        object_id="origin-marker",
        parent=sceneParent.object_id,
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

    groundPlane = Plane(
        persist=persist,
        object_id="click-ground-plane",
        parent=sceneParent.object_id,
        position=Position(0, -0.2, 0),
        rotation=Rotation(-90, 0, 0),
        width=20,
        height=20,
        material=Material(color=(128,128,128), opacity=OPC_OFF),
        clickable=True,
        evt_handler=ground_click_handler,
    )
    scene.add_object(groundPlane)


def get_color(axis):
    if axis == "x":
        return Color(0, 255, 0)
    elif axis == "y":
        return Color(0, 0, 255)
    elif axis == "z":
        return Color(255, 0, 0)


def add_axis(axis):
    global sceneParent
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
        parent=sceneParent.object_id,
        rotation=rotation,
        position=position,
    )
    scene.add_object(click)
    parents.append(click)

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
    rx = 0 if direction == "pos" else 180
    scene.add_object(
        Cone(
            persist=persist,
            object_id=f"click-position-{axis}-{direction}",
            parent=parent,
            scale=CONE_SCALE,
            rotation=Rotation(rx, 0, 0),
            position=Position(0, (MARKER_SCALE / 2) + (py * MARKER_SCALE / 5), 0),
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
            position=Position(x * MARKER_SCALE / 10, 0, 0),
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
        quat = rig["rotation"].quaternion
        msg = {
                "object_id": user_id,
                "type": "rig",
                "action": "update",
                "data": {
                    "position": {
                        "x": rig["position"].x,
                        "y": rig["position"].y,
                        "z": rig["position"].z,
                    },
                   "rotation": {
                        "x": quat.x,
                        "y": quat.y,
                        "z": quat.z,
                        "w": quat.w,
                    }
                },
        }
        scene.mqttc.publish(obj_topic, json.dumps(msg))


def ground_click_handler(_scene, evt, _msg):
    """
    This handles clicks on the ground plane which indicate that a user is starting
    fairly far off from the origin marker. We ignore rotation completely and simply
    apply an initial inverse translation of x and z to the camera offset rig (since
    y is assumed always to be 0).
    """
    if evt.type != "mousedown":
        return
    global user_rigs
    rig = user_rigs.get(evt.data.source)
    rig["position"].x = -evt.data.clickPos.x
    rig["position"].z = -evt.data.clickPos.z
    # print(f'Ground click: {evt.data.clickPos.x}, {evt.data.clickPos.z}')
    publish_rig_offset(evt.data.source)


def camera_position_updater(cam_id, axis, direction):
    """
    We use this to nudge position of camera offset rig. Bearing in mind that the rig
    offset is what is actually being modified, we once again apply the inverse value.
    We shouldn't be nudging y position, but we'll leave it in for now.
    """
    # print(f'Camera position updater: {cam_id}, {axis}, {direction}')
    global user_rigs
    rig = user_rigs.get(cam_id)
    if axis == "x":
        rig["position"].x += -POSITION_INC if direction == "pos" else POSITION_INC
    elif axis == "y":
        rig["position"].y += -POSITION_INC if direction == "pos" else POSITION_INC
    elif axis == "z":
        rig["position"].z += -POSITION_INC if direction == "pos" else POSITION_INC
    publish_rig_offset(cam_id)


def camera_rotation_updater(cam_id, axis, direction):
    """
    We use this to nudge rotation of camera offset rig. Bearing in mind that the rig
    offset is what is actually being modified, we once again apply the inverse value.
    We shouldn't be nudging x or z rotation, but we'll leave it in for now.
    """
    # print(f'Camera rotation updater: {cam_id}, {axis}, {direction}')
    global user_rigs
    rig = user_rigs.get(cam_id)
    now = time.time()
    inc = ROTATION_INC_BIG if (now - rig["last_click"]) < BIG_INC_THRESHOLD else ROTATION_INC
    rig["last_click"] = now
    if axis == "x":
        rig["rotation"].x += -inc if direction == "pos" else inc
    elif axis == "y":
        rig["rotation"].y += -inc if direction == "pos" else inc
    elif axis == "z":
        rig["rotation"].z += -inc if direction == "pos" else inc
    publish_rig_offset(cam_id)


scene.run_tasks()
