import arena
import numpy as np
from scipy.spatial import distance

from face import Face

EYE_THRES = 0.17
MOUTH_THRES = 0.05

class Head(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.has_face = False
        self.rig_enabled = True
        self.obj = None
        self.model_path = "/store/users/wiselab/models/FaceCapHeadGeneric/FaceCapHeadGeneric.gltf"
        self.anims=[
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

    def rig_on(self):
        self.rig_enabled = True

    def rig_off(self):
        if self.rig_enabled and self.obj:
            self.obj.delete()
        self.rig_enabled = False

    def add_face(self, face_json):
        self.face = Face(face_json)
        self.face.update(face_json)
        self.has_face = True
        self.update_face(face_json)

    def create_morph(self, exp_vect):
        morphStr = '{'
        for i in range(len(exp_vect)-2):
            morphStr +='"gltf-morph__' + str(i) + '":{"morphtarget":"' + self.anims[i] + '","value":"' + str(round(exp_vect[i],3)) + '"},'
        i = len(exp_vect) - 1
        morphStr +='"gltf-morph__' + str(i) + '":{"morphtarget":"' + self.anims[i] + '","value":"' + "0.0" + '"}'
        morphStr += '}'
        return morphStr

    def update_face(self, face_json):
        self.face.update(face_json)

        # Outer Brow is set as a normalized scaler compared to face width
        browOuterUp_L = distance.euclidean(self.face.landmarks[19],self.face.landmarks[37])
        browOuterUp_R = distance.euclidean(self.face.landmarks[44],self.face.landmarks[24])
        # print( "Raw Brow Left:" , browOuterUp_L )
        # print( "Raw Brow Right:" , browOuterUp_R )

        browOuterScalar = 5.0
        browOuterUp_L -= 0.04
        browOuterUp_R -= 0.04

        browOuterUp_L = (browOuterUp_L/self.face.faceWidth) * browOuterScalar
        browOuterUp_R = (browOuterUp_R/self.face.faceWidth) * browOuterScalar

        browOuterUp_L = min(browOuterUp_L, 0)
        browOuterUp_R = min(browOuterUp_R, 0)

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

        self.obj = arena.Object(
            objName=f"avatar_{self.user_id}",
            objType=arena.Shape.gltf_model,
            scale=(1.75,1.75,1.75),
            rotation=self.face.rot,
            # location=(0.0, -0.07, 0.035),
            # location=(0.0, 0, -2),
            location=(self.face.trans[0], self.face.trans[1], self.face.trans[2]),
            url=self.model_path,
            parent="camera_"+self.user_id,
            data=morphStr
        )
