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


arena = Arena("arena.andrew.cmu.edu", "realm", "public", "test")
arena.new_obj_callback = new_obj_callback

# box = Box(object_id="box")
# arena.add_object(box)

@arena.run_forever(interval_ms=500, cams=cams)
def move_cams(cams):
    for c in cams:
        arena.manipulate_camera(
            c,
            position=(rando(),1.6,rando()),
            rotation=(0,0,0,1)
        )
        arena.look_at(
            c,
            target=(0,0,0)
        )


arena.run_tasks()
