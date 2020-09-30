# balls.py
#
# spray a bunch of spheres into the scene, test physics

import arena
import random
import time
import signal

HOST = "arena.andrew.cmu.edu"
SCENE = "balls"

arena.init(HOST, "realm", SCENE)

def rando():
    return float(random.randint(0, 10000)) / 1000

def randcolor():
    x = random.randint(0,255)
    y = random.randint(0,255)
    z = random.randint(0,255)
    return(x,y,z)

def signal_handler(sig, frame):
    exit()
signal.signal(signal.SIGINT, signal_handler)

counter = 0
while True:
    obj_id = str(counter)
    name = "sphere" + "_" + obj_id
    counter += 1

    obj = arena.Object(
        physics=arena.Physics.dynamic,
        objName=obj_id,
        objType=arena.Shape.sphere,
        location=(rando(),0,rando()),
        color=randcolor(),
        ttl=40)
    
    time.sleep(0.1)
