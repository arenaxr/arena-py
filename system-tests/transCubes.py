# transCubes.py
#
# draw a symmetric structure of transparent mostly red blue (yellow) rectangles

import arena
import random
import time
import signal

arena.init("arena.andrew.cmu.edu", "realm", "systest-transCubes")


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


def randobj():
    rando = random.random()
    if rando < 0.2:
        return "arena.Shape.cylinder"
    if rando < 0.4:
        return "arena.Shape.sphere"
    if rando < 0.6:
        return "arena.Shape.cube"
    if rando < 0.8:
        return "arena.Shape.quad"
    return "arena.Shape.cube"


def do(name, randx, randy, randz, scalex, scaley, scalez, color):
    obj = arena.Object(
        objName=name,
        location=(randx, randy, randz),
        scale=(scalex, scaley, scalez),
        color=color,
        data='{"material": {"transparent": true, "opacity": 0.5}}')
    messages.append(obj)


def signal_handler(sig, frame):
    exit(0)


signal.signal(signal.SIGINT, signal_handler)


messages = []
counter = 0
while True:
    name = "cube_" + str(counter)
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

    # os.system("mosquitto_pub -h " + HOST + " -t " + TOPIC + "/" + name + " -m " + MESSAGE + " -r");
    if len(messages) >= 100:
        for i_ in range(4):
            pop = messages.pop(0)
            pop.delete()

    time.sleep(0.1)
