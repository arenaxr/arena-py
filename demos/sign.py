# robot-arm.py
#

import time
import arena
import random
import os
import json 

# export HOST=arena.andrew.cmu.edu
# export REALM=realm
# export MQTTH=arena.andrew.cmu.edu


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


def target1_handler(event=None):
    global target1 
    if event.event_type == arena.EventType.mouseenter:
        target1.update(color=(170,200,255),transparency=arena.Transparency(True, 0.5)  )
    if event.event_type == arena.EventType.mouseleave:
        target1.update(transparency=arena.Transparency(True, 0.0) )
    if event.event_type == arena.EventType.mousedown:
        draw_ray(event.click_pos, event.position)
        target1.update(transparency=arena.Transparency(True, 0.0) )


def target2_handler(event=None):
    global target2 
    if event.event_type == arena.EventType.mouseenter:
        target2.update(color=(170,200,255),transparency=arena.Transparency(True, 0.5)  )
    if event.event_type == arena.EventType.mouseleave:
        target2.update( transparency=arena.Transparency(True, 0.0) )
    if event.event_type == arena.EventType.mousedown:
        draw_ray(event.click_pos, event.position)
        target2.update( transparency=arena.Transparency(True, 0.0) )


def target3_handler(event=None):
    global target3 
    if event.event_type == arena.EventType.mouseenter:
        target3.update(color=(170,200,255),transparency=arena.Transparency(True, 0.5)  )
    if event.event_type == arena.EventType.mouseleave:
        target3.update( transparency=arena.Transparency(True, 0.0) )
    if event.event_type == arena.EventType.mousedown:
        draw_ray(event.click_pos, event.position)
        target3.update( transparency=arena.Transparency(True, 0.0) )




# start the fun shall we?

if (os.environ.get('SCENE') is not None) and (os.environ.get('REALM') is not None) and (os.environ.get('MQTTH') is not None):
    SCENE = os.environ["SCENE"]
    HOST = os.environ["MQTTH"]
    REALM = os.environ["REALM"]
    print("Loading:" + SCENE + "," + REALM + "," + HOST)
else:
    print( "You need to set SCENE, MQTTH and REALM as environmental variables to specify the program target")
    exit(-1)


arena.init(HOST, REALM, SCENE)

print("starting sign main loop")

signParent = arena.Object(
    persist=True,
    objName="signParent",
    objType=arena.Shape.cube,
    location=(0, 0, 0),
    transparency=arena.Transparency(True, 0),
)


sign1 = arena.Object(
                objName="sign1-model",
                url="store/users/wiselab/models/blank-sign/scene.gltf",
                objType=arena.Shape.gltf_model,
                scale=(0.02,0.02,0.02),
                location=(0,0,0),
                clickable=False,
		        persist=True,
                parent="signParent"
)

target1 = arena.Object(
                objName="target1",
                objType=arena.Shape.cube,
                scale=(0.6,0.15,0.01),
                location=( -0.292,1.522, 0.027),
                rotation=( 0.017,-0.182, 0.003, 0.983 ),
                color=(170,200,255),
                clickable=True,
                callback=target1_handler,
                data='{"goto-url": { "on": "mousedown", "url": "https://arena.andrew.cmu.edu/?scene=room6" } } ',
                transparency=arena.Transparency(True, 0),
		        persist=True,
                parent="signParent"
)

text1 = arena.Object(
                objName="text1",
                objType=arena.Shape.text,
                scale=(0.5,0.5,0.5),
                location=( -0.292,1.522, 0.037),
                rotation=( 0.017,-0.182, 0.003, 0.983 ),
                clickable=False,
                data='{"text":"Room6"}',
                color=(255,0,0),
		        persist=True,
                parent="signParent"
)

target2 = arena.Object(
                objName="target2",
                objType=arena.Shape.cube,
                scale=(0.6,0.15,0.01),
                location=( -.12,1.22,-.013),
                rotation=( 0.017,0, 0, 1 ),
                color=(170,200,255),
                clickable=True,
                callback=target2_handler,
                data='{"goto-url": { "on": "mousedown", "url": "https://arena.andrew.cmu.edu/?scene=wine-store" } } ',
                transparency=arena.Transparency(True, 0),
		        persist=True,
                parent="signParent"
)

text2 = arena.Object(
                objName="text2",
                objType=arena.Shape.text,
                scale=(0.5,0.5,0.5),
                location=( -.12,1.22,-.003),
                rotation=( 0.017,0, 0, 1 ),
                clickable=False,
                data='{"text":"Wine Store"}',
                color=(255,0,0),
		        persist=True,
                parent="signParent"
)


target3 = arena.Object(
                objName="target3",
                objType=arena.Shape.cube,
                scale=(0.6,0.15,0.01),
                location=( -.3,0.91,0.023),
                rotation=( 0.017,0.225, 0, 1 ),
                color=(170,200,255),
                clickable=True,
                callback=target3_handler,
                data='{"goto-url": { "on": "mousedown", "url": "https://arena.andrew.cmu.edu/?scene=school" } } ',
                transparency=arena.Transparency(True, 0),
		        persist=True,
                parent="signParent"
)


text3 = arena.Object(
                objName="text3",
                objType=arena.Shape.text,
                scale=(0.5,0.5,0.5),
                location=( -.3,0.91,0.033),
                rotation=( 0.017,0.225, 0, 1 ),
                clickable=False,
                data='{"text":"School"}',
                color=(255,0,0),
		        persist=True,
                parent="signParent"
)



signParent.update(location=(3,0,-10))



arena.handle_events()
