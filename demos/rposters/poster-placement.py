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
SCENE = "pbtest"
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
    print(poster['name'], poster['theme'])
    if (poster['theme']==theme):

        l = pindex % gridSize
        c = pindex // gridSize

        pindex+=1
        
        print(l, c)

        wbaName="theme_" + str(theme) + "_wbassembly_" + str(pindex)
        wbName="theme_" + str(theme) + "_whiteboard_" + str(pindex)
        imgName="theme_" + str(theme) + "_wbimg_" + str(pindex)
        lblName="theme_" + str(theme) + "_label_" + str(pindex)
        lhtName="theme_" + str(theme) + "_light_" + str(pindex)
        
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
                parent=wbName)

"""            
postercnt=1
wbassembly = arena.Object(
            objName="wbassembly_" + str(postercnt),
            objType=arena.Shape.plane,
            scale=(1.1, 1.1, 1.1),
            location=(0, 0, 0),
            rotation=(0.707, 0.0, 0.0 , 0.707),
            clickable=True,
            persist=True)

whiteboard = arena.Object(
            objName="whiteboard_" + str(postercnt),
            url="store/users/wiselab/posters/whiteboard/scene.gltf",
            objType=arena.Shape.gltf_model,
            scale=(1, 0.94, 0.54), 
            location=(0, 0, 0),
            rotation=(-0.707, 0.0, 0.0 , 0.707),
            clickable=True,
            parent="wbassembly_" + str(postercnt),
            persist=True)

posterimg = arena.Object(
            objName="wbimg_"+ str(postercnt),
            url="store/users/wiselab/posters/CONIX-mr.png",
            objType=arena.Shape.image,
            scale=(1.6, 1.12, 1.12),
            location=(-0.021, 1.55, 0.002),
            rotation=(0.0, 0.707, 0.0 , -0.707),
            clickable=True,
            parent="whiteboard_" + str(postercnt),
            persist=True)    

text1 = arena.Object(
                objName="text1",
                objType=arena.Shape.text,
                scale=(0.5,0.5,0.5),
                location=(-0.027, .93, 0.0),
                rotation=(0.0, 0.707, 0.0 , -0.707),
                clickable=False,
                data='{"text":"'+'test'+'"}',
                color=(252, 132, 3),
                parent="whiteboard_" + str(postercnt),
		        persist=True) 


light = arena.Object(
    objName="myLight",
    objType=arena.Shape.light,
    location=(-1, 0, 1.5),
    rotation=(0, 0, 0, 1),
    data='{"light":{"type":"point","intensity":"0.75"}}',
    parent="wbassembly_" + str(postercnt)
)

"""

# move the group of objects
#agentParent.update(location=(3, 0, -10))

# This is the main ARENA event handler
# Everything after this should be in callbacks
print("starting main loop")
arena.handle_events()

#agentParent.delete()

