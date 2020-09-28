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
SCENE = "arena-meeting"
REALM = "realm"
MQTTH = "arena.andrew.cmu.edu"

# init the ARENA library
arena.init(MQTTH, REALM, SCENE)

pindex=1

whiteboard = arena.Object(
            objName="whiteboard_" + str(pindex),
            url="store/users/wiselab/posters/whiteboard_modern/scene.gltf",
            objType=arena.Shape.gltf_model,
            scale=(0.03, 0.03, 0.02), 
            location=(0, 1.19, -1.2),
            rotation=(0.0, 1, 0.0, 0.0),
            clickable=True,
            persist=True)
"""
posterimg = arena.Object(
            objName="wbimg_"+ str(pindex),
            url="store/users/wiselab/posters/CONIX-mr.png",
            objType=arena.Shape.image,
            scale=(1.5, 1.22, 1),
            location=(-0.456, 1.783, -0.4),
            rotation=(-0.086, -0.702, -0.086 , 0.702),
            clickable=True,
            persist=True)    
"""

lht = arena.Object(
                objName="myLight",
                objType=arena.Shape.light,
                location=(-1, 1.5, -0.50),
                rotation=(0, 0, 0, 1),                
                color=(50, 50, 50),
                persist=True)

"""
{
  "object_id": "wbimg_1",
  "action": "update",
  "type": "object",
  "persist": true,
  "data": {
    "object_type": "image",
    "position": {
      "x": -0.456,
      "y": 1.783,
      "z": -0.007
    },
    "rotation": {
      "x": -0.086,
      "y": -0.702,
      "z": -0.086,
      "w": 0.702
    },
    "scale": {
      "x": 1.7,
      "y": 1.22,
      "z": 1.21
    },
    "color": "#ffffff",
    "url": "store/users/wiselab/posters/CONIX-mr.png",
    "click-listener": false
  }
}
"""

"""
text1 = arena.Object(
                objName="text1",
                objType=arena.Shape.text,
                scale=(0.5,0.5,0.5),
                location=(-0.027, .93, 0.0),
                rotation=(0.0, 0.707, 0.0 , -0.707),
                clickable=False,
                data='{"text":"'+'test'+'"}',
                color=(252, 132, 3),
                parent="whiteboard_" + str(pindex),
		        persist=True) 

lht = arena.Object(
                objName="myLight",
                objType=arena.Shape.light,
                location=(-1, 1.5, 0.0),
                rotation=(0, 0, 0, 1),                
                color=(50, 50, 50),
                parent="whiteboard_" + str(pindex))
"""

# move the group of objects
#agentParent.update(location=(3, 0, -10))

# This is the main ARENA event handler
# Everything after this should be in callbacks
print("starting main loop")
arena.handle_events()

#agentParent.delete()

