from arena import *

# setup library
arena = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")

def main():
    # make a box
    box = Box(object_id="my_box", position=Position(0,4,-2), scale=Scale(2,2,2))
    print(box.json())
    # add the box
    arena.add_object(box)

# add and start tasks
arena.run_once(main)
arena.run_tasks()

