"""Background Themes

ARENA Scene Options.

Adds one of many predefined backgrounds ( one of: **none, default, contact, egypt, checkerboard, forest, goaland, yavapai, goldmine, threetowers, poison, arches, tron, japan, dream, volcano, starry, osiris**) to the scene.
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
    opt_obj.data["env-presets"] = {"preset": "arches"}
    scene.add_object(opt_obj)


scene.run_tasks()
