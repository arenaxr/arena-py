# ducks.py
#
# emit ducks when Vive controller trigger pressed
# to view, go to url like https://xr.andrew.cmu.edu/?scene=duck&fixedCamera=duck

import json
import random
import time

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from scipy.spatial.transform import Rotation as R

HOST = "oz.andrew.cmu.edu"
TOPIC = "realm/s/duck/vive-rightHand_duck_duck"
USER = "camera_duck_duck"
FORCE = 50


def rando(val):
    rand = random.random() * val
    return str("{0:0.3f}".format(rand))


def randrot():
    return str("{0:0.3f}".format(random.random() * 2 - 1))


def randcolor():
    return "%06x" % random.randint(0, 0xFFFFFF)


# Globals (yes, Sharon)
trigger_state = "up"
counter = 0
click_x = 0
click_y = 0
click_z = 0
rot_x = 0
rot_y = 0
rot_z = 0
rot_w = 1
x = 0
y = 0
z = 0
xf = 0
yf = 0
zf = 0
r = [0.0, 0.0, 0.0]


# define callbacks
def on_click_input(client, userdata, msg):
    global click_x
    global click_y
    global click_z
    global rot_x
    global rot_y
    global rot_z
    global rot_w
    global x
    global y
    global z
    global counter
    global trigger_state
    global xf
    global yf
    global zf
    global r

    obj_id = str(counter)
    name = "duck_" + obj_id

    # print("got %s \"%s\"" % (msg.topic, msg.payload))

    jsonMsg = json.loads(msg.payload.decode("utf-8"))
    # filter non-event messages
    if jsonMsg["action"] == "update":
        click_x = jsonMsg["data"]["position"]["x"]
        click_y = jsonMsg["data"]["position"]["y"]
        click_z = jsonMsg["data"]["position"]["z"]
        rot_x = jsonMsg["data"]["rotation"]["x"]
        rot_y = jsonMsg["data"]["rotation"]["y"]
        rot_z = jsonMsg["data"]["rotation"]["z"]
        rot_w = jsonMsg["data"]["rotation"]["w"]

        rq = R.from_quat([rot_x, rot_y, rot_z, rot_w])
        v = [0, 0, -1]
        r = rq.apply(v)  # multiply unit vector by rotation to get direction

        xf = r[0] * FORCE
        yf = r[1] * FORCE
        zf = r[2] * FORCE

    if jsonMsg["action"] != "clientEvent":
        return

    # filter non-mouse messages
    if jsonMsg["type"] == "triggerdown":
        trigger_state = "down"
        counter += 1
    elif jsonMsg["type"] == "triggerup":
        trigger_state = "up"
    else:
        return

    if trigger_state == "down":
        # print("got click: %s \"%s\"" % (msg.topic, msg.payload))
        # print(xf,yf,zf)
        MESSAGE = {
            "object_id": name,
            "action": "create",
            "ttl": 10,
            "data": {
                "dynamic-body": {"type": "dynamic"},
                "impulse": {
                    "on": "mousedown",
                    "force": str(xf) + " " + str(yf) + " " + str(zf),
                    "click-listener": "",
                    "position": "1 1 1",
                },
                "object_type": "gltf-model",
                "url": "models/Duck.glb",
                "position": {
                    "x": "{0:0.3f}".format(click_x),
                    "y": "{0:0.3f}".format(click_y),
                    "z": "{0:0.3f}".format(click_z),
                },
                "scale": {"x": 0.2, "y": 0.2, "z": 0.2},
                "rotation": {
                    "x": randrot(),
                    "y": randrot(),
                    "z": randrot(),
                    "w": randrot(),
                },
            },
        }
        publish.single(TOPIC, json.dumps(MESSAGE), hostname=HOST, retain=False)

        time.sleep(0.15)  # if we don't pause, mousedown events don't always get through

        MESSAGE = {
            "object_id": name,
            "action": "clientEvent",
            "type": "mousedown",
            "data": {"position": {"x": 0, "y": 0, "z": 0}, "source": "duckprogram"},
        }
        publish.single(TOPIC, json.dumps(MESSAGE), hostname=HOST, retain=False)


client = mqtt.Client(str(random.random()), clean_session=True, userdata=None)
client.connect(HOST)

print("subscribing")
client.subscribe(TOPIC)

print("adding callback")
client.message_callback_add(TOPIC, on_click_input)

print("starting main loop")
client.loop_start()  # doesn't really do anything but wait for events

while True:
    time.sleep(1)

client.disconnect()
client.loop.stop()
