import math
from collections.abc import Iterable, Mapping

from ..utils import Utils
from .attribute import Attribute


class Rotation(Attribute):
    """
    Rotation attribute class to manage its properties in the ARENA: 3D object rotation in quaternion representation; Right-handed coordinate system. Euler degrees are **deprecated** in wire message format.
    Usage: `rotation=Rotation(...)` or `rotation=Rotation(x,y,z,w)` or `rotation=Rotation(x,y,z)` or `rotation=(x,y,z,w)` or `rotation=(x,y,z)`

    :param float|Iterable|Mapping w: w Defaults to '1' (optional)
    :param float x: x Defaults to '0' (optional)
    :param float y: y Defaults to '0' (optional)
    :param float z: z Defaults to '0' (optional)
    """

    def __init__(self, x=None, y=None, z=None, w=None):
        if isinstance(x, Mapping):
            if "w" in x:
                w = x["w"]
            if "x" in x and "y" in x and "z" in x:
                x, y, z = x["x"], x["y"], x["z"]
            else:
                raise ValueError("Rotation takes x,y,z,(w); a 3-4 element array or list; or a dict with {x,y,z,(w)}")
        elif isinstance(x, Iterable):
            if y is None and 3 <= len(x) <= 4:
                if len(x) == 3:
                    x, y, z = x
                else:
                    x, y, z, w = x
            else:
                raise ValueError("Rotation takes x,y,z,(w); a 3-4 element array or list; or a dict with {x,y,z,(w)}")
        x = x or 0
        y = y or 0
        z = z or 0
        if w is not None:  # quaternion
            self.check_quaternion(x, y, z, w)
            super().__init__(x=Utils.agran(x), y=Utils.agran(y), z=Utils.agran(z), w=Utils.agran(w))
        else:  # euler
            self.check_euler(x, y, z)
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

    @property
    def array(self):
        q = self.quaternion
        return [q.x, q.y, q.z, q.w]

    @array.setter
    def array(self, value):
        if not isinstance(value, Iterable) or len(value) not in [3, 4] or isinstance(value, Mapping):
            raise ValueError("Rotation array takes a 3-4 element array or list")
        if len(value) == 3:
            self.check_euler(value, value, value)
            self.x, self.y, self.z = value
            self.w = None
        else:
            self.check_quaternion(value, value, value, value)
            self.x, self.y, self.z, self.w = value

    def check_euler(self, x, y, z):
        values = [x, y, x]
        if any(e < -360 for e in values) or any(e > 360 for e in values):
            raise ValueError(f"Rotation euler values out of range: {x}, {y}, {z}")

    def check_quaternion(self, x, y, z, w):
        values = [x, y, x, w]
        if any(e < -1 for e in values) or any(e > 1 for e in values):
            raise ValueError(f"Rotation quaternion values out of range: {x}, {y}, {z}, {w}")

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
