# balls.py
#
# spray a bunch of spheres into the scene, test physics and impulse

from arena import *
import random

scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="test")


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
        physics=Physics(type="dynamic"),
        impulse=Impulse(position=(1,1,1), force=(1,50,1)),
        position=(rando(), rando(), rando()),
        color=randcolor(),
        ttl=60)

    scene.add_object(obj)

scene.run_tasks()
