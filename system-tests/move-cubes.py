# move-cubes.py
#
# Make two cubes that move away from each other (and a bunch of dodecahedrons!).
# For testing tasks and object creation.

from arena import *
import random


# start ARENA client
arena = Arena("arena.andrew.cmu.edu", "render", "realm")


def evt_handler(msg):
    print("clicked")


cube = Cube(object_id="cube", position=Position(0,3,0), scale=Scale(2,2,2), click_listener=True, evt_handler=evt_handler)
arena.add_object(cube)

sphere = Sphere(object_id="sphere", position=Position(0,3,0), scale=Scale(1.5,1.5,1.5))
arena.add_object(sphere)


@arena.run_once(text="arena-py 2.0!", parent="sphere")
def make_text(text, parent):
    text_obj = Text(text=text, position=Position(0,1.5,0), parent=parent)
    arena.add_object(text_obj)
    print(sphere.object_id, text, parent)


i = 0
@arena.run_forever(interval_ms=500, arg="hi")
def move_cube(arg):
    global i # non allocated variables need to be global
    cube.update_attributes(position=Position(i,3,0))
    arena.update_object(cube)
    i += 0.2
    print(arg)


j = 0
def move_sphere():
    global j # non allocated variables need to be global
    sphere.update_attributes(position=Position(j,3,0))
    arena.update_object(sphere)
    j -= 0.5


def make_dodecahedrons():
    arena.add_object(Dodecahedron(position=Position(random.randint(-10,10),random.randint(0,5),random.randint(-10,10))))


arena.run_once(make_text, text="arena-py 2.0?", parent="cube")
arena.run_forever(move_sphere, 1000)
arena.run_forever(make_dodecahedrons, 2000)


arena.start_tasks() # will block
