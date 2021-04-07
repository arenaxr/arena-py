# get_persisted_objs.py
#
# Tests scene get_persisted_objs

from arena import *

scene = Scene(host="arenaxr.org", realm="realm", scene="test")

@scene.run_once
def main():
    object_id = "the_box"
    for obj_id,obj in scene.get_persisted_objs().items():
        print(obj)
        print()

scene.run_tasks()
