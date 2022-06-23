
import sys
import time
import json
import arena
import re
import math

HOST = "mqtt.arenaxr.org"
SCENE = "roomtest5"

sign_links =  ['Link 1','https://3dwarehouse.sketchup.com/model/f2991e0c12644c9ff87d99a411d2b1c5/University-of-Southern-California-USC-Tower?hl=en','Link 2','https://www.f1.com','Link 3','https://www.eet.com']

waypoints = []
waypoints.append((0.0, 0.2, 0.0))
waypoints.append((-15.8, 0.2, -3.0))
waypoints.append((-1.3, 0.2, 6.4))
waypoints.append((-0.5, 0.4, 33.9))
waypoints.append((-11.5, 0.2, 38.7))
waypoints.append((-18.1, 0.2, 48.7))
waypoints.append((-46.4, 0.3, 44.1))

def drawpath(waypoints, name_seed, persist ):
    print( waypoints)
    lastPt = None
    if name_seed == -1:
        pathStr = "path" + str(random.randint(0, 1000000))
    else:
        pathStr = "path" + str(name_seed)
    stepCnt=0
    for pt in waypoints:
        if lastPt is None:
            lastPt = pt
            continue
        dist = math.sqrt( ((pt[0]-lastPt[0])*(pt[0]-lastPt[0]))+((pt[1]-lastPt[1])*(pt[1]-lastPt[1])) +((pt[2]-lastPt[2])*(pt[2]-lastPt[2]))  )
        totalSteps = int(dist / 0.3)
        stepX = (pt[0]-lastPt[0])/(totalSteps)
        stepY = (pt[1]-lastPt[1])/(totalSteps)
        stepZ = (pt[2]-lastPt[2])/(totalSteps)
        for i in range(0,totalSteps):
            x=lastPt[0]+i*stepX
            y=lastPt[1]+i*stepY
            z=lastPt[2]+i*stepZ
            pathobjstr = pathStr + str(stepCnt)
            stepCnt+=1
            arena.Object(objType=arena.Shape.circle,
            objName=pathobjstr,
            location=(x,y,z),
            color=(0,255,255),scale=(0.1,0.1,1),
            rotation=(-0.7,0.0,0.0,0.7),
            data='{"material": {"transparent":true,"opacity": 0.3}}',
            persist=persist);
        lastPt = pt


def signs():
    arena.Object(
            objName="signpost1",
            url="store/users/wiselab/models/signpost/scene.gltf",
            objType=arena.Shape.gltf_model,
            scale=(0.1, 0.1, 0.1),
            rotation=(0, 0.3, 0, 1),
            location=(-18.2, 0.2, -2.3),
            clickable=True,
            persist=True
    )


arena.init(HOST, "realm", SCENE)


print("starting main loop")
drawpath(waypoints, 0, True)
signs()
arena.handle_events()
