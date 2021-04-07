from arena import *
import random

scene = Scene(host="arenaxr.org", realm="realm", scene="example")

def click(scene, evt, msg):
    if evt.type == "mouseup":
        print("mouseup!")
    elif evt.type == "mousedown":
        print("mousedown!")

@scene.run_once
def main():
    my_tet = Tetrahedron(
        object_id="my_tet",
        position=(-1,2,-5),
        clickable=True,
        evt_handler=click
    )
    scene.add_object(my_tet)

scene.run_tasks()
