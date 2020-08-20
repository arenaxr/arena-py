import math
import numpy as np
from scipy.spatial.transform import Rotation


def pose_to_matrix4(pos, rotq):
    mat = np.identity(4)
    mat[0:3, 0:3] = Rotation.from_quat(
        rotq._x, rotq._y, rotq._z, rotq._w).as_matrix()
    mat[0:3, 3] = [pos.x, pos.y, pose.z]
    return mat


def matrix4_to_pose(mat):
    pos = mat[0:3, 3]
    rotq = Rotation.from_matrix(mat[0:3, 0:3]).as_quat()
    return pos, rotq


def dtag_pose_to_matrix4(dtag_pose):
    FLIP = np.diag([1, -1, -1, 1])
    mat = np.identity(4)
    # Correct for column-major format of detected tag pose
    mat[0:3, 0:3] = np.array(dtag_pose.R).T
    mat[0:3, 3] = dtag_pose.t
    # Swap x/y axis of detected tag coordinate system
    mat = FLIP @ mat @ FLIP
    return mat


def reftag_pose_to_matrix4(reftag_pose):
    # comes in as col-major
    arr = reftag_pose.elements
    mat = np.array([arr[0:4], arr[4:8], arr[8:12], arr[12:16]]).T
    return mat


def pose_diff(pose1, pose2):
    pos1, rot1 = matrix4_to_pose(pose1)
    pos2, rot2 = matrix4_to_pose(pose2)
    pos_diff = np.linalg.norm(pos2 - pos1)
    rotmat_diff = rot2 @ rot1.T
    rot_diff = math.acos((np.trace(rotmat_diff) - 1) / 2)
    return pos_diff, rot_diff


def resolve_pose_ambiguity(pose1, err1, pose2, err2, vio, tagpose):
    vertical_vector = tagpose[0:3, 0:3].T @ np.array([[0, 1, 0]]).T
    pose1_vertical = pose1[0:3, 0:3] @ vertical_vector
    pose2_vertical = pose2[0:3, 0:3] @ vertical_vector
    vio_vertical = vio[0:3, 0:3].T @ vertical_vector
    pose1_vertical = pose1_vertical / np.linalg.norm(pose1_vertical)
    pose2_vertical = pose2_vertical / np.linalg.norm(pose2_vertical)
    vio_vertical = vio_vertical / np.linalg.norm(vio_vertical)
    valign1 = np.dot(pose1_vertical.T, vio_vertical)
    valign2 = np.dot(pose2_vertical.T, vio_vertical)
    if valign1 >= valign2 and err1 <= err2:
        return pose1, err1
    if valign2 >= valign1 and err2 <= err1:
        return pose2, err2
    if valign1 >= valign2:
        return pose1, 99999999.9
    return pose2, 99999999.9


def _test_resolve_pose_ambiguity():
    test_pose1 = np.array(
        [[.72, -.01, -.69, -.06],
         [-.05, 1.00, -.06, -.03],
         [.69, .07, .72, -1.15],
         [.00, .00, .00, 1.00]])
    test_error1 = 1e-6
    test_pose2 = np.array(
        [[.65, -.02, .76, -.05],
         [-.09, .99, .10, -.03],
         [-.75, -.13, .65, -1.14],
         [.00, .00, .00, 1.00]])
    test_error2 = 181e-6
    test_vio = np.identity(4)
    test_tagpose = np.identity(4)
    test_pose, test_error = resolve_pose_ambiguity(
        test_pose1, test_error1, test_pose2, test_error2, test_vio, test_tagpose)
    print(test_pose)
    print(test_error)


if __name__ == '__main__':
    _test_resolve_pose_ambiguity()
