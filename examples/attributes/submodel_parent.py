"""Sub-Model Parent

When this object is parented to a hierarchical model, it attaches to a named sub-component of that model instead of the root position. Requires `parent` attribute.

This program loads a URDF model of a robot arm, and then attaches a see-though green ball at the tip of the armature at the sub-model component named `joint_6_t-flange` of the URDF model.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_model_container():
robot_arm = UrdfModel(
    object_id="robot_arm",
    position=(0, 0, -3),
    rotation=(-90, 0, 0),
    scale=(1, 1, 1),
    url="/store/users/mwfarb/xacro/motoman_gp4_support/urdf/gp4.xacro",
    urlBase="/store/users/mwfarb/xacro/motoman_gp4_support",
)
scene.add_object(robot_arm)
green_ball = Sphere(
    object_id="green_ball",
    parent=robot_arm.object_id,
    scale=(0.05, 0.05, 0.05),
    material={"color": "#00ff00", "transparent": True, "opacity": 0.45},
    submodel_parent="joint_6_t-flange",
)
scene.add_object(green_ball)

scene.run_tasks()
