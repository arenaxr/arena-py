from arena import *

scene = Scene(host="mqtt.arenaxr.org", scene="example")

@scene.run_once
def make_box():
    scene.add_object(Box())

scene.run_tasks()
