# poster placement
#

import time
import arena
import random
import os
import json

import atexit

# To run in ARTS, these parameters are passed in as environmental variables.
# export SCENE=thescene
# export REALM=realm
# export MQTTH=arena.andrew.cmu.edu

def agent_handler(event=None):
    global agent1
    global agentParent
    print("agent handler callback!")


# Pull in the SCENE, MQTT and REALM parameters from environmental variables
# TODO: Add commandline overide
# if (os.environ.get('SCENE') is not None) and (os.environ.get('REALM') is not None) and (os.environ.get('MQTTH') is not None):
#    SCENE = os.environ["SCENE"]
#    HOST = os.environ["MQTTH"]
#    REALM = os.environ["REALM"]
#    print("Loading:" + SCENE + "," + REALM + "," + HOST)
# else:
#    print( "You need to set SCENE, MQTTH and REALM as environmental variables to specify the program target")
#    exit(-1)
SCENE = "newtest"
REALM = "realm"
MQTTH = "arena.andrew.cmu.edu"

# init the ARENA library
arena.init(MQTTH, REALM, SCENE)

posterData=None
with open('poster-data.json') as dataFile:
    posterData = json.load(dataFile)

theme=1
pindex=0
dist=15
persist=True
originx=0
originz=0
postermodel=2 # 1= whiteboard model; 2="modern" whiteboard frame

pcount=0
for poster in posterData:
    print(poster['name'], poster['theme'])
    if (poster['theme']==theme):
        pcount+=1

if pcount <= 4:
    gridSize=3
elif pcount <= 9:
    gridSize=3  
elif pcount <= 16:
    gridSize=4  
elif pcount <= 25:
    gridSize=5
elif pcount <= 36:
    gridSize=6
        
print("theme=", theme, "pcount=", pcount, "gridSize=", gridSize)

for poster in posterData:
    if (poster['theme']==theme):
        print(poster['name'], poster['theme'])

        l = pindex % gridSize
        c = pindex // gridSize

        pindex+=1
        
        print(l, c)

        wbaName="theme_" + str(theme) + "_wbassembly_" + str(pindex)
        wbName="theme_" + str(theme) + "_whiteboard_" + str(pindex)
        imgName="theme_" + str(theme) + "_wbimg_" + str(pindex)
        lblName="theme_" + str(theme) + "_label_" + str(pindex)
        lhtName="theme_" + str(theme) + "_light_" + str(pindex)

        # 1= whiteboard model
        if postermodel==1:
            wba = arena.Object(
                objName=wbaName,
                objType=arena.Shape.plane,
                scale=(1.1, 1.1, 1.1),
                location=(originx + (l * dist) , 0, originz + (c * dist)),
                rotation=(0.707, 0.0, 0.0 , 0.707),
                clickable=True,
                persist=persist)
                    
            wb = arena.Object(
                objName=wbName,
                url="store/users/wiselab/posters/whiteboard/scene.gltf",
                objType=arena.Shape.gltf_model,
                scale=(1, 0.94, 0.54), 
                location=(0, 0, 0),
                rotation=(-0.707, 0.0, 0.0 , 0.707),
                clickable=True,
                parent=wbaName,
                persist=persist)

            pimg = arena.Object(
                objName=imgName,
                url="store/users/wiselab/posters/CONIX-mr.png",
                objType=arena.Shape.image,
                scale=(1.6, 1.12, 1.12),
                location=(-0.021, 1.55, 0.002),
                rotation=(0.0, 0.707, 0.0 , -0.707),
                clickable=True,
                parent=wbName,
                persist=persist)        
            
            txt = arena.Object(
                    objName=lblName,
                    objType=arena.Shape.text,
                    scale=(0.5,0.5,0.5),
                    location=(-0.030, .93, 0.0),
                    rotation=(0.0, 0.707, 0.0 , -0.707),
                    clickable=False,
                    data='{"text":"'+'Theme' + str(theme) + '"}',
                    color=(252, 132, 3),
                    parent=wbName,
                    persist=persist)   

            lht = arena.Object(
                    objName=lhtName,
                    objType=arena.Shape.light,
                    location=(-1, 1.5, 0.0),
                    rotation=(0, 0, 0, 1),                
                    color=(50, 50, 50),
                    parent=wbName,
                    persist=persist)
            
            # 2="modern" whiteboard frame
        if postermodel==2:
                wb = arena.Object(
                    objName=wbName,
                    url="store/users/wiselab/posters/whiteboard_modern/scene.gltf",
                    objType=arena.Shape.gltf_model,
                    scale=(0.03, 0.03, 0.02), 
                    location=(originx + (l * dist), 1.19, -1.2 + originz + (c * dist)),
                    rotation=(0.0, 1, 0.0, 0.0),
                    clickable=True,
                    persist=persist)

                pimg = arena.Object(
                    objName=imgName,
                    url="store/users/wiselab/posters/CONIX-mr.png",
                    objType=arena.Shape.image,
                    scale=(1.5, 1.22, 0.8),
                    location=(-0.456+   originx + (l * dist), 1.783, -0.4 +  originz + (c * dist)),
                    rotation=(-0.086, -0.702, -0.086 , 0.702),
                    clickable=True,
                    persist=persist)       

                lht = arena.Object(
                    objName=lhtName,
                    objType=arena.Shape.light,
                    location=(-1 + originx + (l * dist), 1.5, -0.50 +  originz + (c * dist)),
                    rotation=(0, 0, 0, 1),                
                    color=(50, 50, 50),
                    persist=persist)       
                                      

# move the group of objects
#agentParent.update(location=(3, 0, -10))

# This is the main ARENA event handler
# Everything after this should be in callbacks
print("starting main loop")
arena.handle_events()

#agentParent.delete()

