# simple general purpose functions
import numpy as np


class Utils(object):
    @classmethod
    def tuple_to_string(cls, tup, sep=" "):
        """Turns a tuple into a string"""
        s = ""
        for val in tup:
            s += str(val) + sep
        return s.strip()

    @classmethod
    def agran(cls, float_num):
        """Reduces floating point numbers to ARENA granularity"""
        if isinstance(float_num, str):
            try:
                float_num = float(float_num)
            except:
                pass
        return round(float_num, 3)

    @classmethod
    def dict_key_replace(cls, d, key, new_key):
        """Repalces a key,val with a new key,val"""
        if key in d:
            ref = d[key]
            del d[key]
            d[new_key] = ref
        return d

    @classmethod
    def quat_to_matrix3(cls, rotq):
        x, y, z, w = rotq

        # Compute matrix elements
        xx, xy, xz = x * x, x * y, x * z
        yy, yz, zz = y * y, y * z, z * z
        wx, wy, wz = w * x, w * y, w * z

        # Rotation matrix
        rot_matrix = np.array(
            [
                [1 - 2 * (yy + zz), 2 * (xy - wz), 2 * (xz + wy)],
                [2 * (xy + wz), 1 - 2 * (xx + zz), 2 * (yz - wx)],
                [2 * (xz - wy), 2 * (yz + wx), 1 - 2 * (xx + yy)],
            ]
        )

        return rot_matrix

    @classmethod
    def matrix3_to_quat(cls, rotm):
        m00, m01, m02 = rotm[0, 0], rotm[0, 1], rotm[0, 2]
        m10, m11, m12 = rotm[1, 0], rotm[1, 1], rotm[1, 2]
        m20, m21, m22 = rotm[2, 0], rotm[2, 1], rotm[2, 2]

        # Compute quaternion components
        w = np.sqrt(max(0, 1 + m00 + m11 + m22)) / 2
        x = np.sqrt(max(0, 1 + m00 - m11 - m22)) / 2
        y = np.sqrt(max(0, 1 - m00 + m11 - m22)) / 2
        z = np.sqrt(max(0, 1 - m00 - m11 + m22)) / 2

        x = np.copysign(x, m21 - m12)
        y = np.copysign(y, m02 - m20)
        z = np.copysign(z, m10 - m01)

        return np.array([x, y, z, w])

    @classmethod
    def pose_to_matrix4(cls, pos, rotq, scale=(1, 1, 1)):  # Def arg not mutated
        mat = np.identity(4)
        mat[0:3, 0:3] = cls.quat_to_matrix3([rotq.x, rotq.y, rotq.z, rotq.w])
        mat[0:3, 3] = [pos.x, pos.y, pos.z]
        if scale != (1, 1, 1):
            scale_mat = np.identity(4)
            scale_mat[0:3, 0:3] = np.diag(scale)
            mat = mat @ scale_mat
        return mat

    @classmethod
    def matrix4_to_pose(cls, mat):
        pos = mat[0:3, 3]
        rotq = cls.matrix3_to_quat(mat[0:3, 0:3])
        scale = np.sqrt(np.sum(mat[0:3, 0:3] ** 2, axis=0))
        return pos, rotq, scale

    @classmethod
    def get_world_pose(cls, obj, scene):
        current_obj = obj
        matrices = []
        while "parent" in current_obj.data:
            current_matrix = cls.pose_to_matrix4(
                current_obj.data.position,
                current_obj.data.rotation.quaternion,
                current_obj.data.scale.array,
            )
            matrices = [current_matrix] + matrices  # prepend
            current_obj = scene.all_objects[current_obj.data.parent]
        final_matrix = np.identity(4)
        for matrix in matrices:
            final_matrix = final_matrix @ matrix
        return cls.matrix4_to_pose(final_matrix)
