# laser.py
#
# This program loads a set of models that can be clicked on with
# a laser pointer ray

import time
import arena
import random
import os
import json
import sys 
import threading

# export MQTTH=arena.andrew.cmu.edu
# export REALM=realm
# export SCENE=scene
# export MID=MID_1234
# export JSONCFG=screens.json

objects = []
delete_object_queue = []



def draw_ray(event=None):
    if event.event_type == arena.EventType.mousedown:
        line = arena.Object(
            objType=arena.Shape.thickline,
            thickline=arena.Thickline( # slightly below camera so you can see line vs head-on
                {
                    (event.click_pos[0],event.click_pos[1]-0.1,event.click_pos[2]-0.1),
                    (event.position[0],event.position[1],event.position[2])
                },5,"#FF0000")
        )
        ball = arena.Object(
                objType=arena.Shape.sphere,
                location=(event.position[0],event.position[1],event.position[2] ),
                scale = (0.05,0.05,0.05),
                color=(255,0,0)
        )
        delete_object_queue.append(line)
        delete_object_queue.append(ball)

# Manually delete clicks
def object_harvester_thread():
    global delete_object_queue
    while True:
        while delete_object_queue:
            obj=delete_object_queue.pop()
            if type(obj) is not str: 
                obj.delete()
        time.sleep(5)
# start the fun shall we?

if (os.environ.get('SCENE') is not None) and (os.environ.get('REALM') is not None) and (os.environ.get('MQTTH') is not None) and (os.environ.get('MID') is not None):
    SCENE = os.environ["SCENE"]
    MQTTH = os.environ["MQTTH"]
    REALM = os.environ["REALM"]
    MID = os.environ["MID"]
    print("Loading (prgm,scene,real,host,MID): " + sys.argv[0]  + "," + SCENE + "," + REALM + "," + MQTTH + "," + MID)
    MID = MID + '-'
else:
    print( "You need to set SCENE, MQTTH, MID and REALM as environmental variables to specify the program target")
    print( "JSONCFG is optional for setting multiple screens and loications.")
    print( "\nFor bash you can copy paste the following before running:")
    print( "export MID=dir")
    print( "export MQTTH=arena.andrew.cmu.edu")
    print( "export REALM=realm")
    print( "export SCENE=example")
    print( "export JSONCFG=objects.json")
    exit(-1)


arena.init(MQTTH, REALM, SCENE)

if os.environ.get('JSONCFG') is not None:
    # Links is base64 encoded
    JFILE = os.environ["JSONCFG"]
    print( "JSONCFG:" + JFILE)
    screensData=None
    with open(JFILE) as dataFile:
        screensData = json.load(dataFile)
        cnt=0
        for key in screensData:
            print("Loading Object:" + key)
            value = screensData[key]
            print(value)
            projector_start = arena.Object(                    
                    persist=True,
                    objName=key,
                    objType=arena.Shape.gltf_model,
                    clickable=True,
                    location=value["location"],
                    scale=value["scale"],
                    rotation=value["rotation"],
                    callback=draw_ray,
                    url=value["url"]
            ) 

    

y = threading.Thread(target=object_harvester_thread)
y.start()
print("starting sign main loop")


print( "Go to URL: https://" + MQTTH + "/" + SCENE)

print("Screens Ready")
arena.handle_events()
