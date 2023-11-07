# earth-moon-laser.py
""" Simple program to animate the earth and moon with a laser pointer. """
from arena import *


def click_pointer(scene, evt, msg):
    """Emit a 1-second laser line and target for each user click"""
    if evt.type == "mousedown":
        start = evt.data.clickPos
        end = evt.data.position
        start.y = start.y - 0.1
        line = ThickLine(path=(start, end), color=(255, 0, 0), lineWidth=5, ttl=1)
        scene.add_object(line)
        ball = Sphere(position=end, scale=(0.06, 0.06, 0.06), color=(255, 0, 0), ttl=1)
        scene.add_object(ball)


scene = Scene(host="arenaxr.org", scene="earth")
earth = GLTF(
    object_id="gltf-model_Earth",
    scale=(10, 10, 10),
    url="store/users/wiselab/models/Earth.glb",
    clickable=True,
    persist=True,
    animation=Animation(
        property="rotation", end=(0, 360, 0), loop=True, dur=20000, easing="linear"
    ),
    evt_handler=click_pointer,
)
moon = GLTF(
    object_id="gltf-model_Moon",
    position=(0, 0.05, 0.6),
    scale=(0.05, 0.05, 0.05),
    url="store/users/wiselab/models/Moon.glb",
    persist=True,
    parent="gltf-model_Earth",
)
scene.add_objects([earth, moon])
scene.run_tasks()
