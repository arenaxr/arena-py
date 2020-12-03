import arena
import numpy as np
from scipy.spatial.transform import Rotation as R

def extract_user_id(obj_id):
    return "_".join(obj_id.split("_")[1:])

def draw_line(self, pts1, pts2, name):
        x1 = pts1[0]
        y1 = pts1[1] + 2
        x2 = pts2[0]
        y2 = pts2[1] + 2

        line = arena.Line(
                    (x1,y1,-0.5),
                    (x2,y2,-0.5),
                    2,
                    "#ffffff"
                )
        arena.Object(
            objName=name,
            objType=arena.Shape.line,
            line=line,
            persist=False
        )

def q_mult(q1, q2):
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    return [x, y, z, w]

def q2e(q):
    rot = R.from_quat(q)
    return rot.as_euler('xyz', degrees=False)

def e2q(e):
    rot = R.from_euler('xyz', e, degrees=False)
    return rot.as_quat()

# def get_exp_vect(self):
#     reshaped_lmks = self.landmarks.reshape((1,-1))
#     return model.predict(reshaped_lmks)

class MeanFilter(object):
    def __init__(self, capacity):
        self.history = []
        self.capacity = capacity

    def add(self, data):
        if len(self.history) >= self.capacity:
            self.history.pop(0)
        self.history += [data]

        return np.mean(self.history, axis=0)
