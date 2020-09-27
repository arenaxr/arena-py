# robot-arm.py
#

import time
import arena
import random
import os
import json
import base64

# export HOST=arena.andrew.cmu.edu
# export REALM=realm
# export MQTTH=arena.andrew.cmu.edu
# export MID=MID_1234

# export LINKS = "Link1,https://www.duckduckgo.com,Link 2,https:www.f1.com,Link 3,https://www.eet.com"
# Needs to be base64 encoded for arts:
# export LINKS = "TGluazEsaHR0cHM6Ly93d3cuZHVja2R1Y2tnby5jb20sTGluayAyLGh0dHBzOnd3dy5mMS5jb20sTGluayAzLGh0dHBzOi8vd3d3LmVldC5jb20="

# LINKS env will overwrite this default:
sign_links =  ['Link 1','https://www.duckduckgo.com','Link 2','https://www.f1.com','Link 3','https://www.eet.com']


# export LOCATION = "MywwLC0xMA=="
sign_location = [3,0,-10]

def draw_ray(click_pos, position):
    line = arena.Object(
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
        target1.update(color=(0,255,0), transparency=arena.Transparency(True, 0.5)  )
    if event.event_type == arena.EventType.mouseleave:
        target1.update(transparency=arena.Transparency(True, 0.0) )
    if event.event_type == arena.EventType.mousedown:
        draw_ray(event.click_pos, event.position)
        target1.update(transparency=arena.Transparency(True, 0.0) )


def target2_handler(event=None):
    global target2 
    if event.event_type == arena.EventType.mouseenter:
        target2.update(color=(0,255,0),transparency=arena.Transparency(True, 0.5)  )
    if event.event_type == arena.EventType.mouseleave:
        target2.update( transparency=arena.Transparency(True, 0.0) )
    if event.event_type == arena.EventType.mousedown:
        draw_ray(event.click_pos, event.position)
        target2.update( transparency=arena.Transparency(True, 0.0) )


def target3_handler(event=None):
    global target3 
    if event.event_type == arena.EventType.mouseenter:
        target3.update(color=(0,255,0),transparency=arena.Transparency(True, 0.5)  )
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

if os.environ.get('MID') is not None:
    MID = os.environ["MID"]+'-'
    #SCENE = SCENE + "/" + MID  

print( "MID:" + MID)

if os.environ.get('LINKS') is not None:
    # Links is base64 encoded
    LINKS = os.environ["LINKS"]
    LINKS = str(base64.b64decode(LINKS))
    # Drop the b' at the start of the string and ' at the end
    LINKS = LINKS[2:-1]
    # take the string and parse out CSV parameters
    sign_links= LINKS.split(",")

if os.environ.get('LOCATION') is not None:
    # Links is base64 encoded
    LOC = os.environ["LOCATION"]
    LOC = str(base64.b64decode(LOC))
    # Drop the b' at the start of the string and ' at the end
    LOC = LOC[2:-1]
    # take the string and parse out CSV parameters
    sign_location = LOC.split(",")

print( "Scene:" + SCENE)

arena.init(HOST, REALM, SCENE)

print("starting sign main loop")

signParent = arena.Object(
    persist=True,
    objName=MID+"signParent",
    objType=arena.Shape.cube,
    location=(0, 0, 0),
    transparency=arena.Transparency(True, 0),
)

sign1 = arena.Object(
                objName=MID+"sign1-model",
                url="store/users/wiselab/models/blank-sign/scene.gltf",
                objType=arena.Shape.gltf_model,
                scale=(0.02,0.02,0.02),
                location=(0,0,0),
                clickable=False,
		        persist=True,
                parent=MID+"signParent"
)


dataStr='{"goto-url": { "on": "mousedown", "url": "' + sign_links[1] + '"} } '

target1 = arena.Object(
                objName=MID+"target1",
                objType=arena.Shape.cube,
                scale=(0.6,0.15,0.01),
                location=( -0.292,1.522, 0.027),
                rotation=( 0.017,-0.182, 0.003, 0.983 ),
                color=(170,200,255),
                clickable=True,
                callback=target1_handler,
                data=dataStr,
                transparency=arena.Transparency(True, 0),
		        persist=True,
                parent=MID+"signParent"
)

dataStr='{"text":"' + sign_links[0] + '"}'
text1 = arena.Object(
                objName=MID+"text1",
                objType=arena.Shape.text,
                scale=(0.5,0.5,0.5),
                location=( -0.292,1.522, 0.037),
                rotation=( 0.017,-0.182, 0.003, 0.983 ),
                clickable=False,
                data=dataStr,
                color=(100,100,255),
		        persist=True,
                parent=MID+"signParent"
)

dataStr='{"goto-url": { "on": "mousedown", "url": "' + sign_links[3] + '"} } '
target2 = arena.Object(
                objName=MID+"target2",
                objType=arena.Shape.cube,
                scale=(0.6,0.15,0.01),
                location=( -.12,1.22,-.013),
                rotation=( 0.017,0, 0, 1 ),
                color=(170,200,255),
                clickable=True,
                callback=target2_handler,
                data=dataStr,
                transparency=arena.Transparency(True, 0),
		        persist=True,
                parent=MID+"signParent"
)

dataStr='{"text":"' + sign_links[2] + '"}'
text2 = arena.Object(
                objName=MID+"text2",
                objType=arena.Shape.text,
                scale=(0.5,0.5,0.5),
                location=( -.12,1.22,-.003),
                rotation=( 0.017,0, 0, 1 ),
                clickable=False,
                data=dataStr,
                color=(100,100,255),
		        persist=True,
                parent=MID+"signParent"
)


dataStr='{"goto-url": { "on": "mousedown", "url": "' + sign_links[5] + '"} } '
target3 = arena.Object(
                objName=MID+"target3",
                objType=arena.Shape.cube,
                scale=(0.6,0.15,0.01),
                location=( -.3,0.91,0.023),
                rotation=( 0.017,0.225, 0, 1 ),
                color=(170,200,255),
                clickable=True,
                callback=target3_handler,
                data=dataStr,
                transparency=arena.Transparency(True, 0),
		        persist=True,
                parent=MID+"signParent"
)


dataStr='{"text":"' + sign_links[4] + '"}'
text3 = arena.Object(
                objName=MID+"text3",
                objType=arena.Shape.text,
                scale=(0.5,0.5,0.5),
                location=( -.3,0.91,0.033),
                rotation=( 0.017,0.225, 0, 1 ),
                data=dataStr,
                color=(100,100,255),
		        persist=True,
                parent=MID+"signParent"
)



signParent.update(location=(float(sign_location[0]),float(sign_location[1]),float(sign_location[2])))



arena.handle_events()
