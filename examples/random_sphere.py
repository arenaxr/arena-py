from arena import *
import random

scene = Scene(host="arenaxr.org", namespace="public", scene="random")


def random_color():
    return Color(
        red=random.random() * 255,
        green=random.random() * 255,
        blue=random.random() * 255,
    )


def on_click(_scene, evt, _msg):
    if evt.type == "mousedown":
        print("Clicked! Changing color...")
        scene.update_object(sphere, material=Material(color=random_color()))


sphere = Object(
    object_id="random_sphere",
    object_type="sphere",
    position=Position(0, 1.65, 1.75),
    scale=Scale(0.5, 0.5, 0.5),
    material=Material(color=random_color()),
    clickable=True,
    evt_handler=on_click,
)

scene.add_object(sphere)
scene.run_tasks()
