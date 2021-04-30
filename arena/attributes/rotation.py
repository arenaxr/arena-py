from ..utils import Utils
from .attribute import Attribute
from scipy.spatial.transform import Rotation as R

class Rotation(Attribute):
    """
    Rotation Attribute in quaternions or euler.
    Usage: rotation=Rotation(x,y,z,w) or rotation=Rotation(x,y,z)
    """
    def __init__(self, x=0, y=0, z=0, w=None):
        if w is not None: # quaternions
            super().__init__(x=Utils.agran(x), y=Utils.agran(y), z=Utils.agran(z), w=Utils.agran(w))
        else: # euler
            super().__init__(x=Utils.agran(x), y=Utils.agran(y), z=Utils.agran(z), w=None)

    def __repr__(self):
        if self.is_quaternion:
            return str(vars(self))
        else:
            rot_dict = vars(self).copy()
            del rot_dict["w"]
            return str(rot_dict)

    @property
    def is_quaternion(self):
        return self.w is not None

    @property
    def euler(self):
        if self.is_quaternion: # quaternions
            euler = Rotation.q2e((self.x, self.y, self.z, self.w))
            return Rotation(*euler)
        else: # euler
            return self

    @property
    def quaternion(self):
        if self.is_quaternion: # quaternions
            return self
        else: # euler
            quat = Rotation.e2q((self.x, self.y, self.z))
            return Rotation(*quat)

    @classmethod
    def q2e(cls, q):
        """quaternions to euler"""
        rot = R.from_quat(q)
        return rot.as_euler('xyz', degrees=True)

    @classmethod
    def e2q(cls, e):
        """euler to quaternions"""
        rot = R.from_euler('xyz', e, degrees=False)
        return rot.as_quat()
