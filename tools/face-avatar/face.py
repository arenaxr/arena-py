import arena
import numpy as np
from scipy.spatial import distance

from utils import *

ROT_HIST_WINDOW     = 7
TRANS_HIST_WINDOW   = 10
LMK_HIST_WINDOW     = 3

class Face(object):
    def __init__(self, msg_json):
        self.rot_filter = MeanFilter(ROT_HIST_WINDOW)
        self.trans_filter = MeanFilter(TRANS_HIST_WINDOW)
        self.lmks_filter = MeanFilter(LMK_HIST_WINDOW)

    def update(self, msg_json):
        self.src_width = msg_json["image"]["width"]
        self.src_height = msg_json["image"]["height"]

        # update rotation
        new_quat = msg_json["pose"]["quaternions"]
        new_euler = q2e(new_quat)
        filtered_euler = self.rot_filter.add(new_euler) # filter
        filtered_euler[0] *= 2.5 # scale up
        filtered_euler[1] *= 1.25 # scale up
        filtered_euler[2] *= 1.25 # scale up
        # head faces backward at first, rotate head 180 to correct
        filtered_euler[1] += 3.1415
        self.rot = e2q(filtered_euler)

        # update translation
        new_trans = msg_json["pose"]["translation"]
        new_trans[0] = 0
        new_trans[1] = -0.07
        new_trans[2] = 0.035
        self.trans = self.trans_filter.add(new_trans) # filter

        self.bbox = np.array(msg_json["bbox"]).reshape((2,-1))

        new_lmks = np.array(msg_json["landmarks"]) # [x1, y1, x2, y2...]
        self.lmks_raw = self.lmks_filter.add(new_lmks) # filter
        self.landmarks = self.lmks_raw.reshape((-1,2)) # [[x1,y1],[x2,y2]...]
        # self.landmarks = self.unrotate_lmks(self.landmarks, self.rot)
        self.center = np.mean(self.landmarks, axis=0) # "center of mass" of face
        self.landmarks = self.normalize_to_COM(self.landmarks, self.center)

    def unrotate_lmks(self, landmarks, rot):
        homoPts = np.vstack([landmarks.T, np.ones(len(landmarks))])
        transformed = (np.linalg.inv(R.from_quat(rot).as_matrix()) @ homoPts)
        unrot = transformed / transformed[-1]
        return unrot[:-1].T

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

    def draw_landmarks(self):
        arena.Object(
            objName="origin",
            objType=arena.Shape.sphere,
            scale=(0.01,0.01,0.01),
            location=(0,2,-0.5),
            persist=False
        )

        for i in range(0, len(self.jawPts)-1):
            draw_line(self.jawPts[i], self.jawPts[i+1], "jaw"+str(i))

        for i in range(0, len(self.eyebrowLPts)-1):
            draw_line(self.eyebrowLPts[i], self.eyebrowLPts[i+1], "browL"+str(i))

        for i in range(0, len(self.eyebrowRPts)-1):
            draw_line(self.eyebrowRPts[i], self.eyebrowRPts[i+1], "browR"+str(i))

        for i in range(0, len(self.noseBridgePts)-1):
            draw_line(self.noseBridgePts[i], self.noseBridgePts[i+1], "noseB"+str(i))

        for i in range(0, len(self.noseLowerPts)-1):
            draw_line(self.noseLowerPts[i], self.noseLowerPts[i+1], "noseL"+str(i))
        draw_line(self.noseLowerPts[0], self.noseLowerPts[-1], "noseL"+str(i+1))

        for i in range(0, len(self.eyeLPts)-1):
            draw_line(self.eyeLPts[i], self.eyeLPts[i+1], "eyeL"+str(i))
        draw_line(self.eyeLPts[0], self.eyeLPts[-1], "eyeL"+str(i+1))

        for i in range(0, len(self.eyeRPts)-1):
            draw_line(self.eyeRPts[i], self.eyeRPts[i+1], "eyeR"+str(i))
        draw_line(self.eyeRPts[0], self.eyeRPts[-1], "eyeR"+str(i+1))

        for i in range(0, len(self.lipOuterPts)-1):
            draw_line(self.lipOuterPts[i], self.lipOuterPts[i+1], "lipO"+str(i))
        draw_line(self.lipOuterPts[0], self.lipOuterPts[-1], "lipO"+str(i+1))

        for i in range(0, len(self.lipInnerPts)-1):
            draw_line(self.lipInnerPts[i], self.lipInnerPts[i+1], "lipI"+str(i))

        draw_line(self.lipInnerPts[0], self.lipInnerPts[-1], "lipI"+str(i+1))

    # def get_expressions_vect(self):
    #     reshaped_lmks = self.landmarks.reshape((1,-1))
    #     return model.predict(reshaped_lmks)

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
