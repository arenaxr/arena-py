import random
import time
import signal
import json
import arena

HOST = "oz.andrew.cmu.edu"
REALM = "realm"
SCENE = "face-test"

users = {}

SCALE_FACTOR = 100

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


def callback(msg):
    msg_json = json.loads(msg)
    if "hasFace" in msg_json and msg_json["hasFace"]:
        ID = msg_json["object_id"]
        landmarksRaw = msg_json["landmarks"] # [x1, y1, x2, y2...]

        landmarks = [] # [[x1, y1], [x2, y2], ...]
        for i in range(0, len(landmarksRaw), 2):
            landmarks += [[landmarksRaw[i], landmarksRaw[i+1]]]

        width = msg_json["imWidth"]
        height = msg_json["imHeight"]

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

        xmin,ymin,xmax,ymax = minmax(lipOuterPts)
        #  boxPts = [[xmin,ymin],[xmin,ymax],[xmax,ymax],[xmax,ymin]]
        # print("outer mouth box size:", xmin, ymin, xmax, ymax);
        # print("scale:", xmax-xmin, ymax-ymin)
        openness = ((xmax-xmin) / (ymax-ymin)) / 10
        print (openness)
        # animate the face of existing model 'izzy'
        obj = arena.updateBone(
            object_id="izzy",
            rotation=(0,0,0.6-openness,1), # quaternion value roughly between -.05 and .05
            bone_id = "CC_Base_JawRoot_092"
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
            

arena.init(HOST, REALM, SCENE, callback=callback)
arena.handle_events()
