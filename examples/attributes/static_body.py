"""Static Body Physics

You can enable physics collisions for a scene object by adding the static-body component.

This makes the scene object a fixed-position or animated object. Other objects may collide with static bodies, but static bodies themselves are unaffected by gravity and collisions.

More properties at <a href='https://github.com/c-frame/aframe-physics-system/blob/master/CannonDriver.md'>A-Frame Physics System</a>.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

static_body = StaticBody(
    type="static",
)


@scene.run_once
def make_drop_plane():
    # First, enable physics in the scene.
    opt_obj = Object(
        object_id="scene-options",
        persist=True,
    )
    opt_obj.type = "scene-options"
    opt_obj.data["scene-options"] = {"physics": True}
    scene.add_object(opt_obj)

    # Now, create an static ground Plane for a Box to collide with under gravity.
    ground_plane = Box(
        object_id="groundPlane",
        persist=True,
        position=(0, -0.01, 0),
        depth=1000,
        width=1000,
        height=0.01,
        material=Material(opacity=0.01, transparent=True),
        static_body=static_body,
    )
    scene.add_object(ground_plane)


scene.run_tasks()
