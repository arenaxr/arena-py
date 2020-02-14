# balls.py
#
# spray a bunch of spheres into the scene, test physics

import json
import random
import time

import paho.mqtt.client as mqtt

HOST = "oz.andrew.cmu.edu"
TOPIC = "realm/s/balls"


def randrot():
    # return str("{0:0.3f}".format(random.random() * 2 - 1))
    return "0"


def randy():
    return str("{0:0.3f}".format(random.random() * 2 - 1))


def randcolor():
    return "%06x" % random.randint(0, 0xFFFFFF)


client = mqtt.Client(str(random.random()), clean_session=True, userdata=None)
client.connect(HOST)

counter = 0
while True:
    obj_id = str(counter)
    name = "sphere" + "_" + obj_id
    counter += 1

    MESSAGE = {
        "object_id": name,
        "action": "create",
        "ttl": 40,
        "data": {
            "dynamic-body": {"type": "dynamic"},
            "object_type": "sphere",
            "position": {"x": randy(), "y": "{0:0.3f}".format(0), "z": randy(),},
            "rotation": {
                "x": randrot(),
                "y": randrot(),
                "z": randrot(),
                "w": randrot(),
            },
            "color": "#" + randcolor(),
        },
    }
    MESSAGE_string = json.dumps(MESSAGE)
    print(MESSAGE_string)

    client.publish(TOPIC + "/" + name, MESSAGE_string)
    time.sleep(0.1)
