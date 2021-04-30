from arena import *

scene = Scene(host="arenaxr.org", realm="realm", scene="example")

@scene.run_once
def make_light():
    light = Light(
        object_id="my_light",
        type="point",
        position=(0,2,-3),
        rotation=(0.25,0.25,0,1),
        scale=(1.5,1.5,1.5),
        color=(255,0,0)
    )
    scene.add_object(light)

scene.run_tasks()
