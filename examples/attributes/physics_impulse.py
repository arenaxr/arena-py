from arena import *
import random

scene = Scene(host="arenaxr.org", scene="example")

@scene.run_once
def make_bouncy_ball():
    obj = Sphere(
        clickable=True,
        physics=Physics(type="dynamic"),
        impulse=Impulse(position=(1,1,1), force=(1,50,1)),
        position=(0,5,0))

    scene.add_object(obj)

scene.run_tasks()
