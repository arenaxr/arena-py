# guac.py
#
# plays Tic Tac Toe
# clicked boxes alternate red and blue
# boxes fall if no winner
# boxes launch upon win
# avocado "Vanna White" reacts accordingly

import json
import time
import arena
import re

HOST = "oz.andrew.cmu.edu"
TOPIC = "realm/s/guac/"
REALM = "realm"
SCENE = "guac"

# Globals (yes, Sharon)

cubes = {} # dict of cube objects to be indexed by tuple (x,y)
# grid elements can be:
# -1: unassigned
#  0: red
#  1: blue
grid = [-1, -1, -1], [-1, -1, -1], [-1, -1, -1]
Xcoords = [1, 2, 3]
Ycoords = [1, 2, 3]
redblue = [(255,0,0),(0,0,255)]
messages = []

def solved():
    global grid

    # rows
    for row in [0, 1, 2]:
        for color in [0, 1]:
            if grid[row][0] == color and grid[row][1] == color and grid[row][2] == color: return True

    # columns
    for col in [0, 1, 2]:
        for color in [0, 1]:
            if grid[0][col] == color and grid[1][col] == color and grid[2][col] == color: return True

    # diagonals
    if grid[0][0] == 0 and grid[1][1] == 0 and grid[2][2] == 0: return True
    if grid[0][0] == 1 and grid[1][1] == 1 and grid[2][2] == 1: return True
    if grid[0][2] == 0 and grid[1][1] == 0 and grid[2][0] == 0: return True
    if grid[0][2] == 1 and grid[1][1] == 1 and grid[2][0] == 1: return True

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
    cubes[(x,y)]=arena.Object(objType=arena.Shape.cube,
                              persist=True,
                              objName=name,
                              physics=arena.Physics.static,
                              data='{"collision-listner":"", "material": {"transparent":true,"opacity": 0.5},"impulse":{"on":"mouseup","force":"0 40 0","position": "10 1 1"}}',
                              location=(x,y,-3),
                              color=color,
                              scale=(0.6,0.6,0.6),
                              clickable=True);

def dropCube(x, y):
    cubes[(x,y)].update(physics=arena.Physics.dynamic)


def deleteCube(x, y):
    cubes[(x,y)].delete()

def launchCube(x, y):
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
                           scale=(0.005,0.005,0.005))

def animateAvocado():
    global avocado
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

    jsonMsg = json.loads(msg)

    # filter non-event messages
    if jsonMsg["action"] != "clientEvent":
        return

    # only mousedown messages
    if jsonMsg["type"] == "mousedown":
        #print("on_click_input:" + msg)
        name = jsonMsg["object_id"]        
        if not re.match("cube_\d_\d", name): # test that object name matches pattern e.g. "cube_1_2"
            return

        # get click coordinates
        click_x = str(jsonMsg["data"]["clickPos"]["x"])
        click_y = str(jsonMsg["data"]["clickPos"]["y"]-0.5)
        click_z = str(jsonMsg["data"]["clickPos"]["z"])
        box_x = str(jsonMsg["data"]["position"]["x"])
        box_y = str(jsonMsg["data"]["position"]["y"])
        box_z = str(jsonMsg["data"]["position"]["z"])
        
        # draw a ray from clicker to cube
        line = arena.Object(
            objName="line1",
            objType=arena.Shape.line,
            ttl=1,
            data='{"start": {"x":'+
            click_x+', "y":'+
            click_y+', "z":'+
            click_z+'},"end": {"x":'+
            box_x+', "y":'+
            box_y+', "z":'+
            box_z+'}, "color": "#FFFFFF"}',
            )

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
                            scale=(0.6, 0.6, 0.6))

        #line.delete()

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
