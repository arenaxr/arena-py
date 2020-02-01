# shapes.py
#
# MQTT message format: x,y,z,rotX,rotY,rotZ,rotW,scaleX,scaleY,scaleZ,#colorhex,on/off

import socket,threading,SocketServer,time,random,os,sys,json
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
from scipy.spatial.transform import Rotation as R

HOST="oz.andrew.cmu.edu"
TOPIC="realm/s/guac/"

# Globals (yes, Sharon)

grid = [-1,-1,-1],[-1,-1,-1],[-1,-1,-1]
Xcoords = [1, 2, 3]
Ycoords = [1, 2, 3]
redblue = ["#FF0000","#0000FF"]

def solved():
    global grid

    if grid[0][0] == 1 and grid[0][1] == 1 and grid [0][2] == 1 : return True
    if grid[1][0] == 1 and grid[1][1] == 1 and grid [1][2] == 1 : return True
    if grid[2][0] == 1 and grid[2][1] == 1 and grid [2][2] == 1 : return True
    if grid[0][0] == 0 and grid[0][1] == 0 and grid [0][2] == 0 : return True
    if grid[1][0] == 0 and grid[1][1] == 0 and grid [1][2] == 0 : return True
    if grid[2][0] == 0 and grid[2][1] == 0 and grid [2][2] == 0 : return True

    if grid[0][0] == 1 and grid[1][0] == 1 and grid [2][0] == 1 : return True
    if grid[0][1] == 1 and grid[1][1] == 1 and grid [2][1] == 1 : return True
    if grid[0][2] == 1 and grid[1][2] == 1 and grid [2][2] == 1 : return True
    if grid[0][0] == 0 and grid[1][0] == 0 and grid [2][0] == 0 : return True
    if grid[0][1] == 0 and grid[1][1] == 0 and grid [2][1] == 0 : return True
    if grid[0][2] == 0 and grid[1][2] == 0 and grid [2][2] == 0 : return True

    if grid[0][0] == 0 and grid[1][1] == 0 and grid [2][2] == 0 : return True
    if grid[0][0] == 1 and grid[1][1] == 1 and grid [2][2] == 1 : return True
    if grid[0][2] == 0 and grid[1][1] == 0 and grid [2][0] == 0 : return True
    if grid[0][2] == 1 and grid[1][1] == 1 and grid [2][0] == 1 : return True
    
    return False

def stalemate():
    global grid
    for x in Xcoords:
        for y in Ycoords:
            if grid[x-1][y-1] == -1: return False
    return True

def drawCube(x,y,color):
    name="cube_"+str(x)+'_'+str(y)
    MESSAGE='{"persist": true, "object_id":"'+name+'","action":"update","type":"object","data":{"object_type": "cube","position": {"x": '+"{0:0.3f}".format(x) +', "y": '+"{0:0.3f}".format(y) +', "z": -3 },"material": {"transparent": false, "opacity": 1.0},"scale": {"x":0.6,"y":0.6,"z":0.6},"click-listener":""}}'
    publish.single(TOPIC, MESSAGE, hostname=HOST, retain=False)

def initCube(x,y,color):
    name="cube_"+str(x)+'_'+str(y)
    MESSAGE='{"persist": true, "object_id":"'+name+'","action":"create","type":"object","data":{"dynamic-body": {"type": "static"}, "impulse": {"on": "mouseup", "force": "'+str(0)+' '+str(40)+' '+str(0)+'", "position": "10 1 1"},"click-listener":"", "object_type": "cube","position": {"x": '+"{0:0.3f}".format(x) +', "y": '+"{0:0.3f}".format(y) +', "z": -3 },"material":{"transparent": true, "opacity": 0.5},"color":"'+color+'","scale": {"x":0.6,"y":0.6,"z":0.6},"click-listener":""}}'
    publish.single(TOPIC, MESSAGE, hostname=HOST, retain=False)
    
def dropCube(x,y):
    name="cube_"+str(x)+'_'+str(y)
    MESSAGE='{"persist": true, "object_id":"'+name+'","action":"update","type":"object","data":{"dynamic-body": {"type":"dynamic"}}}'
    publish.single(TOPIC, MESSAGE, hostname=HOST, retain=False)

def deleteCube(x,y):
    name="cube_"+str(x)+'_'+str(y)
    MESSAGE='{"persist": true, "object_id":"'+name+'","action":"delete"}'
    publish.single(TOPIC, MESSAGE, hostname=HOST, retain=False)
    
def launchCube(x,y):
    name="cube_"+str(x)+'_'+str(y)
    MESSAGE='{"persist": true, "object_id":"'+name+'","action":"update","type":"object","data":{"dynamic-body": {"type":"dynamic"}}}'    
    publish.single(TOPIC, MESSAGE, hostname=HOST, retain=False)
    #time.sleep(0.15)
    MESSAGE='{"persist": true,"object_id":"'+name+'","action": "clientEvent", "type": "mouseup", "data": {"position":{"x":0,"y":0,"z":0},"source":"guacprogram"}}'
    publish.single(TOPIC, MESSAGE, hostname=HOST, retain=False)
    
def drawAvocado():
    MESSAGE='{"persist": true, "object_id" : "gltf-model_avocadoman", "action": "create", "data": {"object_type": "gltf-model", "url": "models/avocadoman/scene.gltf", "position": {"x": -1, "y": 0.01, "z": -4}, "rotation": {"x": 0, "y": 0, "z": 0, "w": 1}, "scale": {"x": 0.005, "y": 0.005, "z": 0.005}}}'
    publish.single(TOPIC, MESSAGE, hostname=HOST, retain=False)

def animateAvocado():
    MESSAGE='{"persist": true, "object_id": "gltf-model_avocadoman", "action": "update", "type": "object", "data": {"animation-mixer": {"clip": "Recuperate", "loop": "pingpong", "repetitions": 2, "timeScale": 4}}}'
    publish.single(TOPIC, MESSAGE, hostname=HOST, retain=False)
def animateAvocado2():
    MESSAGE='{"persist": true, "object_id": "gltf-model_avocadoman", "action": "update", "type": "object", "data": {"animation-mixer": {"clip": "Walking", "loop": "pingpong", "repetitions": 2}}}'
    publish.single(TOPIC, MESSAGE, hostname=HOST, retain=False)
    
counter = 0

def draw_board():
    global counter
    global grid
    counter = 0
    grid = [-1,-1,-1],[-1,-1,-1],[-1,-1,-1]
    drawAvocado()
    for x in Xcoords:
        for y in Ycoords:
            initCube(x,y,"#808080")

def animate_win():
    animateAvocado()
    for x in Xcoords:
        for y in Ycoords:
            launchCube(x,y)
    time.sleep( 5)
    for x in Xcoords:
        for y in Ycoords:
            deleteCube(x,y)

def animate_loss():
    for x in Xcoords:
        for y in Ycoords:
            dropCube(x,y)
    animateAvocado2()
    time.sleep( 5)
    for x in Xcoords:
        for y in Ycoords:
            deleteCube(x,y)

#define callbacks
def on_click_input(client, userdata, msg):
    global counter
    global rando
    jsonMsg=json.loads(msg.payload)

    # filter non-event messages
    if jsonMsg["action"] !="clientEvent": return

    # filter non-mouse messages
    if jsonMsg["type"]=="mousedown":
        name = jsonMsg["object_id"]
        color=redblue[counter % 2]
        x=int(name.split('_')[1])
        y=int(name.split('_')[2])
        if grid[(x-1)][(y-1)] != -1: return
        counter=counter+1
        grid[(x-1)][(y-1)]=counter%2
        MESSAGE='{"object_id":"'+name+'","action":"update","type":"object","data":{"material": {"color":"'+color+'", "transparent": false, "opacity": 1.0}}}'
        publish.single(TOPIC, MESSAGE, hostname=HOST, retain=False)

        if solved():
            animate_win()
            draw_board()
        if stalemate():
            animate_loss()
            draw_board()
    else:
        return;

rando=random.randint(0,10000)
print rando

client= mqtt.Client(str(random.random()), clean_session=True, userdata=None )
client.connect(HOST)

print("subscribing")
client.subscribe(TOPIC+'#')

print("adding callback")
client.message_callback_add(TOPIC+'#', on_click_input)

print("starting main loop")
draw_board()
client.loop_start() # doesn't really do anything but wait for events

while True:
    time.sleep(1)

client.disconnect()
client.loop.stop()
