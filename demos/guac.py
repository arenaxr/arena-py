# guac.py
#
# plays Tic Tac Toe

import json
import random
import time
import arena
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

HOST = "oz.andrew.cmu.edu"
TOPIC = "realm/s/guac/"
REALM = "realm"
SCENE = "guac"

# Globals (yes, Sharon)

cubes = {} # dict of cube objects to be indexed by tuple (x,y)
grid = [-1, -1, -1], [-1, -1, -1], [-1, -1, -1]
Xcoords = [1, 2, 3]
Ycoords = [1, 2, 3]
redblue = [(255,0,0),(0,0,255)]
messages = []

def solved():
    global grid

    if grid[0][0] == 1 and grid[0][1] == 1 and grid[0][2] == 1:
        return True
    if grid[1][0] == 1 and grid[1][1] == 1 and grid[1][2] == 1:
        return True
    if grid[2][0] == 1 and grid[2][1] == 1 and grid[2][2] == 1:
        return True
    if grid[0][0] == 0 and grid[0][1] == 0 and grid[0][2] == 0:
        return True
    if grid[1][0] == 0 and grid[1][1] == 0 and grid[1][2] == 0:
        return True
    if grid[2][0] == 0 and grid[2][1] == 0 and grid[2][2] == 0:
        return True

    if grid[0][0] == 1 and grid[1][0] == 1 and grid[2][0] == 1:
        return True
    if grid[0][1] == 1 and grid[1][1] == 1 and grid[2][1] == 1:
        return True
    if grid[0][2] == 1 and grid[1][2] == 1 and grid[2][2] == 1:
        return True
    if grid[0][0] == 0 and grid[1][0] == 0 and grid[2][0] == 0:
        return True
    if grid[0][1] == 0 and grid[1][1] == 0 and grid[2][1] == 0:
        return True
    if grid[0][2] == 0 and grid[1][2] == 0 and grid[2][2] == 0:
        return True

    if grid[0][0] == 0 and grid[1][1] == 0 and grid[2][2] == 0:
        return True
    if grid[0][0] == 1 and grid[1][1] == 1 and grid[2][2] == 1:
        return True
    if grid[0][2] == 0 and grid[1][1] == 0 and grid[2][0] == 0:
        return True
    if grid[0][2] == 1 and grid[1][1] == 1 and grid[2][0] == 1:
        return True

    return False


def stalemate():
    global grid
    for x in Xcoords:
        for y in Ycoords:
            if grid[x - 1][y - 1] == -1:
                return False
    return True


def initCube(x, y, color):
    name = "cube_" + str(x) + "_" + str(y)
    # what happens if we don't delete first?
    #    MESSAGE = {
    #        "object_id": name,
    #        "action": "delete"
    #        }
    #    client.publish(TOPIC, json.dumps(MESSAGE))
    cubes[(x,y)]=arena.Object(objType=arena.Shape.cube,
                              persist=True,
                              objName=name,
                              physics=arena.Physics.static,
                              data='{"material": {"transparent":true,"opacity": 0.5},"impulse":{"on":"mouseup","force":"0 40 0","position": "10 1 1"}}',
                              location=(x,y,-3),
                              color=color,
                              scale=(0.6,0.6,0.6),
                              clickable=True);

def dropCube(x, y):
    name = "cube_" + str(x) + "_" + str(y)
    cubes[(x,y)].update(physics=arena.Physics.dynamic)


def deleteCube(x, y):
    name = "cube_" + str(x) + "_" + str(y)
    cubes[(x,y)].delete()

def launchCube(x, y):
    name = "cube_" + str(x) + "_" + str(y)
    cubes[(x,y)].update(physics=arena.Physics.dynamic)
    cubes[(x,y)].fireEvent(arena.Event.mouseup,(0,0,0),"guacprogram")

def deleteAvocado():
    global avocado
    avocado.delete()

def drawAvocado():
    global avocado
    avocado = arena.Object(persist=True,
                           objName="gltf-model_avocadoman",
                           objType=arena.Shape.gltf_model,
                           url="models/avocadoman/scene.gltf",
                           location=(-1,0.01,-4),
                           scale=(0.005,0.005,0.005),
    )

def animateAvocado():
    global avocado
    #    MESSAGE='{"object_id": "gltf-model_avocadoman", "action": "delete"}'
    #    client.publish((TOPIC, MESSAGE)
    deleteAvocado()
    drawAvocado()
    avocado.update(data='{"animation-mixer": {"clip": "Recuperate","loop": "pingpong","repetitions": 2,"timeScale": 4}}')

def animateAvocado2():
    global avocado
    deleteAvocado()
    drawAvocado()
    avocado.update(data='{"animation-mixer": {"clip": "Walking", "loop": "pingpong", "repetitions": 2}}')

counter = 0

def draw_board():
    global counter
    global grid
    counter = 0
    grid = [-1, -1, -1], [-1, -1, -1], [-1, -1, -1]
    drawAvocado()
    for x in Xcoords:
        for y in Ycoords:
            initCube(x, y, (127,127,127))

def animate_win():
    animateAvocado()
    for x in Xcoords:
        for y in Ycoords:
            launchCube(x, y)
    time.sleep(5);
    for x in Xcoords:
        for y in Ycoords:
            deleteCube(x, y)

def animate_loss():
    for x in Xcoords:
        for y in Ycoords:
            dropCube(x, y)
    animateAvocado2()
    time.sleep(5);
    for x in Xcoords:
        for y in Ycoords:
            deleteCube(x, y)

def process_message(msg):
    global counter
    global rando

    jsonMsg = json.loads(msg)

    # filter non-event messages
    if jsonMsg["action"] != "clientEvent":
        return

    # filter non-mouse messages
    if jsonMsg["type"] == "mousedown":
        #print("on_click_input:" + msg)
        name = jsonMsg["object_id"]
        color = redblue[counter % 2]
        x = int(name.split("_")[1])
        y = int(name.split("_")[2])
        if grid[(x - 1)][(y - 1)] != -1:
            return
        counter = counter + 1
        grid[(x - 1)][(y - 1)] = counter % 2
        colstring = '#%02x%02x%02x' % color
        cubes[(x,y)].update(physics=arena.Physics.static,
                            data='{"impulse": {"on": "mouseup","force":"0 40 0","position":"10 1 1"},"material": {"color":"'+ colstring+'", "transparent": false, "opacity": 1}}',
                            clickable=True,
                            location=(x,y,-3),
                            scale=(0.6, 0.6, 0.6)
        )
        #        MESSAGE='{"persist": true, "object_id":"'+name+'","action":"update","type":"object","data":{"material": {"color":"'+color+'", "transparent": false, "opacity": 1.0}}}'

        if solved():
            print("solved")
            animate_win()
            draw_board()
        if stalemate():
            print("stalemate")
            animate_loss()
            draw_board()
    else:
        return

# start the fun shall we?

arena.init(HOST, REALM, SCENE, process_message)
print("starting main loop")
draw_board()
arena.handle_events()
