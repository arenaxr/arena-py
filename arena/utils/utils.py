# simple general purpose functions
import numpy as np
from scipy.spatial.transform import Rotation


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
    def pose_to_matrix4(cls, pos, rotq, scale=(1, 1, 1)):  # Def arg not mutated
        mat = np.identity(4)
        mat[0:3, 0:3] = Rotation.from_quat([rotq.x, rotq.y, rotq.z, rotq.w]).as_matrix()
        mat[0:3, 3] = [pos.x, pos.y, pos.z]
        if scale != (1, 1, 1):
            scale_mat = np.identity(4)
            scale_mat[0:3, 0:3] = np.diag(scale)
            mat = mat @ scale_mat
        return mat

    @classmethod
    def matrix4_to_pose(cls, mat):
        pos = mat[0:3, 3]
        rotq = Rotation.from_matrix(mat[0:3, 0:3]).as_quat()
        scale = np.sqrt(np.sum(mat[0:3, 0:3] ** 2, axis=0))
        return pos, rotq, scale

    @classmethod
    def get_world_pose(cls, obj, scene):
        current_obj = obj
        matrices = []
        while current_obj.data.get("parent") is not None:
            current_matrix = cls.pose_to_matrix4(
                current_obj.data.position,
                current_obj.data.rotation,
                current_obj.data.scale,
            )
            matrices = [current_matrix] + matrices  # prepend
            current_obj = scene.all_objects[current_obj.data.parent]
        final_matrix = np.identity(4)
        for matrix in matrices:
            final_matrix = final_matrix @ matrix
        return cls.matrix4_to_pose(final_matrix)
