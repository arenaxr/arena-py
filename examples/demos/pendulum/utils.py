import numpy as np
from arena.utils import Utils

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
