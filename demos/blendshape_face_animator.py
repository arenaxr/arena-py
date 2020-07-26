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
SCENE = "sampledata"
OBJECT = "face"

users = {}
SCALE_FACTOR = 100


anims=[
    "blendShape1.browInnerUp",
    "blendShape1.browDown_L",
    "blendShape1.browDown_R",
    "blendShape1.browOuterUp_L",
    "blendShape1.browOuterUp_R",
    "blendShape1.eyeLookUp_L",
    "blendShape1.eyeLookUp_R",
    "blendShape1.eyeLookDown_L",
    "blendShape1.eyeLookDown_R",
    "blendShape1.eyeLookIn_L",
    "blendShape1.eyeLookIn_R",
    "blendShape1.eyeLookOut_L",
    "blendShape1.eyeLookOut_R",
    "blendShape1.eyeBlink_L",
    "blendShape1.eyeBlink_R",
    "blendShape1.eyeSquint_L",
    "blendShape1.eyeSquint_R",
    "blendShape1.eyeWide_L",
    "blendShape1.eyeWide_R",
    "blendShape1.cheekPuff",
    "blendShape1.cheekSquint_L",
    "blendShape1.cheekSquint_R",
    "blendShape1.noseSneer_L",
    "blendShape1.noseSneer_R",
    "blendShape1.jawOpen",
    "blendShape1.jawForward",
    "blendShape1.jawLeft",
    "blendShape1.jawRight",
    "blendShape1.mouthFunnel",
    "blendShape1.mouthPucker",
    "blendShape1.mouthLeft",
    "blendShape1.mouthRight",
    "blendShape1.mouthRollUpper",
    "blendShape1.mouthRollLower",
    "blendShape1.mouthShrugUpper",
    "blendShape1.mouthShrugLower",
    "blendShape1.mouthClose",
    "blendShape1.mouthSmile_L",
    "blendShape1.mouthSmile_R",
    "blendShape1.mouthFrown_L",
    "blendShape1.mouthFrown_R",
    "blendShape1.mouthDimple_L",
    "blendShape1.mouthDimple_R",
    "blendShape1.mouthUpperUp_L",
    "blendShape1.mouthUpperUp_R",
    "blendShape1.mouthLowerDown_L",
    "blendShape1.mouthLowerDown_R",
    "blendShape1.mouthPress_L",
    "blendShape1.mouthPress_R",
    "blendShape1.mouthStretch_L",
    "blendShape1.mouthStretch_R",
]


class FacePart(object):
    def __init__(self, ID, name, width, height, pts, closed=True):
        self.ID = ID
        self.name = name
        self.width = 2 * width / SCALE_FACTOR # scale it down, but make it 2x bigger
        self.height = 2 * height / SCALE_FACTOR
        self.lines = []
        self.update(pts, closed)

    def create_line(self, pts1, pts2, name):
        x1 = float(pts1[0]) * self.width
        y1 = float(pts1[1]) * self.height + self.height
        x2 = float(pts2[0]) * self.width
        y2 = float(pts2[1]) * self.height + self.height

        line = arena.Line(
                    (x1,y1,-0.5),
                    (x2,y2,-0.5),
                    2,
                    users[self.ID]["color"]
                )
        arena.Object(
            objName=name,
            objType=arena.Shape.line,
            line=line,
            persist=False
        )

    def update(self, pts, closed=True):
        self.pts = pts
        for i in range(0, len(self.pts)-1):
            self.create_line(self.pts[i], self.pts[i+1], self.name+str(i)+self.ID)
        if closed:
            # connect the first and last point for closed shapes
            self.create_line(self.pts[0], self.pts[-1], self.name+str(i+1)+self.ID)

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


counter = 0

def callback(msg):
    global counter
    msg_json = json.loads(msg)
    if "hasFace" in msg_json and msg_json["hasFace"]:
        ID = msg_json["object_id"]
        landmarksRaw = msg_json["landmarks"] # [x1, y1, x2, y2...]

        landmarks = [] # [[x1, y1], [x2, y2], ...]
        for i in range(0, len(landmarksRaw), 2):
            landmarks += [[landmarksRaw[i], landmarksRaw[i+1]]]

        #width = msg_json["width"]
        #height = msg_json["height"]
        width=320
        height=240

        bboxx = msg_json["bbox"][0]
        bboxy = msg_json["bbox"][1]
        bboxX = msg_json["bbox"][2]
        bboxY = msg_json["bbox"][3]
        boxPts = [[bboxx,bboxy],[bboxX,bboxY]]

        # print("bbox size:", bboxx, bboxy, bboxX, bboxY)

        # print(landmarks, width, height)

        jawPts = landmarks[0:17]
        eyebrowLPts = landmarks[17:22]
        eyebrowRPts = landmarks[22:27]
        noseBridgePts = landmarks[27:31]
        noseLowerPts = landmarks[30:36] # both parts of nose are connected, so index is 30:36 and not 31:36
        eyeLPts = landmarks[36:42]
        eyeRPts = landmarks[42:48]
        lipOuterPts = landmarks[48:60]
        lipInnerPts = landmarks[60:68]


        print( eyebrowLPts )
        xmin,ymin,xmax,ymax = minmax(lipOuterPts)
        #  boxPts = [[xmin,ymin],[xmin,ymax],[xmax,ymax],[xmax,ymin]]
        # print("outer mouth box size:", xmin, ymin, xmax, ymax);
        # print("scale:", xmax-xmin, ymax-ymin)
        openness = ((xmax-xmin) / (ymax-ymin)) / 10
        print (openness)



        # Grab some point to normalize features with distance
        # Not sure if width of face is good?
        faceWidth = distance.euclidean(landmarks[1],landmarks[15])
        print ("FaceWidth", faceWidth)


        # Outer Brow is set as a normalized scaler compared to face width
        browOuterUp_L = distance.euclidean(landmarks[19],landmarks[37]) 
        browOuterUp_R = distance.euclidean(landmarks[44],landmarks[24]) 

        print( "Raw Brow Left:" , browOuterUp_L )
        print( "Raw Brow Right:" , browOuterUp_R )

        browOuterScalar = 10.0
        browOuterUp_L -= 0.04
        browOuterUp_R -= 0.04
        
        browOuterUp_L = (browOuterUp_L/faceWidth) * browOuterScalar 
        browOuterUp_R = (browOuterUp_R/faceWidth) * browOuterScalar 

        if browOuterUp_L < 0:
            browOuterUp_L = 0

        if browOuterUp_R < 0:
            browOuterUp_R = 0

        print( "Brow Left:" , browOuterUp_L )
        print( "Brow Right:" , browOuterUp_R )


        # Eye blink is set as a normalized scaler compared to face width
        # and then thresholded
        eyeScalar = 1.0
        eyeThresh = 0.2

        eyeRight = distance.euclidean(landmarks[44],landmarks[46])
        eyeLeft = distance.euclidean(landmarks[37],landmarks[41])
        
        eyeRight = (eyeRight/faceWidth) * eyeScalar 
        eyeLeft = (eyeLeft/faceWidth) * eyeScalar 

        if eyeLeft < 0.04:
            eyeLeft = 1.0
        else:
            eyeLeft = 0.0

        if eyeRight< 0.04:
            eyeRight = 1.0
        else:
            eyeRight = 0.0

        # Mouth is set as a normalized scaler compared to face width
        mouthRight = distance.euclidean(landmarks[63],landmarks[65])
        mouthLeft = distance.euclidean(landmarks[61],landmarks[67])
        mouthPucker = distance.euclidean(landmarks[48],landmarks[54])

        mouthScalar = 5.0
        mouthThresh = 0.2

        mouthRight = (mouthRight/faceWidth) * mouthScalar 
        mouthLeft = (mouthLeft/faceWidth) * mouthScalar 
        mouthPucker = (mouthPucker/faceWidth) 
        print( "RawPucker: ", mouthPucker )
        mouthPucker -= 0.35 # remove DC offset
        if mouthPucker < 0.0:
            mouthPucker = 0.0
        mouthPucker *= 2
        mouthPucker = 1.0 - mouthPucker # Inver it
        mouthPucker = 0.0
        print( "MouthPucker: ", mouthPucker )

        if mouthRight < mouthThresh:
            mouthRight = 0.0
        if mouthLeft < mouthThresh:
            mouthLeft = 0.0




        morphStr ='{ "gltf-morph": {"morphtarget": "blendShape1.mouthUpperUp_L", "value": "' + str(mouthLeft) + '" },'
        morphStr += '"gltf-morph__2": {"morphtarget": "blendShape1.mouthUpperUp_R", "value": "' + str(mouthRight) + '" },'
        morphStr += '"gltf-morph__3": {"morphtarget": "blendShape1.mouthLowerDown_L", "value": "' + str(mouthLeft) + '" },'
        morphStr += '"gltf-morph__4": {"morphtarget": "blendShape1.mouthLowerDown_R", "value": "' + str(mouthRight) + '" },'
        morphStr += '"gltf-morph__5": {"morphtarget": "blendShape1.eyeBlink_L", "value": "' + str(eyeLeft) + '" },'
        morphStr += '"gltf-morph__6": {"morphtarget": "blendShape1.eyeBlink_R", "value": "' + str(eyeRight) + '" },'
        morphStr += '"gltf-morph__7": {"morphtarget": "blendShape1.browOuterUp_L", "value": "' + str(browOuterUp_L) + '" },'
        morphStr += '"gltf-morph__8": {"morphtarget": "blendShape1.browOuterUp_R", "value": "' + str(browOuterUp_R) + '" },'
        morphStr += '"gltf-morph__9": {"morphtarget": "blendShape1.mouthPucker", "value": "' + str(mouthPucker) + '" }'
        morphStr += '}'




        print(morphStr)
        obj = arena.Object(
            rotation=(0,0,0.0,1), # quaternion value roughly between -.05 and .05
 #           rotation=(0,0,0.6-openness,1), # quaternion value roughly between -.05 and .05
            objName=OBJECT,
#           url="models/Facegltf/sampledata.gltf", 
            objType=arena.Shape.gltf_model,
            scale=(40,40,40),
            location=(0,3,10),
            data = morphStr
        )
        
        
        if id not in users:
            users[ID] = {}
            users[ID]["color"] = "#"+str(hex(random.randint(0,0xffffff)))[2:]

        # print(id, users)

        # if "box" not in users[ID]:
        #     users[ID]["box"] = FacePart(ID, "box", width, height, boxPts, True) # closed
        # else:
        #     users[ID]["box"].update(boxPts, False)

        # if "jaw" not in users[ID]:
        #     users[ID]["jaw"] = FacePart(ID, "jaw", width, height, jawPts, False)
        # else:
        #     users[ID]["jaw"].update(jawPts, False)

        # if "eyebrowL" not in users[ID]:
        #     users[ID]["eyebrowL"] = FacePart(ID, "eyebrowL", width, height, eyebrowLPts, False)
        # else:
        #     users[ID]["eyebrowL"].update(eyebrowLPts, False)

        # if "eyebrowR" not in users[ID]:
        #     users[ID]["eyebrowR"] = FacePart(ID, "eyebrowR", width, height, eyebrowRPts, False)
        # else:
        #     users[ID]["eyebrowR"].update(eyebrowRPts, False)

        # if "noseBridge" not in users[ID]:
        #     users[ID]["noseBridge"] = FacePart(ID, "noseBridge", width, height, noseBridgePts, False)
        # else:
        #     users[ID]["noseBridge"].update(noseBridgePts, False)

        # if "noseLower" not in users[ID]:
        #     users[ID]["noseLower"] = FacePart(ID, "noseLower", width, height, noseLowerPts)
        # else:
        #     users[ID]["noseLower"].update(noseLowerPts)

        # if "eyeL" not in users[ID]:
        #     users[ID]["eyeL"] = FacePart(ID, "eyeL", width, height, eyeLPts)
        # else:
        #     users[ID]["eyeL"].update(eyeLPts)

        # if "eyeR" not in users[ID]:
        #     users[ID]["eyeR"] = FacePart(ID, "eyeR", width, height, eyeRPts)
        # else:
        #     users[ID]["eyeR"].update(eyeRPts)

        # if "lipOuter" not in users[ID]:
        #     users[ID]["lipOuter"] = FacePart(ID, "lipOuter", width, height, lipOuterPts)
        # else:
        #     users[ID]["lipOuter"].update(lipOuterPts)

        # if "lipInner" not in users[ID]:
        #     users[ID]["lipInner"] = FacePart(ID, "lipInner", width, height, lipInnerPts)
        # else:
        #     users[ID]["lipInner"].update(lipInnerPts)
            





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

