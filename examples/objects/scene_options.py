"""Scene Options

ARENA Scene Options allow customizing the scene environment, fog, and other global settings.

Adds one of many predefined backgrounds ( one of: **none, default, contact, egypt, checkerboard, forest, goaland, yavapai, goldmine, threetowers, poison, arches, tron, japan, dream, volcano, starry, osiris**) to the scene.

Customize the fog, or remove the 'enter VR' icon, and other scene-level settings.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def update_environment():
    opt_obj = Object(
        object_id="scene-options",
        persist=True,
    )
    opt_obj.type = "scene-options"
    # Set background theme
    opt_obj.data["env-presets"] = {"preset": "arches"}
    # Customize fog
    opt_obj.data["scene-options"] = {
        "fog": {"type": "linear", "color": "#F00"},
    }
    scene.add_object(opt_obj)


scene.run_tasks()
