"""Physics Pushable Bouncy Ball

Apply an impulse to an object to set it in motion. This happens in conjunction with an event. Requires `click-listener` and `physics`.

One physics feature is applying an impulse to an object to set it in motion. This happens in conjunction with an event. As an example, here we are setting object `bounce_ball` to respond to `mousedown` messages with an impulse with a certain force.

More properties at <a href='https://github.com/c-frame/physx'>C-Frame PhysX Physics System</a>.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_bounce_ball():
    # First, enable physics in the scene, and default scene bounding plane and cylinder.
    opt_obj = Object(
        object_id="scene-options",
        persist=True,
    )
    opt_obj.type = "scene-options"
    opt_obj.data["scene-options"] = {"physics": {"enabled": True, "useDefaultScene": True}}
    scene.add_object(opt_obj)

    # Next, create an object with physx-body to obey physics, and allow clicks to push it.
    bounce_ball = Sphere(
        persist=True,
        object_id="bounce_ball",
        radius=0.25,
        position=(0, 4, -1),
        material=Material(color="#ab1717"),
        click_listener=ClickListener(enabled=True, bubble=True),
        physx_body=PhysxBody(mass=1),
        physx_material=PhysxMaterial(restitution=1.87),
        physx_force_pushable=PhysxForcePushable(force=10),
    )
    scene.add_object(bounce_ball)


scene.run_tasks()
