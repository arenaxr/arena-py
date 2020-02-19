# shapes.py
#
# MQTT message format: x,y,z,rotX,rotY,rotZ,rotW,scaleX,scaleY,scaleZ,#colorhex,on/off

import json
import random
import time

import paho.mqtt.client as mqtt

HOST = "oz.andrew.cmu.edu"
TOPIC = "realm/s/refactor"

client = mqtt.Client(str(random.random()), clean_session=True, userdata=None)
client.connect(HOST)


def randmove():
    rando = random.random() * 10 - 5
    return rando


def rando(val):
    rando = random.random() * val
    return round(rando, 3)


def randrot():
    return round((random.random() * 2 - 1), 3)


def randcolor():
    return "%06x" % random.randint(0, 0xFFFFFF)


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


messages = []
counter = 0
while True:
    obj_type = randobj()
    obj_id = str(counter)
    name = obj_type + "_" + obj_id
    counter += 1

    MESSAGE = {
        "object_id": name,
        "action": "create",
        "data": {
            "object_type": obj_type,
            "position": {
                "x": round(randmove(), 3),
                "y": round(randmove() + 5, 3),
                "z": round(randmove() - 5, 3),
            },
            "rotation": {
                "x": randrot(),
                "y": randrot(),
                "z": randrot(),
                "w": randrot(),
            },
            "scale": {"x": rando(2), "y": rando(2), "z": rando(2),},
            "color": "#" + randcolor(),
        },
    }
    messages.append(MESSAGE)
    print(json.dumps(MESSAGE))

    # os.system("mosquitto_pub -h " + HOST + " -t " + TOPIC + "/" + name + " -m " + MESSAGE + " -r");
    client.publish(TOPIC + "/" + name, json.dumps(MESSAGE))

    # REMOVE
    if len(messages) >= 25:
        theMess = messages.pop(0)
        theId = theMess["object_id"]
        newMess = {"object_id": theId, "action": "delete"}
        client.publish(TOPIC + "/" + theId, json.dumps(newMess))
    time.sleep(0.1)
