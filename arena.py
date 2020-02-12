import json
import random
import signal
import sys
import time

import paho.mqtt.client as mqtt

mqtt_broker = ""
scene_path = ""
client = mqtt.Client(
    "client-" + str(random.randrange(0, 1000000)), clean_session=True, userdata=None
)
object_count = 0
object_list = []


def signal_handler(sig, frame):
    # 	client.publish(scene_path+object_name,"",retain=True)
    global object_list
    objs = len(object_list)
    for i in range(objs):
        my_obj = object_list.pop()
        my_obj.remove()
        i = i
        time.sleep(1)
        sys.exit(0)


def init(broker, path):
    global client
    global scene_path
    global mqtt_broker
    mqtt_broker = broker
    scene_path = path
    print("connecting to broker ", mqtt_broker)
    client.connect(mqtt_broker)
    # add signal handler to remove objects on quit
    signal.signal(signal.SIGINT, signal_handler)


def start():
    global client
    client.loop_start()  # start loop


def stop():
    global client
    client.loop_stop()  # stop loop
    client.disconnect()


def add(obj):
    print("Add called with: " + obj.name)
    if isinstance(obj, Cube):
        print("its a cube")
    if isinstance(obj, Sphere):
        print("its a sphere")


class Cube:
    """Cube object for the arena"""

    loc = ()
    rot = ()
    scale = ()
    color = (255, 255, 255)
    objName = "empty"

    def __init__(self, loc, rot, scale, color):
        """Initializes the data."""
        global object_count
        global object_list
        self.loc = loc
        self.rot = rot
        self.scale = scale
        self.color = color
        print("loc: " + str(self.loc))
        self.objName = str(object_count)
        object_count = object_count + 1
        object_list.append(self)
        self.redraw()

    def update(self, loc, rot, scale, color):
        self.loc = loc
        self.rot = rot
        self.scale = scale
        self.color = color
        self.redraw()

    def __del__(self):
        self.remove()

    def remove(self):
        client.publish(
            scene_path + "/cube_" + self.objName,
            '{"object_id": "cube_' + self.objName + '", "action": "delete"}',
        )
        client.publish(scene_path + "/cube_" + self.objName, "")
        # uncomment to have boxes all fall to the ground at exit
        # client.publish(scene_path+"/cube_"+self.objName,'{"object_id": "cube_'+self.objName+'", "action": "update", "type": "object", "data": {"dynamic-body": {"type": "dynamic"}}}', retain=False)

    def location(self, loc):
        # mosquitto_pub -h oz.andrew.cmu.edu -t /topic/render/cube_1/position -m "x:1; y:2; z:3;"
        self.loc = loc
        update_msg = {
            "object_id": "cube_" + self.objName,
            "action": "update",
            "data": {
                "position": {"x": self.loc[0], "y": self.loc[1], "z": self.loc[2],}
            },
        }
        print("move str: " + json.dumps(update_msg))
        client.publish(
            scene_path + "/cube_" + self.objName, json.dumps(update_msg), retain=False
        )

    def redraw(self):
        print("Cube publish draw command")
        global scene_path
        color_str = "#%06x" % (
            int(self.color[0]) * 65536 + int(self.color[1]) * 256 + int(self.color[2])
        )
        MESSAGE = {
            "object_id": "cube_" + self.objName,
            "action": "create",
            "data": {
                "object_type": "cube",
                "position": {"x": self.loc[0], "y": self.loc[1], "z": self.loc[2]},
                "rotation": {
                    "x": self.rot[0],
                    "y": self.rot[1],
                    "z": self.rot[2],
                    "w": self.rot[3],
                },
                "scale": {"x": self.scale[0], "y": self.scale[1], "z": self.scale[2]},
                "color": color_str,
            },
        }
        cube_str = (
            "cube_"
            + self.objName
            + ", "
            + str(self.loc)[1:-1]
            + ", "
            + str(self.rot)[1:-1]
            + ", "
            + str(self.scale)[1:-1]
            + ","
            + color_str
            + ",on"
        )
        print("cube str: " + cube_str)
        client.publish(
            scene_path + "/cube_" + self.objName, json.dumps(MESSAGE), retain=False
        )


class Sphere:
    """Sphere object for the arena"""


def __init__(self, name):
    """Initializes the data."""
    self.name = name
    print("(Initializing {})".format(self.name))
