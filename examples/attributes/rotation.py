import math
from arena import *

scene = Scene(host="arenaxr.org", scene="example")

rotation_euler = (0,0,0) # Rotation(0,0,0) works
rotation_quaternion = (0,0,1,1) # Rotation(0,0,1,1) works too

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

@scene.run_once
def make_box():
    scene.add_object(my_box1)
    scene.add_object(my_box2)

@scene.run_forever(interval_ms=100)
def rotate_box():
    my_box1.data.rotation.x += 3
    my_box1.data.rotation.y += 3
    my_box1.data.rotation.z += 3
    scene.update_object(my_box1)

scene.run_tasks()
