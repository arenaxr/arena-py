import json
import random
import signal
import sys
import time
import enum

import paho.mqtt.client as mqtt

# globals
running = False
mqtt_broker = ""
scene_path = ""
client = mqtt.Client(
    "client-" + str(random.randrange(0, 1000000)), clean_session=True, userdata=None
)
object_count = 0
object_list = []
arena_callback = None
messages = []


def signal_handler(sig, frame):
    stop()


def arena_callback(msg):
    #     print("arena_callback called with: " + msg.payload)
    #     jsonMsg = json.loads(msg.payload)
    #     # filter non-event messages
    #     if jsonMsg["action"] != "clientEvent":
    #         return(None)
    #     # filter non-mouse messages
    #     if jsonMsg["type"] != "mousedown" and jsonMsg["type"] != "mouseup":
    #         return
    #     print('got click: %s "%s"' % (msg.topic, msg.payload))

    #     click_x = jsonMsg["data"]["position"]["x"]
    #     click_y = jsonMsg["data"]["position"]["y"]
    #     click_z = jsonMsg["data"]["position"]["z"]
    #     user = jsonMsg["data"]["source"]
    #     # click_x,click_y,click_z,user = msg.payload.split(',')
    #     print("Clicked by: " + user)
    #     obj_x = float(x) - float(click_x)
    #     obj_y = float(y) - float(click_y)
    #     obj_z = float(z) - float(click_z)
    #     if str(msg.topic).find("mousedown") != -1:
    #         print("Obj relative click: " + str(obj_x) + "," + str(obj_y) + "," + str(obj_z))

    arena_callback(msg.payload)


def process_message(msg):
    global arena_callback
    #    print("on_message: "+msg.topic+' '+str(msg.payload))
    if arena_callback:
        arena_callback(msg.payload.decode("utf-8", "ignore"))


def on_message(client, userdata, msg):
    messages.append(msg)


def on_connect(client, userdata, flags, rc):
    print("connected")


# def on_log(client, userdata, level, buf):
#    print("log:" + buf);


def init(broker, realm, scene, callback=None):
    global client
    global scene_path
    global mqtt_broker
    global arena_callback
    mqtt_broker = broker
    scene_path = realm + "/s/" + scene
    arena_callback = callback

    # print("arena callback:", callback)
    # print("connecting to broker ", mqtt_broker)
    client.connect(mqtt_broker)

    # print("subscribing")
    client.subscribe(scene_path + "/#")

    # fall-thru callback for all things on scene
    # not on specific subscribed topics
    client.on_message = on_message

    # client.on_log = on_log
    client.enable_logger()

    # add signal handler to remove objects on quit
    signal.signal(signal.SIGINT, signal_handler)
    start()


def handle_events():
    while running:
        if len(messages) > 0:
            process_message(messages.pop(0))
        else:
            time.sleep(0.1)


def start():
    global client
    global running
    running = True
    print("starting network loop")
    client.loop_start()  # start MQTT network loop
    print("started")


def stop():
    global client
    global running
    running = False
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


class Physics(enum.Enum):
    none = "none"
    static = "static"
    dynamic = "dynamic"


class Shape(enum.Enum):
    cube = "cube"
    sphere = "sphere"
    circle = "circle"
    cone = "cone"
    cylinder = "cylinder"
    dodecahedron = "dodecahedron"
    icosahedron = "icosahedron"
    tetrahedron = "tetrahedron"
    octahedron = "octahedron"
    plane = "plane"
    ring = "ring"
    torus = "torus"
    torusKnot = "torusKnot"
    triangle = "triangle"
    gltf_model = "gltf-model"


class Event(enum.Enum):
    mousedown = "mousedown"
    mouseup = "mouseup"
    mouseenter = "mouseenter"
    mouseleave = "mouseleave"
    collision = "collision"


class MouseEvent:
    """Event data from mouse interaction"""

    location = (0, 0, 0)
    eventType = Event.mousedown
    source = ""

    def __init__(self, location=location, eventType=eventType, source=source):
        self.location = location
        self.eventType = eventType
        self.source = source


class Object:
    """Geometric shape object for the arena type Arena.Shape"""

    objType = Shape.cube
    location = (0, 0, 0)
    rotation = (0, 0, 0, 1)
    scale = (1, 1, 1)
    color = (255, 255, 255)
    objName = ""
    ttl = 0
    persist = False
    physics = Physics.none
    clickable = False
    url = ""
    data = ""
    #    callback = None

    def __init__(
        self,
        objName=objName,
        objType=objType,
        location=location,
        rotation=rotation,
        scale=scale,
        color=color,
        persist=persist,
        ttl=ttl,
        physics=physics,
        clickable=clickable,
        url=url,
        data=data,
        # callback=callback
    ):
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
        self.physics = physics
        self.clickable = clickable
        self.url = url
        self.data = data
        #        self.callback = callback
        # print("loc: " + str(self.loc))
        # avoid name clashes by enumerating each new object
        if objName == "":
            self.objName = self.objType.value + "_" + str(object_count)
        else:
            self.objName = objName

        #        if (callback != None):
        #            print("adding callback")
        #            client.message_callback_add(scene_path+'/'+self.objName, callback)

        object_count = object_count + 1
        object_list.append(self)
        self.redraw()

    def fireEvent(self, event=None, position=(0, 0, 0), source=None):
        if event is None:
            event = arena.Event.mousedown.value
        else:
            event = event.value
        if source is None:
            source = "arenaLibrary"
        MESSAGE = {
            "object_id": self.objName,
            "action": "clientEvent",
            "type": event,
            "data": {
                "position": {"x": position[0], "y": position[1], "z": position[2]},
                "source": source,
            },
        }
        # print("deleting " + json.dumps(MESSAGE))
        # print("client ", client)
        # print ("scene_path ", scene_path)
        client.publish(scene_path, json.dumps(MESSAGE), retain=False)

    def update(
        self,
        location=None,
        rotation=None,
        scale=None,
        color=None,
        physics=None,
        data=None,
        clickable=None,
    ):
        if location is not None:
            self.location = location
        if rotation is not None:
            self.rotation = rotation
        if scale is not None:
            self.scale = scale
        if color is not None:
            self.color = color
        if clickable is not None:
            self.clickable = clickable
        if physics is not None:
            self.physics = physics
        if data is not None:
            self.data = data
        self.redraw()

    #    def __del__(self):
    #        self.delete()

    def delete(self):
        MESSAGE = {"object_id": self.objName, "action": "delete"}
        # print("deleting " + json.dumps(MESSAGE))
        # print("client ", client)
        # print ("scene_path ", scene_path)
        client.publish(scene_path, json.dumps(MESSAGE), retain=False)

    def location(self, location):
        # mosquitto_pub -h oz.andrew.cmu.edu -t /topic/render/cube_1/position -m "x:1; y:2; z:3;"
        self.location = location
        update_msg = {
            "object_id": self.objName,
            "action": "update",
            "data": {
                "position": {
                    "x": self.location[0],
                    "y": self.location[1],
                    "z": self.location[2],
                }
            },
        }
        # print("move str: " + json.dumps(update_msg))
        client.publish(scene_path, json.dumps(update_msg), retain=False)

    def redraw(self):
        # print(self.objType + " publish draw command")
        global scene_path
        color_str = "#%06x" % (
            int(self.color[0]) * 65536 + int(self.color[1]) * 256 + int(self.color[2])
        )
        MESSAGE = {
            "object_id": self.objName,
            "action": "create",
            "type": "object",
            "persist": self.persist,
            "data": {
                "object_type": self.objType.value,
                "position": {
                    "x": self.location[0],
                    "y": self.location[1],
                    "z": self.location[2],
                },
                "rotation": {
                    "x": self.rotation[0],
                    "y": self.rotation[1],
                    "z": self.rotation[2],
                    "w": self.rotation[3],
                },
                "scale": {"x": self.scale[0], "y": self.scale[1], "z": self.scale[2]},
                "color": color_str,
                "url": self.url,
            },
        }
        if self.data != "":
            MESSAGE["data"].update(json.loads(self.data))
        if self.physics != Physics.none:
            MESSAGE["data"]["dynamic-body"] = {"type": self.physics.value}
        if self.clickable:
            MESSAGE["data"]["click-listener"] = ""
        if self.ttl != 0:
            MESSAGE["ttl"] = self.ttl

        # print("publishing " + json.dumps(MESSAGE) + " to " + scene_path)
        client.publish(scene_path, json.dumps(MESSAGE), retain=False)


class Sphere:
    """Sphere object for the arena"""


def __init__(self, name):
    """Initializes the data."""
    self.name = name
    print("(Initializing {})".format(self.name))
