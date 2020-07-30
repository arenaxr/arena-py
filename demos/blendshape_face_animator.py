# blendshapes.py
#
# animate the bones of the 'Facegltf/sampledata.gltf' GLTF model
# bone names came from inspecting scene.gltf
# assumes the model 'izzy' already exists in ARENA scene 'cesium'

import arena
import random
import time
import signal
import json
import numpy as np
from scipy.spatial import distance
from scipy.spatial.transform import Rotation as R

HOST = "oz.andrew.cmu.edu"
SCENE = "face-agr"
OBJECT = "face-agr-model"

EYE_THRES = 0.16
MOUTH_THRES = 0.25

last_face_state = { 'jawOpen': 0.0, 'eyeBlink_L':0.0, 'eyeBlink_R':0.0, 'browOuterUp_L':0.0, 'browOuterUp_R':0.0,'rotation':[1.0,1.0,1.0,1.0] }

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

class Face(object):
    def __init__(self, msg_json):
        self.counter = 0
        self.update(msg_json)

    def update(self, msg_json):
        self.counter += 1

        self.srcWidth = msg_json["image"]["width"]
        self.srcHeight = msg_json["image"]["height"]

        self.rot = msg_json["pose"]["quaternions"]
        self.trans = msg_json["pose"]["translation"]

        self.bbox = np.array(msg_json["bbox"]).reshape((2,-1))

        self.landmarksRaw = np.array(msg_json["landmarks"]) # [x1, y1, x2, y2...]
        self.landmarks = self.landmarksRaw.reshape((self.landmarksRaw.size//2,-1)) # [[x1,y1],[x2,y2]...]
        self.landmarks = self.unrotateLandmarks(self.landmarks, self.rot)
        self.com = np.mean(self.landmarks, axis=0) # "center of mass" of face
        self.landmarks = self.normalizeToCOM(self.landmarks, self.com)

    def unrotateLandmarks(self, landmarks, rot):
        homoPts = np.vstack([landmarks.T, np.ones(len(landmarks))])
        transformed = (R.from_quat(rot).as_matrix() @ homoPts)
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


face = None

def callback(msg):
    global face, last_face_state
    msg_json = json.loads(msg)
    if "hasFace" in msg_json and msg_json["hasFace"]:
        if face is None:
            face = Face(msg_json)
        else:
            face.update(msg_json)

        # Outer Brow is set as a normalized scaler compared to face width
        browOuterUp_L = distance.euclidean(face.landmarks[19],face.landmarks[37])
        browOuterUp_R = distance.euclidean(face.landmarks[44],face.landmarks[24])
        # print( "Raw Brow Left:" , browOuterUp_L )
        # print( "Raw Brow Right:" , browOuterUp_R )

        browOuterScalar = 10.0
        browOuterUp_L -= 0.04
        browOuterUp_R -= 0.04

        browOuterUp_L = (browOuterUp_L/face.faceWidth) * browOuterScalar
        browOuterUp_R = (browOuterUp_R/face.faceWidth) * browOuterScalar

        if browOuterUp_L < 0:
            browOuterUp_L = 0
        if browOuterUp_R < 0:
            browOuterUp_R = 0

        if abs(last_face_state['browOuterUp_L']-browOuterUp_L) < 0.3:
            browOuterUp_L = last_face_state['browOuterUp_L']
        last_face_state['browOuterUp_L'] = browOuterUp_L

        if abs(last_face_state['browOuterUp_R']-browOuterUp_R) < 0.3:
            browOuterUp_R = last_face_state['browOuterUp_R']
        last_face_state['browOuterUp_R'] = browOuterUp_R

        # print( "Brow Left:" , browOuterUp_L )
        # print( "Brow Right:" , browOuterUp_R )

        # Mouth is set as a normalized scaler compared to face width
        mouthRight = distance.euclidean(face.landmarks[63],face.landmarks[65])
        mouthLeft = distance.euclidean(face.landmarks[61],face.landmarks[67])
        mouthPucker = distance.euclidean(face.landmarks[48],face.landmarks[54])

        mouthScalar = 5.0
        mouthThresh = 0.2

        mouthRight = (mouthRight/face.faceWidth) * mouthScalar
        mouthLeft = (mouthLeft/face.faceWidth) * mouthScalar
        mouthPucker = (mouthPucker/face.faceWidth)
        # print( "RawPucker: ", mouthPucker )
        mouthPucker -= 0.35 # remove DC offset
        if mouthPucker < 0.0:
            mouthPucker = 0.0
        mouthPucker *= 2
        mouthPucker = 1.0 - mouthPucker # Invert it
        mouthPucker = 0.0
        # print( "MouthPucker: ", mouthPucker )

        openness = face.mouthAspect() * 2
        if openness < MOUTH_THRES: openness = 0.0

        # print(face.blinkAmount)
        blink = int(face.blinkAmount < EYE_THRES)

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

        rotChange = distance.euclidean(face.rot,last_face_state['rotation'])
        if rotChange < 0.03:
            face.rot = last_face_state['rotation']
        last_face_state['rotation'] = face.rot

        # print(morphStr)
        if face.counter % 2 == 0:
            obj = arena.Object(
                rotation=face.rot,
                # location=(face.trans[0]/10, face.trans[1]/10+3, (face.trans[2]+50)/10-5),
                # rotation=(0,0,0.6-openness,1), # quaternion value roughly between -.05 and .05
                objName=OBJECT,
                # url="models/Facegltf/sampledata.gltf",
                objType=arena.Shape.gltf_model,
                scale=(15,15,15),
                location=(0,2,-5),
                data=morphStr
            )


arena.init(HOST, "realm", SCENE, callback=callback)
arena.handle_events()
