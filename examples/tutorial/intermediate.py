from arena import *

# setup library
arena = Arena("arena.andrew.cmu.edu", "realm", "public", "example")

# make a cube
cube = Cube(object_id="my_cube", position=Position(0,4,-2), scale=Scale(2,2,2))

@arena.run_once
def main():
    # add the cube
    arena.add_object(cube)

    # cube.update_attributes(position=Position(2,4,-2))
    # arena.update_object(cube)

    # add text
    text = Text(object_id="my_text", text="Welcome to arena-py!", position=Position(0,2,0), parent=cube)
    arena.add_object(text)

x = 0
@arena.run_forever(interval_ms=500)
def periodic():
    global x    # non allocated variables need to be global
    cube.update_attributes(position=Position(x,3,0))
    arena.update_object(cube)
    x += 0.1

# start tasks
arena.run_tasks()
