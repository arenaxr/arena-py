from arena import *

# setup library
scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")

def main():
    # make a box
    box = Box(object_id="my_box", position=Position(0,4,-2), scale=Scale(2,2,2))
    print(box.json())
    # add the box
    scene.add_object(box)

# add and start tasks
scene.run_once(main)
scene.run_tasks()

