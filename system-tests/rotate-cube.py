# rotate-box.py
#
# Rotates a color changing box. Tests making and updating Euler Rotation and Color Attributes.

from arena import *
import random


# start ARENA client
arena = Arena(host="arena.andrew.cmu.edu", realm="realm", scene="test")

box = Box(object_id="box", position=(0,4,-2), scale=Scale(2,2,2), rotation=(0,0,0), color=Color(0,0,0))
arena.add_object(box)

@arena.run_forever(interval_ms=250)
def rotate_box():
    sign = random.randint(1,2)
    if sign == 1: sign = 1
    else: sign = -1

    direction = random.randint(1,3)
    if direction == 1:
        box.data.rotation.x += sign*0.1
    elif direction == 2:
        box.data.rotation.y += sign*0.1
    elif direction == 3:
        box.data.rotation.z += sign*0.1

    color = random.randint(1,3)
    if color == 1:
        box.data.color.red = (box.data.color.red + sign*5) % 255
    elif color == 2:
        box.data.color.blue = (box.data.color.blue + sign*5) % 255
    elif color == 3:
        box.data.color.green = (box.data.color.green + sign*5) % 255

    arena.update_object(box)

arena.run_forever(rotate_box)

arena.run_tasks()
