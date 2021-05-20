""" init3d.py
3d program manager: Subscribes to runtime channels to 3d-control modules present in the scene.
- service "service name" start/stop/status/restart
"""
import json
import os
import pprint
import re

from arts.artsrequests import Action, ARTSRESTRequest, FileType
from arts.module import Module

from arena import *

CFG_FILE = 'config.json'
PRG_FILE = 'programs.json'
HOST = None
REALM = "realm"
NAMESPACE = None
SCENE = None
TOPIC_ALL = None
config = {}
programs = []
start_obj = None
stop_obj = None
mod = None
CLR_RED = (255, 0, 0)
CLR_GRN = (0, 255, 0)


def init_args():
    global HOST, REALM, NAMESPACE, SCENE, TOPIC_ALL, config, programs
    if os.getenv("MQTTH") is not None:
        HOST = os.getenv("MQTTH")
    if os.getenv("REALM") is not None:
        REALM = os.getenv("REALM")
    if os.getenv("NAMESPACE") is not None:
        NAMESPACE = os.getenv("NAMESPACE")
    if os.getenv("SCENE") is not None:
        SCENE = os.getenv("SCENE")

    config = load_json_file(CFG_FILE)
    print(config)
    programs = load_json_file(PRG_FILE)
    print(programs)
    TOPIC_ALL = f"{REALM}/proc/#"


def runtime_callback(client, userdata, msg):
    try:
        payload_str = msg.payload.decode("utf-8", "ignore")
        payload = json.loads(payload_str)
        print(payload)
    except:
        pass


def load_json_file(cfg_file):
    with open(cfg_file) as json_data_file:
        s_dict = json.load(json_data_file)
    return s_dict


def process_keywords(str):
    global HOST, REALM, NAMESPACE, SCENE, keywords
    str = re.sub(r'\${mqtth}', HOST, str)
    str = re.sub(r'\${realm}', REALM, str)
    str = re.sub(r'\${namespace}', NAMESPACE, str)
    str = re.sub(r'\${scene}', SCENE, str)
    return str


def module_test(scene: Scene):
    global config, programs, start_obj, stop_obj

    # one time process keyword substitution
    for pidx, prog in enumerate(programs):
        programs[pidx]['env'] = process_keywords(prog['env'])
        programs[pidx]['args'] = process_keywords(prog['args'])
        programs[pidx]['ch'] = process_keywords(prog['ch'])

    # render module controllers
    for pidx, prog in enumerate(programs):
        # process_objects(scene, 0, "arena/py/moving-box",
        #                 "box.py", ["012345", "a69e07"])
        process_objects(scene, pidx, prog, [])

    # query for modules of a particular runtime, given its uuid:
    #  modulesJson = artsRest.getRuntimes('a69e075c-51e5-4555-999c-c49eb283dc1d')
    #
    # we can also query arts for runtimes:
    #  runtimesJson = artsRest.getRuntimes()

    # TODO: we can check for arts confirmation:
    #  1. subscribe to reg topic (config['arts']['ctl'])
    #  2. look for message of type "arts_resp", with the object_id set to the value of req_uuid we saved before

    # create ARTSRESTRequest object to query arts
    artsRest = ARTSRESTRequest(f"{HOST}/{config['arts']['rest_url']}")
    # we can use arts rest interface to query existing modules
    modulesJson = artsRest.getModules()
    print('** These are all the modules known to ARTS:')
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(modulesJson)


def process_objects(scene, pidx, prog, modules):
    name = prog['name']
    file = prog['file']
    y = 1 + (0.1*(pidx+1)) + (0.01*(pidx+1))
    regex = r"[!#$&'()*+,\/:;=?@[\]]"
    tag = f"{re.sub(regex, '_', name)}_{re.sub(regex, '_', file)}"

    # start the module
    start_obj = Cone(
        object_id=f"start_obj_{tag}",
        position=Position(0, y, -1),
        scale={"x": 0.05, "y": 0.1, "z": 0.01},
        rotation={"x": 0, "y": 0, "z": -90},
        color=CLR_RED,
        material=Material(color=CLR_RED, transparent=True,
                          opacity=0.4, shading="flat"),
        clickable=True,
        evt_handler=start_handler,
    )
    start_txt = Text(
        object_id=f"start_txt_{tag}",
        parent=start_obj.object_id,
        text=file,
        align="left",
        anchor="left",
        xOffset=-0.5,
        rotation={"x": 0, "y": 0, "z": 90},
        scale={"x": 1, "y": 2, "z": 10},
    )
    # module name
    name_txt = Text(
        object_id=f"name_txt_{tag}",
        text=name,
        position=Position(0.15, y, -1),
        align="left",
        anchor="left",
        xOffset=-0.5,
        scale={"x": 0.1, "y": 0.1, "z": 0.1},
    )
    scene.add_object(start_obj)
    scene.add_object(start_txt)
    scene.add_object(name_txt)

    for midx, val in enumerate(modules):
        # stop running module
        x = (-0.1*(midx+1)) - (0.01*(midx+1))
        stop_obj = Box(
            object_id=f"stop_obj{midx}_{tag}",
            position=Position(x, y, -1),
            scale={"x": 0.1, "y": 0.1, "z": 0.01},
            rotation={"x": 0, "y": 0, "z": -90},
            color=CLR_RED,
            material=Material(color=CLR_RED, transparent=True,
                              opacity=0.4, shading="flat"),
            clickable=True,
            evt_handler=stop_handler,
        )
        stop_txt = Text(
            object_id=f"stop_txt{midx}_{tag}",
            parent=stop_obj.object_id,
            text=val,
            rotation={"x": 0, "y": 0, "z": 90},
            scale={"x": 1, "y": 1, "z": 10},
        )
        scene.add_object(stop_obj)
        scene.add_object(stop_txt)


def start_handler(scene, evt, msg):
    global mod, start_obj

    if evt.type == "mousedown":
        if mod:
            # kill the module
            deleteModule(mod, scene)
            mod = None
        else:
            env = f"['NAMESPACE={NAMESPACE}','SCENE={SCENE}','MQTTH={HOST}','REALM={REALM}']"
            mod = createModule(scene, "arena/py/moving-box", "box.py", env, "")


def stop_handler(scene, evt, msg):
    global mod, stop_obj
    # TODO: add stop handler


def createModule(scene, name, file, env, args):
    global config

    # create environment variables to be passed as a string
    # env = f"['NAMESPACE={NAMESPACE}','SCENE={SCENE}','MQTTH={HOST}','REALM={REALM}']"

    # create a module object
    # mod = Module("arena/py/moving-box", "box.py", mod_env=env)
    # mod = Module("wiselab/boxes", "box.py", mod_uuid='4264bac8-13ed-453b-b157-49cc2421a112')
    mod = Module(name, file, mod_env=env, mod_args=args)

    # get arts request json string (req_uuid will be used to confirm the request)
    req_uuid, artsModCreateReq = mod.artsReqJson(Action.create)
    print(artsModCreateReq)

    # publish request
    scene.mqttc.publish(
        f"{REALM}/{config['arts']['ctl']}", artsModCreateReq)
    return mod


def deleteModule(mod, scene):
    global config
    # kill the module
    req_uuid, artsModDeleteReq = mod.artsReqJson(Action.delete)
    print(artsModDeleteReq)
    scene.mqttc.publish(
        f"{REALM}/{config['arts']['ctl']}", artsModDeleteReq)


# setup and launch
init_args()
kwargs = {}
if NAMESPACE:
    kwargs["namespace"] = NAMESPACE
scene = Scene(
    host=HOST,
    realm=REALM,
    scene=SCENE,
    **kwargs)
scene.message_callback_add(TOPIC_ALL, runtime_callback)
scene.run_after_interval(module_test(scene), 1000)
scene.run_tasks()
