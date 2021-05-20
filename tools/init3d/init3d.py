""" init3d.py
3d program manager: Subscribes to runtime channels to 3d-control modules present in the scene.
- service "service name" start/stop/status/restart
"""
import json
import os
import pprint
import re

from arena import Material, Position, Scene, Sphere

from arts.artsrequests import Action, ARTSRESTRequest, FileType
from arts.module import Module

CFG_FILE = 'config.json'
PRG_FILE = 'programs.json'
HOST = None
REALM = "realm"
NAMESPACE = None
SCENE = None
TOPIC_ALL = None
config = None
programs = None
keywords = ["moduleid", "namespace", "scene", "mqtth", "realm"]
click_obj = None
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


def module_test(scene: Scene):
    global config, programs, click_obj

    click_obj = Sphere(
        object_id="click_obj",
        position=Position(0, 1, -1),
        scale={"x": 0.1, "y": 0.1, "z": 0.1},
        color=CLR_RED,
        material=Material(color=CLR_RED),
        clickable=True,
        evt_handler=click_handler,
    )
    scene.add_object(click_obj)

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

    # query for modules of a particular runtime, given its uuid:
    #  modulesJson = artsRest.getRuntimes('a69e075c-51e5-4555-999c-c49eb283dc1d')
    #
    # we can also query arts for runtimes:
    #  runtimesJson = artsRest.getRuntimes()


def click_handler(scene, evt, msg):
    global mod, click_obj

    if evt.type == "mousedown":
        if mod:
            # kill the module
            deleteModule(mod, scene)
            mod = None
            click_obj.update_attributes(
                color=CLR_RED,
                material=Material(color=CLR_RED))
        else:
            # create a module object
            mod = createModule(scene)
            click_obj.update_attributes(
                color=CLR_GRN,
                material=Material(color=CLR_GRN))


def createModule(scene):
    global HOST, REALM, NAMESPACE, SCENE, config

    # create environment variables to be passed as a *space-separated* string
    #env = re.sub(r'${scene}', SCENE, env)
    #env = f"NAMESPACE={NAMESPACE} SCENE={SCENE} MQTTH={HOST} REALM={REALM}"
    env = f"['NAMESPACE={NAMESPACE}','SCENE={SCENE}','MQTTH={HOST}','REALM={REALM}']"

    # create a module object
    mod = Module("arena/py/moving-box", "box.py", mod_env=env)

    # mod = Module("wiselab/boxes", "box.py", mod_uuid='4264bac8-13ed-453b-b157-49cc2421a112')

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
