from arena import *

import numpy as np
from arena.utils import Utils

scene = Scene(host="arenaxr.org", scene="grab")

grabbing = False

grabber = None
child_pose_relative_to_parent = None

orig_position = (0,1.5,-2)
orig_scale = (0.5,0.5,0.5)
grabbed_scale = (0.55,0.55,0.55)

def pose_matrix(position, rotation):
    position = np.array((position.x, position.y, position.z))
    rotation = np.array((rotation.x, rotation.y, rotation.z, rotation.w))
    scale = np.array((1, 1, 1))

    rotation_matrix = np.eye(4)
    rotation_matrix[:3,:3] = Utils.quat_to_matrix3(rotation)

    scale_matrix = np.diag([scale[0], scale[1], scale[2], 1])

    translation_matrix = np.eye(4)
    translation_matrix[:3, 3] = [position[0], position[1], position[2]]

    pose_matrix = translation_matrix @ rotation_matrix @ scale_matrix

    return pose_matrix

def get_relative_pose_to_parent(parent_pose, child_pose_world):
    parent_pose_inverse = np.linalg.inv(parent_pose)
    relative_pose = parent_pose_inverse @ child_pose_world
    return relative_pose

def get_world_pose_when_parented(parent_pose, child_pose_relative_to_parent):
    world_pose = parent_pose @ child_pose_relative_to_parent
    return world_pose

def box_click(scene, evt, msg):
    global my_box
    global grabbing
    global grabber
    global orig_scale
    global child_pose_relative_to_parent

    if evt.type == "mousedown":
        clicker = scene.users[evt.data.source]
        handRight = clicker.hands.get("handRight", None)
        # handLeft = clicker.hands.get("handLeft", None)

        if not grabbing:
            print("grabbed")

            if handRight is not None:
                grabber = handRight

                grabbing = True
                hand_pose = pose_matrix(grabber.data.position, grabber.data.rotation)
                child_pose = pose_matrix(my_box.data.position, my_box.data.rotation)
                child_pose_relative_to_parent = get_relative_pose_to_parent(hand_pose, child_pose)

    elif evt.type == "mouseup":
        if grabbing:
            print("released")
            grabbing = False
            my_box.update_attributes(scale=orig_scale)
            scene.update_object(my_box)

my_box = Box(
    object_id="my_box",
    position=orig_position,
    scale=orig_scale,
    rotation=(1,0,0,0),
    color=(50,60,200),
    patent=None,
    clickable=True,
    evt_handler=box_click
)

@scene.run_forever(interval_ms=10)
def move_box():
    global my_box
    global grabber
    global grabbed_scale
    global child_pose_relative_to_parent

    if grabber is not None and child_pose_relative_to_parent is not None and grabbing:
        hand_pose = pose_matrix(grabber.data.position, grabber.data.rotation)
        new_pose = get_world_pose_when_parented(hand_pose, child_pose_relative_to_parent)

        new_position = (new_pose[0,3], new_pose[1,3], new_pose[2,3])
        new_rotation = Utils.matrix3_to_quat(new_pose[:3,:3])
        new_rotation = (new_rotation[3], new_rotation[0], new_rotation[1], new_rotation[2])

        my_box.update_attributes(position=new_position, scale=grabbed_scale)#, rotation=new_rotation)
        scene.update_object(my_box)

@scene.run_once
def main():
    scene.add_object(my_box)

scene.run_tasks()

