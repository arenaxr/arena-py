"""Balls

Spray a bunch of spheres into the scene, test physics and impulse.
"""

import random

from arena import *

scene = Scene(host="arenaxr.org", scene="test")


def rando():
    return float(random.randint(0, 10000)) / 1000


def randcolor():
    x = random.randint(0, 255)
    y = random.randint(0, 255)
    z = random.randint(0, 255)
    return (x, y, z)


@scene.run_forever(interval_ms=100)
def make_balls():
    obj = Sphere(
        clickable=True,
        physx_body=PhysxBody(mass=1),
        physx_force_pushable=PhysxForcePushable(force=50),
        position=(rando(), rando(), rando()),
        color=randcolor(),
        ttl=60)

    scene.add_object(obj)

scene.run_tasks()
