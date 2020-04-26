import json
import random
import uuid
import arena
import numpy as np
import math

# This function takes a list of (x,z) way points and draws dots at given y
# waypoints = []
# waypoints.append((-3.0,0.1,-3.0))
# waypoints.append((5.0,0.1,-2.0))
# waypoints.append((2.0,0.1,-8.0))
# drawpath(waypoints,-1, False)
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
