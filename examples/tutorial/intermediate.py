from arena import *

# setup library
scene = Scene(host="arenaxr.org", scene="example")

# make a box
box = Box(object_id="my_box", position=Position(0,4,-2), scale=Scale(2,2,2))

@scene.run_once
def main():
    # add the box
    scene.add_object(box)

    # box.update_attributes(position=Position(2,4,-2))
    # scene.update_object(box)

    # add text
    text = Text(object_id="my_text", value="Welcome to arena-py!", position=Position(0,2,0), parent=box)
    scene.add_object(text)

x = 0
@scene.run_forever(interval_ms=500)
def periodic():
    global x    # non allocated variables need to be global
    box.update_attributes(position=Position(x,3,0))
    scene.update_object(box)
    x += 0.1

# start tasks
scene.run_tasks()
