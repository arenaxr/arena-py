from arena import *
import numpy as np
from scipy.spatial import distance

from utils import MeanFilter
from face import Face

EXP_HIST_WINDOW = 3

EYE_THRES   = 0.17
MOUTH_THRES = 0.05

class HeadRig(object):
    def __init__(self, user_id, scene, camera):
        self.user_id = user_id
        self.scene = scene
        self.camera = camera
        self.faceObj = None

        self.model_path = "/store/users/wiselab/models/FaceCapHeadGeneric/FaceCapHeadGeneric.gltf"

        self.rig_enabled = True

        self.avatar = None

        self.exp_filter = MeanFilter(EXP_HIST_WINDOW)

        self.anims = [
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

    @property
    def has_avatar(self):
        return "hasAvatar" in self.camera and self.camera.hasAvatar

    def rig_on(self):
        self.rig_enabled = True

    def rig_off(self):
        if self.rig_enabled and self.avatar:
            self.scene.delete_object(self.avatar)
        self.rig_enabled = False

    def add_face(self, faceObj):
        self.faceObj = faceObj
        self.face = Face()

    def create_morph(self, exp_vect):
        morph = {}
        for i in range(len(exp_vect)-2):
            if "blink" in self.anims[i].lower():
                exp_vect[i] = exp_vect[i]*0.3
            morph["gltf-morph__" + str(i)] = {
                    "morphtarget": self.anims[i],
                    "value": str(round(exp_vect[i],3))
                }
        i = len(exp_vect) - 1
        morph["gltf-morph__" + str(i)] = {
                    "morphtarget": self.anims[i],
                    "value": "0.0"
                }
        return morph

    def update(self):
        if self.faceObj is None: return
        if not self.faceObj.data.hasFace: return

        self.face.update(self.faceObj.data)

        expressions_vect = self.face.get_expressions_vect()
        expressions_vect = expressions_vect.reshape((-1,))
        expressions_vect = self.exp_filter.add(expressions_vect)

        morph = self.create_morph(expressions_vect)

        if self.avatar is None:
            self.avatar = GLTF(
                    object_id=f"avatar_{self.user_id}",
                    url=self.model_path,
                    # position=(0.0, -0.07, 0.035),
                    # position=(0.0, 0, -2),
                    position=self.face.trans,
                    rotation=self.face.rot,
                    scale=(3,3,3),
                    parent="camera_"+self.user_id,
                    **morph
                )
            self.scene.add_object(self.avatar)
        else:
            self.avatar.update_attributes(
                    position=self.face.trans,
                    rotation=self.face.rot,
                    **morph
                )
            self.scene.update_object(self.avatar)
