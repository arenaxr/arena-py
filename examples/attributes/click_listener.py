"""Click Listener

Object will listen for mouse events like clicks.

Add the "click-listener" event to a scene object; click-listener is a Component defined in `events.js`. This works for adding other, arbitrary Components. A non-empty message gets sent to the Component's `init: ` function.
"""

import random

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


def click(scene, evt, msg):
    if evt.type == "mouseup":
        print("mouseup!")
    elif evt.type == "mousedown":
        print("mousedown!")


@scene.run_once
def main():
    my_tet = Tetrahedron(
        object_id="my_tet",
        position=(-1, 2, -5),
        clickable=True,
        evt_handler=click,
    )
    scene.add_object(my_tet)


scene.run_tasks()
