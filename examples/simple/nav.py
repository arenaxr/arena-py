"""Path Navigation
"""

import math
import random
import sys
import time

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

color = (0, 255, 0)

# more complex case: Create many boxes

x = 1

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
            cyl = Cylinder(
                position = (x,y,z),
                color=(0,255,255),
                scale=(0.1,0.05,0.1),
                material=Material(transparent=True, opacity=0.5),
            	persist=persist
            )
            scene.add_object(cyl)
        lastPt = pt

def click_handler(scene,evt,msg):
    if evt.type =="mouseup":
        waypoints = []
        waypoints.append( (18.9, -3.05,-12.3))
        waypoints.append((18.9, -4.147,-12.0))
        waypoints.append((17.4, -4.147,-15.4))
        waypoints.append((14.95,-4.1,-16.0))
        waypoints.append((11.6,-1.8,-17.1))
        waypoints.append((10.64,-1.8,-17.46))
        waypoints.append((7.1,0.1,-18.6))
        waypoints.append((5.7,0.1,-19.2))
        waypoints.append((5.6,0.1,-13.5))
        drawpath( waypoints,-1, False)



#@scene.run_forever(interval_ms=500)
@scene.run_once
def draw_waypoints():

    cyl = Cylinder(
        position = (18.9, -3.05,-12.3),
        color=(0,255,255),
        scale=(0.03,0.03,0.03),
        material=Material(transparent=True, opacity=0.1),
        evt_handler=click_handler,
        clickable=True
    )
    scene.add_object(cyl)

scene.run_tasks()
