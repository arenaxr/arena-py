"""Dynamic-Body Physics

You can enable physics (gravity) for a scene object by adding the dynamic-body component.

This makes the scene object a freely-moving object. Dynamic bodies have mass, collide with other objects, bounce or slow during collisions, and fall if gravity is enabled.

More properties at <a href='https://github.com/c-frame/aframe-physics-system/blob/master/CannonDriver.md'>A-Frame Physics System</a>.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

dynamic_body = DynamicBody(
    type="dynamic",
)


@scene.run_once
def make_drop_box():
    # First, enable physics in the scene.
    opt_obj = Object(
        object_id="scene-options",
        persist=True,
    )
    opt_obj.type = "scene-options"
    opt_obj.data["scene-options"] = {"physics": True}
    scene.add_object(opt_obj)

    # Second, create an static ground Plane for a Box to collide with under gravity.
    # However, currently the ARENA web site does this automatically when ["scene-options"] = {"physics": True}.

    # Third, create an object dynamically obeying gravity.
    box = Box(
        object_id="box_3",
        persist=True,
        position=(0, 5, -2),
        dynamic_body=dynamic_body,
    )
    scene.add_object(box)


scene.run_tasks()
