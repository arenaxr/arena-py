import time
import json
import random
import arena

HOST = "oz.andrew.cmu.edu"
REALM = "realm"
SCENE = "face-test"

users = {}

SCALE_FACTOR = 100

class FacePart(object):
    def __init__(self, obj_id, name, width, height, pts, closed=True):
        self.obj_id = obj_id
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
                    users[self.obj_id]["color"]
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
            self.create_line(self.pts[i], self.pts[i+1], self.name+str(i)+self.obj_id)
        if closed:
            # connect the first and last point for closed shapes
            self.create_line(self.pts[0], self.pts[-1], self.name+str(i+1)+self.obj_id)

def callback(msg):
    msg_json = json.loads(msg)
    if "hasFace" in msg_json and msg_json["hasFace"]:
        landmarksRaw = msg_json["landmarks"] # [x1, y1, x2, y2...]

        landmarks = [] # [[x1, y1], [x2, y2], ...]
        for i in range(0, len(landmarksRaw), 2):
            landmarks += [[landmarksRaw[i], landmarksRaw[i+1]]]

        width = msg_json["image"]["width"]
        height = msg_json["image"]["height"]

        quat = msg_json["pose"]["quaterions"]
        trans = msg_json["pose"]["translation"]

        # print(quat, trans)

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

        obj_id = msg_json["object_id"]

        if obj_id not in users:
            users[obj_id] = {}
            users[obj_id]["color"] = "#"+str(hex(random.randint(0,0xffffff)))[2:]

        # print(obj_id, users)

        if "jaw" not in users[obj_id]:
            users[obj_id]["jaw"] = FacePart(obj_id, "jaw", width, height, jawPts, False)
        else:
            users[obj_id]["jaw"].update(jawPts, False)

        if "eyebrowL" not in users[obj_id]:
            users[obj_id]["eyebrowL"] = FacePart(obj_id, "eyebrowL", width, height, eyebrowLPts, False)
        else:
            users[obj_id]["eyebrowL"].update(eyebrowLPts, False)

        if "eyebrowR" not in users[obj_id]:
            users[obj_id]["eyebrowR"] = FacePart(obj_id, "eyebrowR", width, height, eyebrowRPts, False)
        else:
            users[obj_id]["eyebrowR"].update(eyebrowRPts, False)

        if "noseBridge" not in users[obj_id]:
            users[obj_id]["noseBridge"] = FacePart(obj_id, "noseBridge", width, height, noseBridgePts, False)
        else:
            users[obj_id]["noseBridge"].update(noseBridgePts, False)

        if "noseLower" not in users[obj_id]:
            users[obj_id]["noseLower"] = FacePart(obj_id, "noseLower", width, height, noseLowerPts)
        else:
            users[obj_id]["noseLower"].update(noseLowerPts)

        if "eyeL" not in users[obj_id]:
            users[obj_id]["eyeL"] = FacePart(obj_id, "eyeL", width, height, eyeLPts)
        else:
            users[obj_id]["eyeL"].update(eyeLPts)

        if "eyeR" not in users[obj_id]:
            users[obj_id]["eyeR"] = FacePart(obj_id, "eyeR", width, height, eyeRPts)
        else:
            users[obj_id]["eyeR"].update(eyeRPts)

        if "lipOuter" not in users[obj_id]:
            users[obj_id]["lipOuter"] = FacePart(obj_id, "lipOuter", width, height, lipOuterPts)
        else:
            users[obj_id]["lipOuter"].update(lipOuterPts)

        if "lipInner" not in users[obj_id]:
            users[obj_id]["lipInner"] = FacePart(obj_id, "lipInner", width, height, lipInnerPts)
        else:
            users[obj_id]["lipInner"].update(lipInnerPts)

arena.init(HOST, REALM, SCENE, callback=callback)
arena.handle_events()
