# get_persisted_obj.py
#
# Tests scene get_persisted_obj

from arena import *

scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="test")

@scene.run_once
def main():
    object_id = "the_box"
    box = scene.get_persisted_obj(object_id)
    box.data.position = Position(0,2,0)
    scene.update_object(box)
    print(box)

scene.run_tasks()
