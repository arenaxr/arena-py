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
arena_callback = lambda: None
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

def our_callback(client, userdata, msg):
    print("received callback: ", msg)
    arena_callback(msg)

def on_connected():
    print("connected callback")

def init(broker, realm, scene, callback=arena_callback):
    global client
    global scene_path
    global mqtt_broker
    global arena_callback
    mqtt_broker = broker
    scene_path = realm + '/s/' + scene
    arena_callback = callback
        
    print("connecting to broker ", mqtt_broker)
    client.connect(mqtt_broker)
    client.message_callback_add(scene_path+'/#', our_callback)
    # add signal handler to remove objects on quit
    signal.signal(signal.SIGINT, signal_handler)


def start():
    global client
    client.loop_start()  # start loop


def stop():
    global client
    print("stopping client loop")
    client.loop_stop()  # stop loop
    print("disconnecting")
    client.disconnect()
    print("disconnected")


def add(obj):
    print("Add called with: " + obj.name)
    if isinstance(obj, Cube):
        print("its a cube")
    if isinstance(obj, Sphere):
        print("its a sphere")

class Object:
    """Geometric shape object for the arena
    one of cube, sphere, circle, cone, cylinder, dodecahedron, icosahedron, tetrahedron, octahedron, plane, ring, torus, torusKnot, triangle"""

    objType = "cube"
    location = (0, 0, 0)
    rotation = (0, 0, 0, 1)
    scale = (1, 1, 1)
    color = (255, 255, 255)
    objName = ""
    ttl = 0
    persist = False
    physical = False
    clickable = False
    url = ""

    def __init__(self, objType=objType, location=location, rotation=rotation, scale=scale, color=color, persist=persist, ttl=ttl, physical=physical, clickable=clickable, url=url):
        """Initializes the data."""
        global object_count
        global object_list
        self.objType = objType
        self.location = location
        self.rotation = rotation
        self.scale = scale
        self.color = color
        self.persist = persist
        self.ttl = ttl
        self.physical = physical
        self.clickable = clickable
        self.url = url
        #print("loc: " + str(self.loc))
        # avoid name clashes by enumerating each new object
        self.objName = self.objType + '_' + str(object_count)
        object_count = object_count + 1
        object_list.append(self)
        self.redraw()

    def update(self, location, rotation, scale, color):
        self.location = location
        self.rotation = rotation
        self.scale = scale
        self.color = color
        self.redraw()

    def __del__(self):
        self.remove()

    def remove(self):
        MESSAGE = {
            "object_id": self.objName,
            "action": "delete"
            }
        print("deleting " + json.dumps(MESSAGE))
        print("client ", client)
        print ("scene_path ", scene_path)
        client.publish(scene_path, json.dumps(MESSAGE), retain=False)

    def location(self, location):
        # mosquitto_pub -h oz.andrew.cmu.edu -t /topic/render/cube_1/position -m "x:1; y:2; z:3;"
        self.location = location
        update_msg = {
            "object_id": self.objName,
            "action": "update",
            "data": {
                "position": {"x": self.location[0],
                             "y": self.location[1],
                             "z": self.location[2],}
            },
        }
        #print("move str: " + json.dumps(update_msg))
        client.publish(
            scene_path, json.dumps(update_msg), retain=False
        )

    def redraw(self):
        #print(self.objType + " publish draw command")
        global scene_path
        color_str = "#%06x" % (
            int(self.color[0]) * 65536 + int(self.color[1]) * 256 + int(self.color[2])
        )
        MESSAGE = {
            "object_id": self.objName,
            "action": "create",
            "type": "object",
            "ttl": self.ttl,
            "data": {
                "object_type": self.objType,
                "position": {
                    "x": self.location[0],
                    "y": self.location[1],
                    "z": self.location[2]
                },
                "rotation": {
                    "x": self.rotation[0],
                    "y": self.rotation[1],
                    "z": self.rotation[2],
                    "w": self.rotation[3],
                },
                "scale": {
                    "x": self.scale[0],
                    "y": self.scale[1],
                    "z": self.scale[2]
                },
                "color": color_str,
                "persist": self.persist,
                "physical": self.physical,
                "clickable": self.clickable,
                "url": self.url
            },
        }
        #print("publishing " + json.dumps(MESSAGE) + " to " + scene_path)
        client.publish(
            scene_path, json.dumps(MESSAGE), retain=False
        )


class Sphere:
    """Sphere object for the arena"""


def __init__(self, name):
    """Initializes the data."""
    self.name = name
    print("(Initializing {})".format(self.name))
