"""Environment Presets

Adds one of many predefined background themes to the scene.

Presets available: **none, default, contact, egypt, checkerboard, forest, goaland, yavapai, goldmine, threetowers, poison, arches, tron, japan, dream, volcano, starry, osiris**.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_env():
    env = Entity(
        object_id="env",
        env_presets=EnvPresets(preset="starry"),
        persist=True,
    )
    scene.add_object(env)
    # To change the theme later:
    env.data.env_presets = EnvPresets(preset="arches")
    scene.update_object(env)


scene.run_tasks()
