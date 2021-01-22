# screen_mgr.py
#
# This program presents control knobs that draw a screenshare object
# at a particular location in the screen. It also dims the ambient 
# lighting level to 1 which provides ideal contrast.  Upon clicks
# a laser annotation appears. 

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

screens= []
delete_object_queue = []


def projector_start(event=None):
    global screens
    
    if event.event_type == arena.EventType.mouseup:
        local_screens = screens.copy()
        print("Start")
        for i in range(len(local_screens)):
            screen=local_screens.pop()
            print(screen)
            screen.update(transparency=arena.Transparency(True,1.0))


def projector_stop(event=None):
    global screens
    if event.event_type == arena.EventType.mouseup:
        local_screens = screens.copy()
        print("Start")
        for i in range(len(local_screens)):
            screen=local_screens.pop()
            print(screen)
            screen.update(transparency=arena.Transparency(True,0.0))



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
    print( "export JSONCFG=directory_cfg.json")
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
            print("Key:" + key)
            value = screensData[key]
            if key == "projector":
                print("Projector")
                projector_start = arena.Object(                    
                    persist=True,
                    objName="projector_start",
                    objType=arena.Shape.cube,
                    clickable=True,
                    color=(0,255,0),
                    location=value["location"],
                    scale=value["scale"],
                    rotation=value["rotation"],
                    callback=projector_start
                    ) 
                stop_location = value["location"]
                stop_location[1]=stop_location[1]- value["button_distance"]
                projector_stop = arena.Object(                    
                    persist=True,
                    objName="projector_stop",
                    objType=arena.Shape.cube,
                    clickable=True,
                    location=stop_location,
                    color=(255,0,0),
                    scale=value["scale"],
                    rotation=value["rotation"],
                    callback=projector_stop
                    ) 

            else:
                print("Screen: " + str(cnt))
                value = screensData[key]
                screens.append( arena.Object(
                    persist=True,
                    objName=key,
                    objType=arena.Shape.cube,
                    #transparency=arena.Transparency(True, 0),
                    clickable=True,
                    location=value["location"],
                    scale=value["scale"],
                    rotation=value["rotation"],
                    callback=draw_ray
                    ))
                cnt+=1
    

y = threading.Thread(target=object_harvester_thread)
y.start()
print("starting sign main loop")


print( "Go to URL: https://" + MQTTH + "/" + SCENE)

print("Screens Ready")
arena.handle_events()
