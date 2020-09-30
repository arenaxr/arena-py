# shapes.py
#
# MQTT message format: x,y,z,rotX,rotY,rotZ,rotW,scaleX,scaleY,scaleZ,#colorhex,on/off

import arena
import random
import time
import signal

arena.init("arena.andrew.cmu.edu", "realm", "system-tests")


def randmove():
    rando = random.random() * 10 - 5
    return rando


def rando(val):
    rando = random.random() * val
    return round(rando, 3)


def randrot():
    return round((random.random() * 2 - 1), 3)


def randcolor():
    x = random.randint(0, 255)
    y = random.randint(0, 255)
    z = random.randint(0, 255)
    return(x, y, z)


def randobj():
    rando = random.random()
    if rando < 0.2:
        return arena.Shape.cylinder
    if rando < 0.4:
        return arena.Shape.sphere
    if rando < 0.6:
        return arena.Shape.cube
    if rando < 0.8:
        return arena.Shape.torus
    return arena.Shape.cube


def signal_handler(sig, frame):
    exit()


signal.signal(signal.SIGINT, signal_handler)
messages = []
counter = 0
while True:
    obj_type = randobj()
    obj_id = str(counter)
    name = obj_type.value + "_" + obj_id
    counter += 1

    x = round(randmove(), 3)
    y = round(randmove() + 5, 3)
    z = round(randmove() - 5, 3)
    obj = arena.Object(
        objName=name,
        objType=obj_type,
        location=(x, y, z),
        rotation=(randrot(), randrot(), randrot(), randrot()),
        scale=(rando(2), rando(2), rando(2)),
        color=randcolor())
    messages.append(obj)

    # REMOVE
    if len(messages) >= 25:
        theMess = messages.pop(0)
        theMess.delete()
    time.sleep(0.1)
exit()
