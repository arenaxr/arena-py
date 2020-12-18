from arena import *
import time

def msg_callback(arg):
    print("callback1")

arena = Arena("arena.andrew.cmu.edu", "head", "realm", callback=msg_callback)

def f(arg):
    print("callback")
cube = Cube(object_id="cube1", scale=Scale(2,2,2), position=Position(0,1,1), callback=f)
torusKnot = TorusKnot(object_id="torus1", scale=Scale(1,2,1), position=Position(2,3,1), color="#ff0ff6")
line = Line(object_id="line1", scale=Scale(1,2,3), start=Position(0,0,0), end=Position(5,1,-4), position=Position(2,3,1), color="#ff0f0f")

cam = Camera(object_id="camera_6146_EdwardLu", scale=Scale(1,2,3))

arena.add_object(cube)
arena.add_object(line)
time.sleep(1)
arena.add_object(torusKnot)
time.sleep(1)
arena.delete_object(cube)
arena.delete_object(torusKnot)

while 1:
    # print(arena.all_objects)
    print(cam.data.position, cam.data.rotation)
    time.sleep(1)
