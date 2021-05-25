# landmarks.py
#
# test creating landmarks

from arena import *

scene = Scene(host="arenaxr.org", scene="test")

object_id = "the_box"

@scene.run_once
def make_box():
    scene.add_landmark(
        Box(object_id=object_id, position=(0,2,-2)), label="The Box")

scene.run_tasks()
