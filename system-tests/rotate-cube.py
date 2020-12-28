# rotate-cube.py
#
# Rotates a color changing cube. Tests making and updating Euler Rotation and Color Attributes.

from arena import *
import random


# start ARENA client
arena = Arena("arena.andrew.cmu.edu", "realm", "test")

cube = Cube(object_id="cube", position=(0,4,-2), scale=Scale(2,2,2), rotation=(0,0,0), color=(0,0,0))
arena.add_object(cube)

@arena.run_forever(interval_ms=250)
def rotate_cube():
    sign = random.randint(1,2)
    if sign == 1: sign = 1
    else: sign = -1

    direction = random.randint(1,3)
    if direction == 1:
        cube.data.rotation.x += sign*0.1
    elif direction == 2:
        cube.data.rotation.y += sign*0.1
    elif direction == 3:
        cube.data.rotation.z += sign*0.1

    color = random.randint(1,3)
    if color == 1:
        cube.data.color.red = (cube.data.color.red + sign*5) % 255
    elif color == 2:
        cube.data.color.blue = (cube.data.color.blue + sign*5) % 255
    elif color == 3:
        cube.data.color.green = (cube.data.color.green + sign*5) % 255

    arena.update_object(cube)

arena.run_forever(rotate_cube)

arena.run_tasks()
