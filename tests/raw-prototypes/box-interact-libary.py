import arena
import json
import random
import signal
import sys
import time

HOST = "oz.andrew.cmu.edu"
REALM = "realm"
SCENE="render"
object_name = "cube_x"

# Object starting point, global so click handler can modify it
x = 1.0
y = 1.0
z = 1.0


# add signal handler to remove objects on quit
def signal_handler(sig, frame):
    exit()
signal.signal(signal.SIGINT, signal_handler)

# this object will be our box
theBox = None

# define callbacks
def on_click_input(msg):
    global theBox
    global x
    global y
    global z

    #print('got ' + msg)

    jsonMsg = json.loads(msg)
    # filter non-event messages
    if jsonMsg["action"] != "clientEvent":
        return
    # filter non-mouse messages
    if jsonMsg["type"] != "mousedown":
        return
    print('got click')

    click_x = jsonMsg["data"]["position"]["x"]
    click_y = jsonMsg["data"]["position"]["y"]
    click_z = jsonMsg["data"]["position"]["z"]
    user = jsonMsg["data"]["source"]
    # click_x,click_y,click_z,user = msg.payload.split(',')
    print("Clicked by: " + user)
    obj_x = float(x) - float(click_x)
    obj_y = float(y) - float(click_y)
    obj_z = float(z) - float(click_z)

    print("Obj relative click: " + str(obj_x) + "," + str(obj_y) + "," + str(obj_z))
    x = click_x
    y = click_y
    z = click_z
    # cube_str = "property: position; to: {} {} {}; dur: 100; easing: linear"
    # Publish an animation command to move the object

    theData='{"animation": {"property": "position","to":"'+str(x)+' '+str(y)+' '+str(z)+'","easing": "linear","dur": 100}}'
    theBox.update(data=theData)
    
    print("Update Box Location")

theColor = (random.randint(0, 255),random.randint(0, 255),random.randint(0, 255))
# cube_str = object_name + ",{},{},{},0,0,0,0,1,1,1,{},on"
# Publish a cube with x,y,z and color parameters
# retain=False makes it not persist forever in the scene


arena.init(HOST, REALM, SCENE, on_click_input)
theBox = arena.Object(objName=object_name,objType=arena.Shape.cube, location=(x, y, z), clickable=True,color=theColor)

# Main loop that runs every 5 seconds and changes the object color
while True:
    print("Main loop changing color")
    arena.flush_events()
    color = (random.randint(0, 255),random.randint(0, 255),random.randint(0, 255))

    # Draw cube at x,y,z location with a new color
    theBox = arena.Object(objName=object_name,objType=arena.Shape.cube,location=(x,y,z),color=color)
    for i in range(0, 50):
        arena.flush_events()
        time.sleep(0.1)
