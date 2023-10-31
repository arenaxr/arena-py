import math
from ..utils import Utils
from .attribute import Attribute
from collections.abc import Iterable


class Rotation(Attribute):
    """
    Rotation Attribute in quaternions or euler.
    Usage: rotation=Rotation(x,y,z,w) or rotation=Rotation(x,y,z)
    """

    def __init__(self, x=None, y=None, z=None, w=None):
        if x is not None and (y is None or z is None or isinstance(x, Iterable)):
            raise ValueError("Rotation takes x,y,z or x,y,z,w")
        x = x or 0
        y = y or 0
        z = z or 0
        if w is not None:  # quaternion
            super().__init__(
                x=Utils.agran(x), y=Utils.agran(y), z=Utils.agran(z), w=Utils.agran(w)
            )
        else:  # euler
            super().__init__(
                x=Utils.agran(x), y=Utils.agran(y), z=Utils.agran(z), w=None
            )

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
        if self.is_quaternion:  # quaternions
            euler = Rotation.q2e((self.x, self.y, self.z, self.w))
            return Rotation(*euler)
        else:  # euler
            return self

    @property
    def quaternion(self):
        if self.is_quaternion:  # quaternions
            return self
        else:  # euler
            quat = Rotation.e2q((self.x, self.y, self.z))
            return Rotation(*quat)

    @classmethod
    def q2e(cls, q):
        """quaternions to euler (degrees)"""
        x, y, z, w = q

        # Roll (x-axis rotation)
        sinr_cosp = 2.0 * (w * x + y * z)
        cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        # Pitch (y-axis rotation)
        sinp = 2.0 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)  # Use 90 degrees if out of range
        else:
            pitch = math.asin(sinp)

        # Yaw (z-axis rotation)
        siny_cosp = 2.0 * (w * z + x * y)
        cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        return (math.degrees(roll), math.degrees(pitch), math.degrees(yaw))

    @classmethod
    def e2q(cls, e):
        """euler (degrees) to quaternions"""
        roll, pitch, yaw = e

        roll_rad = math.radians(roll)
        pitch_rad = math.radians(pitch)
        yaw_rad = math.radians(yaw)

        cy = math.cos(yaw_rad * 0.5)
        sy = math.sin(yaw_rad * 0.5)
        cp = math.cos(pitch_rad * 0.5)
        sp = math.sin(pitch_rad * 0.5)
        cr = math.cos(roll_rad * 0.5)
        sr = math.sin(roll_rad * 0.5)

        w = cy * cp * cr + sy * sp * sr
        x = cy * cp * sr - sy * sp * cr
        y = sy * cp * sr + cy * sp * cr
        z = sy * cp * cr - cy * sp * sr

        return (x, y, z, w)
