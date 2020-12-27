# move-camera.py
#
# Move cameras to a random location

from arena import *
import random

cams = []

def rando():
    return float(random.randint(-100000, 100000)) / 1000


def new_obj_callback(msg):
    global cams
    if "camera" in msg["object_id"]:
        cams += [Camera(**msg)]


arena = Arena("arena.andrew.cmu.edu", "realm", "systest-movecamera")
arena.new_obj_callback = new_obj_callback

# cube = Cube(object_id="cube")
# arena.add_object(cube)

@arena.run_forever(interval_ms=500, cams=cams)
def move_cams(cams):
    for c in cams:
        arena.manipulate_camera(
            c, "camera-override",
            position=(rando(),1.6,rando()),
            rotation=(0,0,0,1)
        )
        arena.manipulate_camera(
            c, "look-at",
            target=(0,0,0)
        )


arena.start_tasks()
