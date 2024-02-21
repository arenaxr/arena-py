# balance.py
#
# balance cube on one corner on a moving plane, test physics with rtt

from arena import *

scene = Scene(host="arenaxr.org", scene="test")


@scene.run_once
def make_test():
    free = Box(
        object_id="free_box",
        dynamic_body=DynamicBody(
            type="dynamic",
            mass=5,
            angularDamping=0.01,
            linearDamping=0.01,
        ),
        position=(0, 1, -2),
        rotation=(45, 0, 35.264),  # rotation to balance on one corner
    )
    scene.add_object(free)
    control = Plane(
        object_id="control_plane",
        static_body=StaticBody(type="static"),
        position=(0, 0.1, -2),
        rotation=(-90, 0, 0),
        scale=(2, 2, 2),
        material=Material(opacity=0.5),
    )
    scene.add_object(control)


scene.run_tasks()
