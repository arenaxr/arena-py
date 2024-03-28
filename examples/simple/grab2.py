from arena import *

import numpy as np
from scipy.spatial.transform import Rotation

scene = Scene(host="arenaxr.org", scene="grab")

grabbing = False

hand = None
child_pose_relative_to_parent = None

orig_position = (0,1.5,-2)

def pose_matrix(position, rotation):
    position = np.array((position.x, position.y, position.z))
    rotation = np.array((rotation.x, rotation.y, rotation.z, rotation.w))
    scale = np.array((1, 1, 1))

    rotation_matrix = np.eye(4)
    rotation_matrix[:3,:3] = Rotation.from_quat(rotation).as_matrix()

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
    global hand
    global child_pose_relative_to_parent

    if evt.type == "mousedown":
        clicker = scene.users[evt.data.source]
        handRight = clicker.hands.get("handRight", None)
        # handLeft = clicker.hands.get("handLeft", None)

        if not grabbing:
            print("grabbed")

            if handRight is not None:
                hand = handRight

                grabbing = True
                hand_pose = pose_matrix(hand.data.position, hand.data.rotation)
                child_pose = pose_matrix(my_box.data.position, my_box.data.rotation)
                child_pose_relative_to_parent = get_relative_pose_to_parent(hand_pose, child_pose)

    elif evt.type == "mouseup":
        if grabbing:
            print("released")
            grabbing = False

my_box = Box(
    object_id="my_box",
    position=orig_position,
    scale=(0.5,0.5,0.5),
    rotation=(1,0,0,0),
    color=(50,60,200),
    patent=None,
    clickable=True,
    evt_handler=box_click
)

@scene.run_forever(interval_ms=10)
def move_box():
    global hand
    global child_pose_relative_to_parent

    if hand is not None and child_pose_relative_to_parent is not None and grabbing:
        hand_pose = pose_matrix(hand.data.position, hand.data.rotation)
        new_pose = get_world_pose_when_parented(hand_pose, child_pose_relative_to_parent)

        new_position = (new_pose[0,3], new_pose[1,3], new_pose[2,3])
        new_rotation = Rotation.from_matrix(new_pose[:3,:3]).as_quat()
        new_rotation = (new_rotation[3], new_rotation[0], new_rotation[1], new_rotation[2])

        my_box.update_attributes(position=new_position)#, rotation=new_rotation)
        scene.update_object(my_box)

@scene.run_once
def main():
    scene.add_object(my_box)

scene.run_tasks()

