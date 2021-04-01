import math
from arena import *

scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")

rotation_euler = (45,0,45) # Rotation(45,0,45) works too
rotation_quaternion = (0,0,1,1) # Rotation(0,0,1,1) works too

@scene.run_once
def make_box():
    my_box1 = Box(
        object_id="my_box1",
        position=(-2,2,-5),
        rotation=rotation_euler
    )

    my_box2 = Box(
        object_id="my_box2",
        position=(2,2,-5),
        rotation=rotation_quaternion
    )

    scene.add_object(my_box1)
    scene.add_object(my_box2)

scene.run_tasks()
