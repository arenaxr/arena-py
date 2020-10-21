
import sys
import time
import json
import arena
import re
import math

HOST = "arena.andrew.cmu.edu"
SCENE = "roomtest5"

waypoints = []
waypoints.append((0.0,0.1,0.0))
waypoints.append((-14.8,0.1,-1.4))
waypoints.append((-10.8,0.1,5.3))
waypoints.append((-9.8,0.1,37.1))
waypoints.append((-16.3,0.1,18.8))

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
            color=(0,255,255),scale=(0.1,0.1,0.1),
            rotation=(-0.7,0.0,0.0,0.7), 
            data='{"material": {"transparent":true,"opacity": 0.3}}', 
            persist=persist);
        lastPt = pt 


arena.init(HOST, "realm", SCENE)


print("starting main loop")
drawpath(waypoints, 0, True)
arena.handle_events()
