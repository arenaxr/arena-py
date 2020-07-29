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
from scipy.spatial import distance

HOST = "oz.andrew.cmu.edu"
SCENE = "face-agr"
OBJECT = "face-agr-model"

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

def minmax(theArray):
    xmin = theArray[0][0]
    xmax = theArray[0][0]
    ymin = theArray[0][1]
    ymax = theArray[0][1]
    for i in range(1, len(theArray)):
        if theArray[i][0] < xmin:
            xmin = theArray[i][0]
        if theArray[i][0] > xmax:
            xmax = theArray[i][0]
        if theArray[i][1] < ymin:
            ymin = theArray[i][1]
        if theArray[i][1] > ymax:
            ymax = theArray[i][1]
    return(xmin,ymin,xmax,ymax)


class FaceFeatures(object):
    def __init__(self, msg_json):
        self.landmarksRaw = msg_json["landmarks"] # [x1, y1, x2, y2...]

        self.landmarks = [] # [[x1, y1], [x2, y2], ...]
        for i in range(0, len(self.landmarksRaw), 2):
            self.landmarks += [[self.landmarksRaw[i], self.landmarksRaw[i+1]]]

        self.width = msg_json["image"]["width"]
        self.height = msg_json["image"]["height"]

        bboxx = msg_json["bbox"][0]
        bboxy = msg_json["bbox"][1]
        bboxX = msg_json["bbox"][2]
        bboxY = msg_json["bbox"][3]
        self.bbox = [[bboxx,bboxy],[bboxX,bboxY]]

        self.rot = msg_json["pose"]["quaternions"]
        self.trans = msg_json["pose"]["translation"]

        self.jawPts = self.landmarks[0:17]
        self.eyebrowLPts = self.landmarks[17:22]
        self.eyebrowRPts = self.landmarks[22:27]
        self.noseBridgePts = self.landmarks[27:31]
        self.noseLowerPts = self.landmarks[30:36] # both parts of nose are connected, so index is 30:36 and not 31:36
        self.eyeLPts = self.landmarks[36:42]
        self.eyeRPts = self.landmarks[42:48]
        self.lipOuterPts = self.landmarks[48:60]
        self.lipInnerPts = self.landmarks[60:68]


counter = 0

def callback(msg):
    global counter
    msg_json = json.loads(msg)
    if "hasFace" in msg_json and msg_json["hasFace"]:
        features = FaceFeatures(msg_json)

        # print( features.eyebrowLPts )
        xmin,ymin,xmax,ymax = minmax(features.lipOuterPts)
        #  boxPts = [[xmin,ymin],[xmin,ymax],[xmax,ymax],[xmax,ymin]]
        # print("outer mouth box size:", xmin, ymin, xmax, ymax);
        # print("scale:", xmax-xmin, ymax-ymin)
        openness = ((xmax-xmin) / (ymax-ymin)) / 10
        # print (openness)


        # Grab some point to normalize features with distance
        # Not sure if width of face is good?
        faceWidth = distance.euclidean(features.landmarks[1],features.landmarks[15])
        # print ("FaceWidth", faceWidth)


        # Outer Brow is set as a normalized scaler compared to face width
        browOuterUp_L = distance.euclidean(features.landmarks[19],features.landmarks[37])
        browOuterUp_R = distance.euclidean(features.landmarks[44],features.landmarks[24])
        # print( "Raw Brow Left:" , browOuterUp_L )
        # print( "Raw Brow Right:" , browOuterUp_R )

        browOuterScalar = 10.0
        browOuterUp_L -= 0.04
        browOuterUp_R -= 0.04

        browOuterUp_L = (browOuterUp_L/faceWidth) * browOuterScalar
        browOuterUp_R = (browOuterUp_R/faceWidth) * browOuterScalar

        if browOuterUp_L < 0:
            browOuterUp_L = 0
        if browOuterUp_R < 0:
            browOuterUp_R = 0
        # print( "Brow Left:" , browOuterUp_L )
        # print( "Brow Right:" , browOuterUp_R )


        # Eye blink is set as a normalized scaler compared to face width
        # and then thresholded
        eyeScalar = 1.0
        eyeThresh = 0.2

        eyeRight = distance.euclidean(features.landmarks[44],features.landmarks[46])
        eyeLeft = distance.euclidean(features.landmarks[37],features.landmarks[41])

        eyeRight = (eyeRight/faceWidth) * eyeScalar
        eyeLeft = (eyeLeft/faceWidth) * eyeScalar

        if eyeLeft < 0.06:
            eyeLeft = 1.0
        else:
            eyeLeft = 0.0

        if eyeRight< 0.06:
            eyeRight = 1.0
        else:
            eyeRight = 0.0

        # Mouth is set as a normalized scaler compared to face width
        jawOpen = distance.euclidean(features.landmarks[62],features.landmarks[66])
        mouthRight = distance.euclidean(features.landmarks[63],features.landmarks[65])
        mouthLeft = distance.euclidean(features.landmarks[61],features.landmarks[67])
        mouthPucker = distance.euclidean(features.landmarks[48],features.landmarks[54])

        mouthScalar = 5.0
        mouthThresh = 0.2

        jawOpen = (jawOpen/faceWidth) * mouthScalar
        mouthRight = (mouthRight/faceWidth) * mouthScalar
        mouthLeft = (mouthLeft/faceWidth) * mouthScalar
        mouthPucker = (mouthPucker/faceWidth)
        # print( "RawPucker: ", mouthPucker )
        mouthPucker -= 0.35 # remove DC offset
        if mouthPucker < 0.0:
            mouthPucker = 0.0
        mouthPucker *= 2
        mouthPucker = 1.0 - mouthPucker # Invert it
        mouthPucker = 0.0
        # print( "MouthPucker: ", mouthPucker )

        if jawOpen < mouthThresh:
            jawOpen = 0.0
        if mouthRight < mouthThresh:
            mouthRight = 0.0
        if mouthLeft < mouthThresh:
            mouthLeft = 0.0


        morphStr = '{ "gltf-morph": {"morphtarget": "shapes.jawOpen", "value": "' + str(jawOpen) + '" },'
#        morphStr = '{ "gltf-morph": {"morphtarget": "shapes.mouthUpperUp_L", "value": "' + str(mouthLeft) + '" },'
#        morphStr += '"gltf-morph__2": {"morphtarget": "shapes.mouthUpperUp_R", "value": "' + str(mouthRight) + '" },'
#        morphStr += '"gltf-morph__3": {"morphtarget": "shapes.mouthLowerDown_L", "value": "' + str(mouthLeft) + '" },'
#        morphStr += '"gltf-morph__4": {"morphtarget": "shapes.mouthLowerDown_R", "value": "' + str(mouthRight) + '" },'
        morphStr += '"gltf-morph__5": {"morphtarget": "shapes.eyeBlink_L", "value": "' + str(eyeLeft) + '" },'
        morphStr += '"gltf-morph__6": {"morphtarget": "shapes.eyeBlink_R", "value": "' + str(eyeRight) + '" },'
        morphStr += '"gltf-morph__7": {"morphtarget": "shapes.browOuterUp_L", "value": "' + str(browOuterUp_L) + '" },'
        morphStr += '"gltf-morph__8": {"morphtarget": "shapes.browOuterUp_R", "value": "' + str(browOuterUp_R) + '" },'
        morphStr += '"gltf-morph__9": {"morphtarget": "shapes.mouthPucker", "value": "' + str(mouthPucker) + '" }'
        morphStr += '}'


        # print(morphStr)
        obj = arena.Object(
            rotation=features.rot, # quaternion value roughly between -.05 and .05
            location=(features.trans[0]/10, features.trans[1]/10+3, (features.trans[2]+50)/10-5),
#           rotation=(0,0,0.6-openness,1), # quaternion value roughly between -.05 and .05
            objName=OBJECT,
#           url="models/Facegltf/sampledata.gltf",
            objType=arena.Shape.gltf_model,
            scale=(15,15,15),
            # location=(0,2,-5),
            data=morphStr
        )


arena.init(HOST, "realm", SCENE, callback=callback)
arena.handle_events()

def signal_handler(sig, frame):
    exit()

signal.signal(signal.SIGINT, signal_handler)

counter = 0
while True:
    counter = counter + 1

    rando = random.random()
    anim = anims[counter % len(anims)]
    print (anim, rando)

    obj = arena.Object(
        objName=OBJECT,
#        url="models/Facegltf/sampledata.gltf",
        objType=arena.Shape.gltf_model,
        scale=(40,40,40),
        location=(0,3,10),
        data ='{"gltf-morph": {"morphtarget": "'+
        anim +
        '", "value": ' +
        str(rando) +
        '}}'
        )
    time.sleep(0.5)
exit()

