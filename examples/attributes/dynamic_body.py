"""Physics

You can enable physics (gravity) for a scene object by adding the dynamic-body Component.
"""

import random

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

dynamic_body = DynamicBody(
    type="dynamic",
)


@scene.run_once
def make_drop_box():
    obj = Sphere(
        object_id="box_3",
        position=(0, 5, 0),
        dynamic_body=dynamic_body,
    )
    scene.add_object(obj)


scene.run_tasks()
