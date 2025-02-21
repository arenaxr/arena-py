"""Impulse

Apply an impulse to an object to set it in motion. This happens in conjunction with an event. Requires click-listener and physics.

One physics feature is applying an impulse to an object to set it in motion. This happens in conjunction with an event. As an example, here are messages setting objects fallBox and fallBox2 to respond to `mouseup` and `mousedown` messages with an impulse with a certain force and position.
"""

import random

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

impulse = Impulse(
    on="mouseup",
    position=(1, 1, 1),
    force=(1, 50, 1),
)


@scene.run_once
def make_click_impulse_ball():
    obj = Sphere(
        object_id="fallBall",
        clickable=True,
        dynamic_body=DynamicBody(type="dynamic"),
        position=(0, 4, -4),
        scale=(0.5, 0.5, 0.5),
        impulse=impulse,
    )
    scene.add_object(obj)


scene.run_tasks()
