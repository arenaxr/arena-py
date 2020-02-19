# shapes.py
#
# MQTT message format: x,y,z,rotX,rotY,rotZ,rotW,scaleX,scaleY,scaleZ,#colorhex,on/off

import json
import random
import time

import paho.mqtt.client as mqtt

HOST = "oz.andrew.cmu.edu"
TOPIC = "/topic/transCubes"

client = mqtt.Client(str(random.random()), clean_session=True, userdata=None)
client.connect(HOST)


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
    return "FF" + format(random.randint(128, 208), "x") + "00"


def randblue():
    return "0000" + format(random.randint(128, 255), "x")


def randred():
    return format(random.randint(128, 255), "x") + "0000"


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
        return "cylinder"
    if rando < 0.4:
        return "sphere"
    if rando < 0.6:
        return "cube"
    if rando < 0.8:
        return "quad"
    return "cube"


def do(name, randx, randy, randz, scalex, scaley, scalez, color):
    MESSAGE = {
        "action": "create",
        "object_id": name,
        "type": "object",
        "data": {
            "position": {
                "x": round(randx, 3),
                "y": round(randy, 3),
                "z": round(randz, 3),
            },
            "rotation": {"x": 0, "y": 0, "z": 0, "w": 0},
            "scale": {"x": scalex, "y": scaley, "z": scalez,},
            "color": color,
            "material": {"transparent": True, "opacity": 0.5},
        },
    }
    messages.append(MESSAGE)
    print(json.dumps(MESSAGE))
    client.publish(TOPIC + "/" + name, json.dumps(MESSAGE))


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
            name = pop["object_id"]
            client.publish(
                TOPIC + "/" + name,
                json.dumps({"action": "delete", "object_id": name}),
            )
    time.sleep(0.1)
