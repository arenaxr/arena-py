"""Entity (generic object)

Entities are the base of all objects in the scene. Entities are containers into which components can be attached.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_empty():
    my_ent = Object(
        object_id="invisible_object",
        position=(0, 2, -3),
    )
    scene.add_object(my_ent)


scene.run_tasks()
