# robot-arm.py
#

import time
import arena
import random
import os
import json 

pinata_loc = [ 3, 2, -10]
hit_counter = 0

# To run in ARTS, these parameters are passed in as environmental variables.
# export HOST=arena.andrew.cmu.edu
# export REALM=realm
# export MQTTH=arena.andrew.cmu.edu

# This function draws a line when a user clicks
def draw_ray(click_pos, position):
    line = arena.Object(
        #objName="line1",
        ttl=1,
        objType=arena.Shape.thickline,
        thickline=arena.Thickline( # slightly below camera so you can see line vs head-on
            {
                (click_pos[0],click_pos[1]-0.2,click_pos[2]),
                (position[0],position[1],position[2])
            },5,"#FF00FF")
    )

animateState = False


def pinata_handler(event=None):
    global pinata1 
    global text1 
    global pinataParent
    global hit_counter 
    print("pinata hit handler callback!")
    if event.event_type == arena.EventType.mouseenter:
        # Make it transparent on hover over
        pinata1.update(transparency=arena.Transparency(True, 0.1)  )
    if event.event_type == arena.EventType.mouseleave:
        # Make it opaque, you can add color or other properties in the list
        pinata1.update(transparency=arena.Transparency(True, 1.0) )
    if event.event_type == arena.EventType.mousedown:
        # On click, draw a ray
        draw_ray(event.click_pos, event.position)
        pinata1.update(transparency=arena.Transparency(True, 1.0) )
        #pinataParent.update(location=(random.randrange(-10,10) , 0 , random.randrange(-10,1)) )
        # Need to add Tweening...
        pinataParent.update(location=(pinata_loc[0],pinata_loc[1],pinata_loc[2]))
        pinata_loc[0]=random.uniform(0,10)
        pinata_loc[1]=random.uniform(0,10)
        pinata_loc[2]=random.uniform(0,10)
        pinataParent.update(data='{"animation": {"property": "position","to": "' + str(pinata_loc[0]) + ' ' + str(pinata_loc[1]) + ' ' + str(pinata_loc[2]) + '","easing": "linear","dur": 250}}')
        hit_counter = hit_counter + 1

        text1 = arena.Object(
                objName="text1",
                objType=arena.Shape.text,
                scale=(5.0,5.0,5.0),
                location=( 0,7,0),
                rotation=( 0,0,0,1),
                #clickable=False,
                data='{"text":"Hit Counter ' + str(hit_counter) + '"}',
                color=(100,100,255),
		        persist=True,
                parent="pinataParent"
            )


# Pull in the SCENE, MQTT and REALM parameters from environmental variables 
# TODO: Add commandline overide
if (os.environ.get('SCENE') is not None) and (os.environ.get('REALM') is not None) and (os.environ.get('MQTTH') is not None):
    SCENE = os.environ["SCENE"]
    HOST = os.environ["MQTTH"]
    REALM = os.environ["REALM"]
    print("Loading:" + SCENE + "," + REALM + "," + HOST)
else:
    print( "You need to set SCENE, MQTTH and REALM as environmental variables to specify the program target")
    exit(-1)

# init the ARENA library
arena.init(HOST, REALM, SCENE)

print("starting sign main loop")

# 
pinataParent = arena.Object(
    persist=True,
    objName="pinataParent",
    objType=arena.Shape.cube,
    location=(0, 0, 0),
    transparency=arena.Transparency(True, 0),
)


pinata1 = arena.Object(
                objName="pinata-model",
                url="store/users/wiselab/models/fortnite_llama/scene.gltf",
                objType=arena.Shape.gltf_model,
                scale=(0.01,0.01,0.01),
                location=(0,0,0),
                clickable=True,
		        persist=True,
                parent="pinataParent",
                callback=pinata_handler
)

text1 = arena.Object(
                objName="text1",
                objType=arena.Shape.text,
                scale=(5.0,5.0,5.0),
                location=( 0,7,0),
                rotation=( 0,0,0,1),
                clickable=False,
                data='{"text":"Click Me!"}',
                color=(100,100,255),
		        persist=True,
                parent="pinataParent"
)


# move the group of objects
pinataParent.update(location=(pinata_loc[0],pinata_loc[1],pinata_loc[2]))


# This is the main ARENA event handler
# Everything after this should be in callbacks
arena.handle_events()
