# jitsi-avatar.py
#
# rigs 3d avatar to replace camera head on ARENA videoconf

import arena
import random
import time
import signal
import json
import sys
import numpy as np
from scipy.spatial import distance
from scipy.spatial.transform import Rotation as R

if len(sys.argv) != 2:
    print("Usage: jitsi-avatar.py <scene-name>")
    exit(0)

HOST = "oz.andrew.cmu.edu"
SCENE = sys.argv[1]

EYE_THRES = 0.16
MOUTH_THRES = 0.05

users = {}

anims = [
    "shapes.browInnerUp",
    "shapes.browDown_L",
    "shapes.browDown_R",
    "shapes.browOuterUp_L",
    "shapes.browOuterUp_R",
    "shapes.eyeLookUp_L",
    "shapes.eyeLookUp_R",
    "shapes.eyeLookDown_L",
    "shapes.eyeLookDown_R",
    "shapes.eyeLookIn_L",
    "shapes.eyeLookIn_R",
    "shapes.eyeLookOut_L",
    "shapes.eyeLookOut_R",
    "shapes.eyeBlink_L",
    "shapes.eyeBlink_R",
    "shapes.eyeSquint_L",
    "shapes.eyeSquint_R",
    "shapes.eyeWide_L",
    "shapes.eyeWide_R",
    "shapes.cheekPuff",
    "shapes.cheekSquint_L",
    "shapes.cheekSquint_R",
    "shapes.noseSneer_L",
    "shapes.noseSneer_R",
    "shapes.jawOpen",
    "shapes.jawForward",
    "shapes.jawLeft",
    "shapes.jawRight",
    "shapes.mouthFunnel",
    "shapes.mouthPucker",
    "shapes.mouthLeft",
    "shapes.mouthRight",
    "shapes.mouthRollUpper",
    "shapes.mouthRollLower",
    "shapes.mouthShrugUpper",
    "shapes.mouthShrugLower",
    "shapes.mouthClose",
    "shapes.mouthSmile_L",
    "shapes.mouthSmile_R",
    "shapes.mouthFrown_L",
    "shapes.mouthFrown_R",
    "shapes.mouthDimple_L",
    "shapes.mouthDimple_R",
    "shapes.mouthUpperUp_L",
    "shapes.mouthUpperUp_R",
    "shapes.mouthLowerDown_L",
    "shapes.mouthLowerDown_R",
    "shapes.mouthPress_L",
    "shapes.mouthPress_R",
    "shapes.mouthStretch_L",
    "shapes.mouthStretch_R",
    "tongue_out"
]

def q_mult(q1, q2):
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    return [x, y, z, w]

class Face(object):
    def __init__(self, msg_json):
        self.update(msg_json)

    def update(self, msg_json):
        self.srcWidth = msg_json["image"]["width"]
        self.srcHeight = msg_json["image"]["height"]

        self.rot = msg_json["pose"]["quaternions"]
        self.trans = msg_json["pose"]["translation"]

        self.bbox = np.array(msg_json["bbox"]).reshape((2,-1))

        self.landmarksRaw = np.array(msg_json["landmarks"]) # [x1, y1, x2, y2...]
        self.landmarks = self.landmarksRaw.reshape((-1,2)) # [[x1,y1],[x2,y2]...]
        self.landmarks = self.unrotateLandmarks(self.landmarks, self.rot)
        self.com = np.mean(self.landmarks, axis=0) # "center of mass" of face
        self.landmarks = self.normalizeToCOM(self.landmarks, self.com)

    def unrotateLandmarks(self, landmarks, rot):
        homoPts = np.vstack([landmarks.T, np.ones(len(landmarks))])
        transformed = (np.linalg.inv(R.from_quat(rot).as_matrix()) @ homoPts)
        unrot = transformed / transformed[-1]
        return unrot[:-1].T

    def normalizeToCOM(self, landmarks, com):
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

    def create_line(self, pts1, pts2, name):
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

    def drawLandmarks(self):
        arena.Object(
            objName="origin",
            objType=arena.Shape.sphere,
            scale=(0.01,0.01,0.01),
            location=(0,2,-0.5),
            persist=False
        )
        for i in range(0, len(self.jawPts)-1):
            self.create_line(self.jawPts[i], self.jawPts[i+1], "jaw"+str(i))
        for i in range(0, len(self.eyebrowLPts)-1):
            self.create_line(self.eyebrowLPts[i], self.eyebrowLPts[i+1], "browL"+str(i))
        for i in range(0, len(self.eyebrowRPts)-1):
            self.create_line(self.eyebrowRPts[i], self.eyebrowRPts[i+1], "browR"+str(i))
        for i in range(0, len(self.noseBridgePts)-1):
            self.create_line(self.noseBridgePts[i], self.noseBridgePts[i+1], "noseB"+str(i))
        for i in range(0, len(self.noseLowerPts)-1):
            self.create_line(self.noseLowerPts[i], self.noseLowerPts[i+1], "noseL"+str(i))
        self.create_line(self.noseLowerPts[0], self.noseLowerPts[-1], "noseL"+str(i+1))
        for i in range(0, len(self.eyeLPts)-1):
            self.create_line(self.eyeLPts[i], self.eyeLPts[i+1], "eyeL"+str(i))
        self.create_line(self.eyeLPts[0], self.eyeLPts[-1], "eyeL"+str(i+1))
        for i in range(0, len(self.eyeRPts)-1):
            self.create_line(self.eyeRPts[i], self.eyeRPts[i+1], "eyeR"+str(i))
        self.create_line(self.eyeRPts[0], self.eyeRPts[-1], "eyeR"+str(i+1))
        for i in range(0, len(self.lipOuterPts)-1):
            self.create_line(self.lipOuterPts[i], self.lipOuterPts[i+1], "lipO"+str(i))
        self.create_line(self.lipOuterPts[0], self.lipOuterPts[-1], "lipO"+str(i+1))
        for i in range(0, len(self.lipInnerPts)-1):
            self.create_line(self.lipInnerPts[i], self.lipInnerPts[i+1], "lipI"+str(i))
        self.create_line(self.lipInnerPts[0], self.lipInnerPts[-1], "lipI"+str(i+1))

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

class Head(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.counter = 0
        self.has_face = False
        self.rig = True
        self.obj = None

    def rigOn(self):
        self.rig = True

    def rigOff(self):
        self.rig = False
        if self.obj is not None:
            self.obj.delete()

    def add_face(self, face_json):
        self.last_face_state = { 'jawOpen': 0.0, 'eyeBlink_L':0.0, 'eyeBlink_R':0.0, 'browOuterUp_L':0.0, 'browOuterUp_R':0.0,'rotation':[1.0,1.0,1.0,1.0] }
        self.face = Face(face_json)
        self.has_face = True
        self.update_face(face_json)

    def update_face(self, face_json):
        if not self.rig: return
        self.counter += 1

        self.face.update(face_json)

        # Outer Brow is set as a normalized scaler compared to face width
        browOuterUp_L = distance.euclidean(self.face.landmarks[19],self.face.landmarks[37])
        browOuterUp_R = distance.euclidean(self.face.landmarks[44],self.face.landmarks[24])
        # print( "Raw Brow Left:" , browOuterUp_L )
        # print( "Raw Brow Right:" , browOuterUp_R )

        browOuterScalar = 10.0
        browOuterUp_L -= 0.04
        browOuterUp_R -= 0.04

        browOuterUp_L = (browOuterUp_L/self.face.faceWidth) * browOuterScalar
        browOuterUp_R = (browOuterUp_R/self.face.faceWidth) * browOuterScalar

        if browOuterUp_L < 0:
            browOuterUp_L = 0
        if browOuterUp_R < 0:
            browOuterUp_R = 0

        if abs(self.last_face_state['browOuterUp_L']-browOuterUp_L) < 0.3:
            browOuterUp_L = self.last_face_state['browOuterUp_L']
        self.last_face_state['browOuterUp_L'] = browOuterUp_L

        if abs(self.last_face_state['browOuterUp_R']-browOuterUp_R) < 0.3:
            browOuterUp_R = self.last_face_state['browOuterUp_R']
        self.last_face_state['browOuterUp_R'] = browOuterUp_R

        # print( "Brow Left:" , browOuterUp_L )
        # print( "Brow Right:" , browOuterUp_R )

        # Mouth is set as a normalized scaler compared to face width
        mouthRight = distance.euclidean(self.face.landmarks[63],self.face.landmarks[65])
        mouthLeft = distance.euclidean(self.face.landmarks[61],self.face.landmarks[67])
        mouthPucker = distance.euclidean(self.face.landmarks[48],self.face.landmarks[54])

        mouthScalar = 5.0
        mouthThresh = 0.10

        mouthRight = (mouthRight/self.face.faceWidth) * mouthScalar
        mouthLeft = (mouthLeft/self.face.faceWidth) * mouthScalar
        mouthPucker = (mouthPucker/self.face.faceWidth)
        # print( "RawPucker: ", mouthPucker )
        mouthPucker -= 0.35 # remove DC offset
        if mouthPucker < 0: mouthPucker = 0.0
        mouthPucker *= 2
        mouthPucker = 1.0 - mouthPucker # Invert it
        mouthPucker = 0.0
        # print( "MouthPucker: ", mouthPucker )

        openness = self.face.mouthAspect()
        if openness < MOUTH_THRES: openness = 0.0

        # print(self.face.blinkAmount)
        blink = int(self.face.blinkAmount < EYE_THRES)

        morphStr = '{ "gltf-morph": {"morphtarget": "shapes.jawOpen", "value": "' + str(openness) + '" },'
        # morphStr = '{ "gltf-morph": {"morphtarget": "shapes.mouthUpperUp_L", "value": "' + str(mouthLeft) + '" },'
        # morphStr += '"gltf-morph__2": {"morphtarget": "shapes.mouthUpperUp_R", "value": "' + str(mouthRight) + '" },'
        # morphStr += '"gltf-morph__3": {"morphtarget": "shapes.mouthLowerDown_L", "value": "' + str(mouthLeft) + '" },'
        # morphStr += '"gltf-morph__4": {"morphtarget": "shapes.mouthLowerDown_R", "value": "' + str(mouthRight) + '" },'
        morphStr += '"gltf-morph__5": {"morphtarget": "shapes.eyeBlink_L", "value": "' + str(blink) + '" },'
        morphStr += '"gltf-morph__6": {"morphtarget": "shapes.eyeBlink_R", "value": "' + str(blink) + '" },'
        morphStr += '"gltf-morph__7": {"morphtarget": "shapes.browOuterUp_L", "value": "' + str(browOuterUp_L) + '" },'
        morphStr += '"gltf-morph__8": {"morphtarget": "shapes.browOuterUp_R", "value": "' + str(browOuterUp_R) + '" },'
        morphStr += '"gltf-morph__9": {"morphtarget": "shapes.mouthPucker", "value": "' + str(mouthPucker) + '" }'
        morphStr += '}'

        rotChange = distance.euclidean(self.face.rot,self.last_face_state['rotation'])
        if rotChange < 0.03:
            self.face.rot = self.last_face_state['rotation']
        self.last_face_state['rotation'] = self.face.rot

        # head faces backward at first, rotate head 180 to correct
        corrected_rot = q_mult(self.face.rot, [0,1,0,0])
        # flip left right rotations
        # corrected_rot[2] *= -1
        # corrected_rot[3] *= -1

        if self.counter % 2 == 0:
            self.obj = arena.Object(
                objName=f"head_{self.user_id}",
                objType=arena.Shape.gltf_model,
                scale=(1.75,1.75,1.75),
                rotation=corrected_rot,
                location=(0.0, -0.07, 0.035),
                #location=(self.face.trans[0]/100, self.face.trans[1]/100, (self.face.trans[2]+50)/100+.25),
                url="/models/FaceCapHeadGeneric/FaceCapHeadGeneric.gltf",
                parent="camera_"+self.user_id,
                data=morphStr
            )

def extract_user_id(obj_id):
    return "_".join(obj_id.split("_")[1:])

def callback(msg):
    global users

    msg_json = json.loads(msg)
    # print(msg_json)

    if "avatar" in msg_json:
        user = extract_user_id(msg_json["object_id"])
        if msg_json["avatar"]:
            if user not in users:
                users[user] = Head(user)
            users[user].rigOn()
        else:
            if user in users:
                users[user].rigOff()

    elif "hasFace" in msg_json and msg_json["hasFace"]:
        user = extract_user_id(msg_json["object_id"])
        if user in users:
            if not users[user].has_face:
                users[user].add_face(msg_json)
            else:
                users[user].update_face(msg_json)

arena.init(HOST, "realm", SCENE, callback=callback)
arena.handle_events()
