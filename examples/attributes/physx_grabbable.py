"""Physics Grabbable Bouncy Box

You can enable physics (gravity) for a scene object by adding the `physx-body` component.

This makes the scene object a freely-moving object. Dynamic bodies have mass, collide with other objects, bounce or slow during collisions, and fall if gravity is enabled.

Here we are adding the `physx-grabbable` component to allow a user's hand-controller to pick up the object in immersive AR/VR.

More properties at <a href='https://github.com/c-frame/physx'>C-Frame PhysX Physics System</a>.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_grab_box():
    # First, enable physics in the scene, and default scene bounding plane and cylinder.
    opt_obj = Object(
        object_id="scene-options",
        persist=True,
    )
    opt_obj.type = "scene-options"
    opt_obj.data["scene-options"] = {"physics": {"enabled": True, "useDefaultScene": True}}
    scene.add_object(opt_obj)

    # Next, create an object with physx-body to obey physics, and allow hands to grab it.
    grab_box = Box(
        persist=True,
        object_id="grab_box",
        depth=0.25,
        height=0.25,
        width=0.25,
        position=(1, 0.126, -2),
        material=Material(color="#96981b"),
        click_listener=ClickListener(enabled=True, bubble=True),
        physx_body=PhysxBody(mass=1),
        physx_material=PhysxMaterial(restitution=1.8),
        physx_grabbable=True,
    )
    scene.add_object(grab_box)


scene.run_tasks()
