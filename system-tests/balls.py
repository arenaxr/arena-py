# balls.py
#
# spray a bunch of spheres into the scene, test physics and impulse

from arena import *
import random

arena = Arena("arena.andrew.cmu.edu", "systest-balls", "realm")


def rando():
    return float(random.randint(0, 10000)) / 1000


def randcolor():
    x = random.randint(0, 255)
    y = random.randint(0, 255)
    z = random.randint(0, 255)
    return (x, y, z)


counter = 0
@arena.run_forever(interval_ms=100)
def make_balls():
    global counter

    obj_id = str(counter)
    name = "sphere" + "_" + obj_id
    counter += 1

    obj = Sphere(
        object_id=obj_id,
        click_listener=True,
        physics=Physics(type="dynamic"),
        impulse=Impulse(position=(1,1,1), force=(1,50,1)),
        position=(rando(), rando(), rando()),
        color=randcolor(),
        ttl=60)

    arena.add_object(obj)

arena.start_tasks()
