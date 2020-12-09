import enum
import json
import random
import signal
import sys
import time
from datetime import datetime
from threading import Event

import paho.mqtt.client as mqtt

from arena import auth

# globals
running = False
mqtt_broker = ""
scene_path = ""
client = mqtt.Client(
    "client-" + str(random.randrange(0, 1000000)), clean_session=True, userdata=None
)
object_count = 0
callbacks = {}
secondary_callbacks = {}
arena_callback = None
messages = []
debug_toggle = False
pseudoclick = None  # (x,y) tuple of pixel coordinates to display clicks
msgs_ready = Event()


def signal_handler(sig, frame):
    stop()


#def arena_callback(msg):
#    arena_callback(msg.payload)


def arena_publish(scene_path, MESSAGE):
    #print(json.dumps(MESSAGE))

    d = datetime.now().isoformat()[:-3]+'Z'
    MESSAGE["timestamp"] = d
    client.publish(scene_path, json.dumps(MESSAGE), retain=False)


def process_message(msg):
    global arena_callback
    global pseudoclick
    #print("process_message: "+str(msg.payload))

    # manage secondary subscriptions to the same bus, not always JSON
    for sub in secondary_callbacks:
        if mqtt.topic_matches_sub(sub, msg.topic):
            secondary_callbacks[sub](msg)
            return

    # otherwise, all arena object data is required to be JSON
    # first call specific objects' callbacks
    payload = msg.payload.decode("utf-8", "ignore")
    try:
        MESSAGE = json.loads(payload)
    except:
        if debug_toggle:
            print("JSON parsing failed!")
        return

    if "object_id" in MESSAGE:
        object_id = MESSAGE["object_id"]
    else:
        if debug_toggle:
            print("Message has no object_id!")

    if pseudoclick:  # display random clicks in right corner for demos
        if MESSAGE["action"] == "clientEvent" and MESSAGE["type"] == "mousedown":
            draw_psuedoclick(xpix=pseudoclick[0], ypix=pseudoclick[1])

    if object_id in callbacks:
        evtType = 'object' # event type is required
        clickPos=(0,0,0)
        Pos=(0,0,0)
        Rot=(0,0,0,1)
        Src=""
        # Unpack JSON data
        objId  = MESSAGE["object_id"]
        Action = MESSAGE["action"] # create/delete/update/clientEvent
        if ("type" in MESSAGE):
            evtType = MESSAGE["type"] # object/rig/mousedown/mouseup/mouseenter/mouseleave/controler++
        if ("data" in MESSAGE):
            if ("clickPos" in MESSAGE["data"]):
                clickPos = (MESSAGE["data"]["clickPos"]["x"],MESSAGE["data"]["clickPos"]["y"],MESSAGE["data"]["clickPos"]["z"])
            if ("position" in MESSAGE["data"]):
                Pos = (MESSAGE["data"]["position"]["x"],MESSAGE["data"]["position"]["y"],MESSAGE["data"]["position"]["z"])
            if ("rotation" in MESSAGE["data"]):
                Rot = (MESSAGE["data"]["rotation"]["x"],MESSAGE["data"]["rotation"]["y"],MESSAGE["data"]["rotation"]["z"],MESSAGE["data"]["rotation"]["w"])
            if ("source" in MESSAGE["data"]):
                Src = MESSAGE["data"]["source"]
        # slight oversight: MQTT messages don't set 'type' for delete events
        if (Action == 'delete'):
            evtType = 'object'

        # Repackage into & return a GenericEvent
        event_data = GenericEvent(
            object_id=objId,
            event_action=EventAction[Action],# delete/create/update/clientEvent
            event_type=EventType[evtType],  # object/rig/mouseup/mousedown/mouseenter/mouseleave/collision/controller++
            position=Pos,
            rotation=Rot,
            click_pos=clickPos,
            source=Src)
        callbacks[object_id](event_data)

    # else call general callback set at init time, for all messages
    elif arena_callback:
        arena_callback(payload)


def draw_psuedoclick(xpix, ypix):
    x = (xpix + random.randrange(-10, 10)) / 10000
    y = (ypix + random.randrange(-10, 10)) / 10000
    Object(objType=Shape.circle, scale=(
        0.003, 0.003, 0.003), location=(x, y, -0.1), ttl=0.1,
        transparency=Transparency(True, 0.3), parent="myCamera")


def on_message(client, userdata, msg):
    messages.append(msg)
    msgs_ready.set()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected")
    else:
        print("connection error, result code: " + rc)


# def on_log(client, userdata, level, buf):
#    print("log:" + buf)


def init(broker, realm, scene, callback=None, port=None, democlick=None, webhost='xr.andrew.cmu.edu'):
    global client
    global scene_path
    global mqtt_broker
    global arena_callback
    global debug_toggle
    global pseudoclick
    debug_toggle = False
    mqtt_broker = broker
    scene_path = realm + "/s/" + scene
    arena_callback = callback
    pseudoclick = democlick

    data = auth.authenticate(realm, scene, broker, webhost=webhost,
                                    debug=debug_toggle)
    if 'username' in data and 'token' in data:
        client.username_pw_set(username=data['username'], password=data['token'])

    #print("arena callback:", callback)
    #print("connecting to broker ", mqtt_broker)
    #print("scene_path ", scene_path)
    if (port != None):
        client.connect(mqtt_broker, port)
    else:
        client.connect(mqtt_broker)

    # print("subscribing")
    client.subscribe(scene_path + "/#")

    # fall-thru callback for all things on scene
    # not on specific subscribed topics
    client.on_connect = on_connect
    client.on_message = on_message

    # client.on_log = on_log
    client.enable_logger()

    # add signal handler to remove objects on quit
    signal.signal(signal.SIGINT, signal_handler)
    start()

def poll_events():
    # Instead of while loop, just manually cycle through any pending events in mqtt queue
    # This can be used if you don't want handle_events() to loop forever at the end of your program.
    # Instead you need to periodically call poll_events() from your main thread
    if running:
        for i in messages:
            process_message(messages.pop(0))

def handle_events():
    # process messages are available
    # if not, block until messages arrive
    while running:
        if len(messages) > 0:
            process_message(messages.pop(0))
        else:
            msgs_ready.clear()
            msgs_ready.wait()

def flush_events():
    if running:
        while len(messages) > 0:
            print("flush_events")
            process_message(messages.pop(0))

def start():
    global client
    global running
    running = True
    print("starting network loop")
    client.loop_start()  # start MQTT network loop
    print("started")


def add_topic(sub, callback):
    """Subscribes to new topic and adds filter for callback to on_message()"""
    global client
    secondary_callbacks[sub] = callback
    client.subscribe(sub)


def remove_topic(sub):
    """Unsubscribes to topic and removes filter for callback"""
    global client
    client.unsubscribe(sub)


def debug():
    global debug_toggle
    debug_toggle = True


def stop():
    global client
    global running
    running = False
    print("stopping client loop")
    client.loop_stop()  # stop loop
    print("disconnecting")
    client.disconnect()
    print("disconnected")
    sys.exit()


def agran(float_num):
    """Reduces floating point numbers to ARENA granularity."""
    return round(float_num, 3)


def get_network_persisted_obj(object_id, broker, scene):
    # pass token to persist
    data = auth._urlopen(
        url=f'https://{broker}/persist/{scene}/{object_id}', creds=True)
    output = json.loads(data)
    return output


def get_network_persisted_scene(broker, scene):
    # pass token to persist
    data = auth._urlopen(
        url=f'https://{broker}/persist/{scene}', creds=True)
    output = json.loads(data)
    return output


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
    image = "image"
    particle = "particle"
    text = "text"
    line = "line"
    light = "light"
    thickline = "thickline"


class EventType(enum.Enum):
    """Values of  MQTT 'type'"""

    rig = "rig"
    object = "object"
    mousedown = "mousedown"
    mouseup = "mouseup"
    mouseenter = "mouseenter"
    mouseleave = "mouseleave"
    collision = "collision"
    triggerdown = "triggerdown"
    triggerup = "triggerup"
    gripdown = "gripdown"
    gripup = "gripup"
    menudown = "menudown"
    menuup = "menuup"
    systemdown = "systemdown"
    systemup = "systemup"
    trackpaddown = "trackpaddown"
    trackpadup = "trackpadup"

class ObjectType(enum.Enum):
    object = "object"
    rig = "rig"
    bone = "bone"

class EventAction(enum.Enum):
    """Kinds of actions"""

    delete = "delete"
    create = "create"
    update = "update"
    clientEvent = "clientEvent"

class Transparency:
    transparent = False
    opacity = 1
    def __init__(self, transparent=transparent, opacity=opacity):
        self.transparent = transparent
        self.opacity = opacity

class Line:
    start = (0, 0, 0)
    end = (0, 0, 0)
    line_width = 1
    color = "#FFFFFF"
    def __init__(self, start=start, end=end, line_width=line_width, color=color):
        self.start = start
        self.end = end
        self.line_width = line_width
        self.color = color

class Thickline:
    path = [] # array of tuple coordinates
    line_width = 1
    color = "#FFFFFF"
    def __init__(self, path=path, line_width=line_width, color=color):
        self.path = path
        self.line_width = line_width
        self.color = color

class Impulse:
    on = None
    force = (0, 0, 0)
    position = (0, 0, 0)
    def __init__(self, on=on, force=force, position=position):
        self.on = on
        self.force = force
        self.position = position

class Animation:
    clip = ""
    loop = ""
    repetitions = 1
    timeScale = 1
    def __init__(self, clip=clip, loop=loop, repetitions=repetitions, timeScale=timeScale):
        self.clip = clip
        self.loop = loop
        self.repetitions = repetitions
        self.timeScale = timeScale


class GenericEvent:
    """Event data any ARENA event"""
    object_id = ""
    event_action = EventAction.clientEvent
    event_type = EventType.mousedown
    update_type = ObjectType.object
    position = (0, 0, 0)
    rotation = (0, 0, 0, 1)
    click_pos = (0, 0, 0)
    source = ""

    def __init__(self, object_id=object_id, event_action=event_action, event_type=event_type, update_type=update_type, position=position, rotation=rotation, click_pos=click_pos, source=source):
        self.object_id = object_id
        self.event_action = event_action
        self.event_type = event_type
        self.update_type = update_type
        self.position = position
        self.rotation = rotation
        self.click_pos = click_pos
        self.source = source

class ClickEvent:
    """Event data e.g. mouse interaction"""
    object_id = ""
    position = (0, 0, 0)
    click_pos = (0, 0, 0)
    event_type = EventType.mousedown
    source = ""

    def __init__(self, object_id=object_id, position=position, click_pos=click_pos, event_type=event_type, source=source):
        self.object_id = object_id
        self.position = position
        self.click_pos=click_pos
        self.event_type = event_type
        self.source = source


class updateRig:
    def __init__(self, object_id, position, rotation):
        global debug_toggle
        MESSAGE = {
            "object_id": object_id,
            "action": "update",
            "type": "rig",
            "data": {
                "position": {
                    "x": agran(position[0]),
                    "y": agran(position[1]),
                    "z": agran(position[2])
                    },
                "rotation": {
                    "x": agran(rotation[0]),
                    "y": agran(rotation[1]),
                    "z": agran(rotation[2]),
                    "w": agran(rotation[3])
                },
            },
        }
        if debug_toggle:
            print(json.dumps(MESSAGE))
        arena_publish(scene_path, MESSAGE)


class updateBone:
    object_id = ""
    bone_id = ""
    position = None
    rotation = None
    scale = None
    def __init__(self, object_id=object_id, bone_id=bone_id, position=position, rotation=rotation, scale=scale):
        global debug_toggle
        MESSAGE = {
            "object_id": object_id,
            "bone": bone_id,
            "action": "update",
            "type": "bone",
            "data": {}
        }
        if (position != None):
            pos = {
                "x": agran(position[0]),
                "y": agran(position[1]),
                "z": agran(position[2])
            }
            MESSAGE["data"]["position"]=pos
        if (rotation != None):
            rot= {
                "x": agran(rotation[0]),
                "y": agran(rotation[1]),
                "z": agran(rotation[2]),
                "w": agran(rotation[3])
                }
            MESSAGE["data"]["rotation"] = rot
        if (scale != None):
            sc = {
                "x": agran(scale[0]),
                "y": agran(scale[1]),
                "z": agran(scale[2])
                }
            MESSAGE["data"]["scale"] = sc

        if debug_toggle:
            print(json.dumps(MESSAGE))
        arena_publish(scene_path, MESSAGE)


def tuple_to_string(tuple):
    return str(tuple[0])+' '+str(tuple[1])+' '+str(tuple[2])


class Object:
    """Geometric shape object for the arena type Arena.Shape"""

    objType = Shape.cube
    location = (0, 0, 0)
    rotation = (0, 0, 0, 1)
    scale = (1, 1, 1)
    color = (255, 255, 255)
    objName = ""
    ttl = 0
    parent = ""
    persist = False
    physics = Physics.none
    clickable = False
    url = ""
    text = None
    transparentOcclude = False
    line = None
    thickline = None
    collision_listener = False
    transparency = None
    impulse = None
    animation = None
    data = ""
    callback = None

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
        parent=parent,
        clickable=clickable,
        transparency=transparency,
        impulse=impulse,
        animation=animation,
        url=url,
        text=text,
        transparentOcclude=transparentOcclude,
        line=line,
        thickline=thickline,
        collision_listener=collision_listener,
        data=data,
        callback=callback
    ):
        """Initializes the data."""
        global object_count
        global object_list
        global debug_toggle
        self.objType = objType
        self.location = location
        self.rotation = rotation
        self.scale = scale
        self.color = color
        self.persist = persist
        self.ttl = ttl
        self.parent = parent
        self.physics = physics
        self.clickable = clickable
        self.url = url
        self.text = text
        self.transparentOcclude = transparentOcclude
        self.line = line
        self.thickline = thickline
        self.collision_listener = collision_listener
        self.transparency = transparency
        self.impulse = impulse
        self.data = data
        self.callback = callback
        # print("loc: " + str(self.loc))
        # avoid name clashes by enumerating each new object
        if objName == "":
            self.objName = self.objType.value + "_" + str(object_count)
        else:
            self.objName = objName

        if (callback != None):
            #print("adding callback")
            callbacks[self.objName] = callback

        object_count = object_count + 1
        #object_list.append(self)

        # do all the work
        self.redraw()

    def fireEvent(self, event=None, position=(0, 0, 0), source=None):
        global debug_toggle
        if event is None:
            event = EventType.mousedown.value
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

        if debug_toggle:
            print(json.dumps(MESSAGE))
        arena_publish(scene_path, MESSAGE)

    def update(
            self,
            location=None,
            rotation=None,
            scale=None,
            color=None,
            physics=None,
            data=None,
            clickable=None,
            ttl=None,
            url=None,
            text=None,
            transparentOcclude=None,
            line=None,
            thickline=None,
            collision_listener=None,
            animation=None,
            transparency=None,
            impulse=None,
            parent=None,
            persist=None):
        global debug_toggle
        if persist is not None:
            self.persist = persist
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
        if ttl is not None:
            self.ttl = ttl
        if url is not None:
            self.url = url
        if text is not None:
            self.text = text
        if transparentOcclude is not None:
            self.transparentOcclude = transparentOcclude
        if collision_listener is not None:
            self.collision_listener = collision_listener
        if animation is not None:
            self.animation = animation
        if impulse is not None:
            self.impulse = impulse
        if transparency is not None:
            self.transparency = transparency
        if parent is not None:
            self.parent = parent
        self.redraw()

    #    def __del__(self):
    #        print ("del (self) ", self.objName)
    #        self.delete()

    def delete(self):
        global debug_toggle
        if self.objName in callbacks:
            del callbacks[self.objName]
        MESSAGE = {
            "object_id": self.objName,
            "action": "delete"
        }
        # print("deleting " + json.dumps(MESSAGE))
        # print("client ", client)
        # print ("scene_path ", scene_path)
        if debug_toggle:
            print(json.dumps(MESSAGE))
        arena_publish(scene_path, MESSAGE)

    def position(self, location=(0, 0, 0)):
        global debug_toggle
        self.location = location
        MESSAGE = {
            "object_id": self.objName,
            "action": "update",
            "type": "object",
            "data": {
                "position": {
                    "x": agran(self.location[0]),
                    "y": agran(self.location[1]),
                    "z": agran(self.location[2]),
                }
            },
        }
        # print("move str: " + json.dumps(update_msg))
        if debug_toggle:
            print(json.dumps(MESSAGE))
        arena_publish(scene_path, MESSAGE)

    def redraw(self):
        global scene_path
        global debug_toggle
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
                    "x": agran(self.location[0]),
                    "y": agran(self.location[1]),
                    "z": agran(self.location[2])
                },
                "rotation": {
                    "x": agran(self.rotation[0]),
                    "y": agran(self.rotation[1]),
                    "z": agran(self.rotation[2]),
                    "w": agran(self.rotation[3])
                },
                "scale": {
                    "x": agran(self.scale[0]),
                    "y": agran(self.scale[1]),
                    "z": agran(self.scale[2])
                    },
                "color": color_str,
            },
        }
        if self.url != "":
            MESSAGE["data"]["url"] = self.url
        if self.text != None:
            MESSAGE["data"]["text"] = self.text
        if self.transparentOcclude:
            MESSAGE["data"]["material"] = {
                "colorWrite": false,
                "render-order": 0
            }
        if self.line != None:
            MESSAGE["data"]["start"] = {
                "x": agran(self.line.start[0]),
                "y": agran(self.line.start[1]),
                "z": agran(self.line.start[2])
            }
            MESSAGE["data"]["end"] = {
                "x": agran(self.line.end[0]),
                "y": agran(self.line.end[1]),
                "z": agran(self.line.end[2])
            }
            #MESSAGE["data"]["lineWidth"] = self.line.line_width
            MESSAGE["data"]["color"] = self.line.color
        if self.thickline != None:
            pathstring = ""
            for point in self.thickline.path:
                pathstring = pathstring +\
                             str(agran(point[0]))+' '+\
                             str(agran(point[1]))+' '+\
                             str(agran(point[2]))+','
            MESSAGE["data"]["path"] = pathstring.rstrip(',')
            MESSAGE["data"]["lineWidth"] = self.thickline.line_width
            MESSAGE["data"]["color"] = self.thickline.color
        if self.collision_listener != False:
            MESSAGE["data"]["collision-listener"] = ""
        if self.data != "":
            MESSAGE["data"].update(json.loads(self.data))
        if self.physics != Physics.none:
            MESSAGE["data"]["dynamic-body"] = {"type": self.physics.value}
        if self.clickable:
            MESSAGE["data"]["click-listener"] = ""
        if self.ttl != 0:
            MESSAGE["ttl"] = self.ttl
        if self.animation != None:
            MESSAGE["data"]["animation-mixer"] = {
                "clip": self.animation.clip,
                "loop": self.animation.loop,
                "repetitions": self.animation.repetitions,
                "timeScale": self.animation.timeScale
            }
        if self.transparency != None:
            MESSAGE["data"]["material"] = {
                "transparent": self.transparency.transparent,
                "opacity": self.transparency.opacity
            }
        if self.impulse != None:
            MESSAGE["data"]["impulse"] = {
                "on": self.impulse.on,
                "force": tuple_to_string(self.impulse.force),
                "position": tuple_to_string(self.impulse.position)
            }
        if self.parent != "":
            MESSAGE["data"]["parent"] = self.parent

        # print("publishing " + json.dumps(MESSAGE) + " to " + scene_path)
        if debug_toggle:
            print(json.dumps(MESSAGE))
        arena_publish(scene_path, MESSAGE)


def __init__(self, name):
    """Initializes the data."""
    self.name = name
    print("(Initializing {})".format(self.name))
