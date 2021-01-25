# transBoxs.py
#
# draw a symmetric structure of transparent mostly red blue (yellow) rectangles

from arena import *
import random
import time


arena = Arena(host="arena.andrew.cmu.edu", realm="realm", scene="test")


def randmove():
    rando = random.random() * 10 - 5
    return rando


def rando(val):
    rand = random.random() * val
    return round(rand, 3)


def randrot():
    return round((random.random() * 2 - 1), 3)


def unhex(a):
    return int(a, 16)


def randgold():
    return (255, random.randint(128, 208), 0)


def randblue():
    return (0, 0, random.randint(128, 255))


def randred():
    return (random.randint(128, 255), 0, 0)


def randcolor():
    rando = random.random()
    if rando < 0.2:
        return randgold()
    if rando < 0.4:
        return randblue()
    if rando < 0.6:
        return randgold()
    if rando < 0.8:
        return randblue()
    return randred()


def do(name, randx, randy, randz, scalex, scaley, scalez, color):
    obj = Box(
            object_id=name,
            position=(randx, randy, randz),
            scale=(scalex, scaley, scalez),
            color=color,
            material=Material(transparent=True, opacity=0.5),
            animation=Animation(property="rotation", to="0 360 0", loop=5, dur=10000, easing="linear")
        )
    arena.add_object(obj)


counter = 0
@arena.run_forever
def do_stuff():
    global counter

    name = "box_" + str(counter)
    counter += 1
    randx = randmove()
    randy = randmove()
    randz = randmove()
    scalex = rando(8)
    scaley = rando(1)
    scalez = rando(4)
    color = randcolor()
    do(name, randx, randy, randz, scalex, scaley, scalez, color)
    do(name + "a", -randx, randy, randz, scalex, scaley, scalez, color)

    randx = randmove()
    randy = randmove()
    randz = randmove()
    scalex = rando(1)
    scaley = rando(8)
    scalez = rando(4)
    color = randcolor()
    do(name + "b", randx, -randy, randz, scalex, scaley, scalez, color)
    do(name + "c", -randx, -randy, randz, scalex, scaley, scalez, color)

arena.run_tasks()
