from arena import Position, Rotation
import numpy as np
from scipy.spatial import distance

from utils import *

ROT_HIST_WINDOW     = 5
TRANS_HIST_WINDOW   = 5
LMK_HIST_WINDOW     = 3

class Face(object):
    def __init__(self):
        self.rot_filter = MeanFilter(ROT_HIST_WINDOW)
        self.trans_filter = MeanFilter(TRANS_HIST_WINDOW)
        self.lmks_filter = MeanFilter(LMK_HIST_WINDOW)
        self.model = model

    def update(self, data):
        self.src_width = data["image"]["width"]
        self.src_height = data["image"]["height"]

        # update rotation
        new_quat = data["pose"]["quaternions"]
        new_euler = Rotation(*new_quat).euler
        filtered_euler = self.rot_filter.add((new_euler.x, new_euler.y, new_euler.z)) # filter
        filtered_euler[0] *= -1.2   # flip direction and scale up a bit
        filtered_euler[0] += 5      # rotate up a bit
        filtered_euler[1] *= 0.7    # scale down
        # head faces backward at first, rotate head 180 to correct
        filtered_euler[1] += 180
        self.rot = Rotation(*filtered_euler)

        # update translation
        new_trans = data["pose"]["translation"]
        new_trans[0] = 0
        new_trans[1] = -0.07
        new_trans[2] = 0.035
        self.trans = self.trans_filter.add(new_trans) # filter
        self.trans = Position(*new_trans)

        self.bbox = np.array(data["bbox"]).reshape((2,-1))

        new_lmks = np.array(data["landmarks"]) # [x1, y1, x2, y2...]
        self.lmks_raw = self.lmks_filter.add(new_lmks) # filter
        self.landmarks = self.lmks_raw.reshape((-1,2)) # [[x1,y1],[x2,y2]...]
        self.center = np.mean(self.landmarks, axis=0) # "center of mass" of face
        self.landmarks = self.normalize_to_COM(self.landmarks, self.center)

    def normalize_to_COM(self, landmarks, com):
        return (landmarks - com) / (np.max(landmarks, axis=0)-np.min(landmarks, axis=0))

    def mouthAspect(self):
        height1 = distance.euclidean(self.lipInnerPts[1], self.lipInnerPts[7])
        height2 = distance.euclidean(self.lipInnerPts[2], self.lipInnerPts[6])
        height3 = distance.euclidean(self.lipInnerPts[3], self.lipInnerPts[5])
        width = distance.euclidean(self.lipInnerPts[0], self.lipInnerPts[4])
        return ((height1 + height2 + height3) / 3) / width

    def eyeAspect(self, eyePts):
        height1 = distance.euclidean(eyePts[1], eyePts[5])
        height2 = distance.euclidean(eyePts[2], eyePts[4])
        width = distance.euclidean(eyePts[0], eyePts[3])
        return ((height1 + height2) / 2) / width

    def get_expressions_vect(self):
        reshaped_lmks = self.landmarks.reshape((1,-1))
        return self.model.predict(reshaped_lmks)

    @property
    def faceWidth(self):
        # Grab some point to normalize face with distance
        # Not sure if width of face is good?
        return distance.euclidean(self.jawPts[0],self.jawPts[-1])

    @property
    def blinkAmount(self):
        return (self.eyeAspect(self.eyeRPts) + self.eyeAspect(self.eyeLPts)) / 2

    @property
    def jawPts(self):
        return self.landmarks[0:17]

    @property
    def eyebrowLPts(self):
        return self.landmarks[17:22]

    @property
    def eyebrowRPts(self):
        return self.landmarks[22:27]

    @property
    def noseBridgePts(self):
        return self.landmarks[27:31]

    @property
    def noseLowerPts(self):
        return self.landmarks[30:36] # both parts of nose are connected, so index is 30:36 and not 31:36

    @property
    def eyeLPts(self):
        return self.landmarks[36:42]

    @property
    def eyeRPts(self):
        return self.landmarks[42:48]

    @property
    def lipOuterPts(self):
        return self.landmarks[48:60]

    @property
    def lipInnerPts(self):
        return self.landmarks[60:68]
