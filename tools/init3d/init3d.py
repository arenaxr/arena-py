""" init3d.py
3d program manager: Subscribes to runtime channels to 3d-control modules present in the scene.
- service "service name" start/stop/status/restart
"""
import json
import os
import re
import uuid

from arena import *

from artsrequests import Action, ARTSRESTRequest, FileType
from module import Module

CFG_FILE = 'config.json'
PRG_FILE = 'programs.json'
HOST = "mqtt.arenaxr.org"
REALM = "realm"
NAMESPACE = None
SCENE = None
TOPIC_ALL = None
config = {}
programs = []
CLR_RED = (255, 0, 0)
CLR_GRN = (0, 255, 0)
init3d_root = None


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
    # TODO: we can check for arts confirmation:
    #  1. subscribe to reg topic (config['arts']['ctl'])
    #  2. look for message of type "arts_resp", with the object_id set to the value of req_uuid we saved before
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
    global HOST, REALM, NAMESPACE, SCENE
    str = re.sub(r'\${mqtth}', HOST, str)
    str = re.sub(r'\${realm}', REALM, str)
    str = re.sub(r'\${namespace}', NAMESPACE, str)
    str = re.sub(r'\${scene}', SCENE, str)
    return str


def startup_state(scene: Scene):
    global programs
    # one time process keyword substitution
    for pidx, prog in enumerate(programs):
        programs[pidx]['env'] = process_keywords(prog['env'])
        programs[pidx]['args'] = process_keywords(prog['args'])
        programs[pidx]['ch'] = process_keywords(prog['ch'])

    # create ARTSRESTRequest object to query arts
    queryRunningModules()
    # render module controllers
    populateControls(scene)


def queryRunningModules():
    global config, programs
    # create ARTSRESTRequest object to query arts
    artsRest = ARTSRESTRequest(f"{HOST}/{config['arts']['rest_url']}")
    # query existing modules
    new_programs = []
    modulesJson = artsRest.getModules()
    for mod in modulesJson:
        # add current modules to list, for this scene
        if restModuleInScene(mod):
            known = False
            for pidx, prog in enumerate(programs):
                # add unknown module instances
                if 'modules' not in prog:
                    programs[pidx]['modules'] = []
                if prog['name'] == mod['name'] and prog['file'] == mod['filename']:
                    known = True
                    if mod['uuid'] not in prog['modules']:
                        programs[pidx]['modules'].append(mod['uuid'])
                # add unknown module instances
                if not known:
                    module = {"name": mod['name'],
                              "file": mod['filename'],
                              "modules": [mod['uuid']]}
                    if 'env' in mod:
                        module['env'] = mod['env']
                    if 'args' in mod:
                        module['args'] = mod['args']
                    if 'ch' in mod:
                        module['ch'] = mod['ch']
                    new_programs.append(module)

    # TODO: add found programs
    print(new_programs)


def restModuleInScene(mod):
    global SCENE, NAMESPACE
    matchS = False
    matchNS = False
    if f'SCENE={SCENE}' in mod['env']:
        matchS = True
    if f'NAMESPACE=' in mod['env']:
        if f'NAMESPACE={NAMESPACE}' in mod['env']:
            matchNS = True
    else:
        if NAMESPACE == 'public':
            matchNS = True
    return (matchS and matchNS)


def populateControls(scene):
    global config, programs, init3d_root
    # render module controllers
    parent_id = "init3d_root"
    init3d_root = Box(
        object_id=parent_id,
        position=Position(0, 0, 0),
        scale={"x": 1, "y": 1, "z": 1},
        material=Material(transparent=True, opacity=0),
    )
    scene.delete_object(init3d_root)  # clear root
    scene.add_object(init3d_root)
    for pidx, prog in enumerate(programs):
        mods = []
        if 'modules' in prog:
            mods = prog['modules']
        process_objects(scene, parent_id, pidx, prog, mods)


def process_objects(scene, parent_id, pidx, prog, modules):
    name = prog['name']
    file = prog['file']
    y = 1 + (0.1*(pidx+1)) + (0.01*(pidx+1))
    regex = r"[!#$&'()*+,\/:;=?@[\]]"
    tag = f"{re.sub(regex, '_', name)}_{re.sub(regex, '_', file)}"

    # start the module
    start_obj = Cone(
        object_id=f"start_{pidx}_{tag}",
        parent=parent_id,
        position=Position(0, y, -1),
        scale={"x": 0.05, "y": 0.1, "z": 0.01},
        rotation={"x": 0, "y": 0, "z": -90},
        color=CLR_RED,
        material=Material(color=CLR_GRN, transparent=True,
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
        parent=parent_id,
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
            object_id=f"stop_{pidx}_{val}",
            parent=parent_id,
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
            object_id=f"stop_txt_{pidx}_{val}",
            parent=stop_obj.object_id,
            text=val[0:6],
            rotation={"x": 0, "y": 0, "z": 90},
            scale={"x": 1, "y": 1, "z": 10},
        )
        scene.add_object(stop_obj)
        scene.add_object(stop_txt)


def start_handler(scene, event, msg):
    obj = event.object_id.split("_")
    if event.type == "mousedown":
        pidx = int(obj[1])
        mod = createModule(scene, pidx)
        if 'modules' not in programs[pidx]:
            programs[pidx]['modules'] = []
        programs[pidx]['modules'].append(mod.uuid)
        populateControls(scene)


def stop_handler(scene, event, msg):
    # kill the module
    obj = event.object_id.split("_")
    if event.type == "mousedown":
        pidx = int(obj[1])
        uuid = obj[2]
        deleteModule(scene, programs[pidx], uuid)
        if 'modules' not in programs[pidx]:
            programs[pidx]['modules'] = []
        programs[pidx]['modules'].remove(uuid)
        populateControls(scene)


def createModule(scene, pidx):
    global config
    # create a module object
    name = programs[pidx]['name']
    file = programs[pidx]['file']
    env = programs[pidx]['env']
    args = programs[pidx]['args']
    # mod = Module("arena/py/moving-box", "box.py", mod_uuid=uuid.uuid4(), mod_env=env)
    # mod = Module("arena/py/moving-box", "box.py", mod_uuid='4264bac8-13ed-453b-b157-49cc2421a112')
    mod = Module(name, file, uuid.uuid4(), mod_env=env, mod_args=args)
    print(mod.uuid)
    # get arts request json string (req_uuid will be used to confirm the request)
    req_uuid, artsModCreateReq = mod.artsReqJson(Action.create)
    scene.mqttc.publish(
        f"{REALM}/{config['arts']['ctl']}", artsModCreateReq)
    return mod


def deleteModule(scene, prog, uuid):
    global config
    # kill the module
    mod = Module(prog['name'], prog['file'], mod_uuid=uuid)
    req_uuid, artsModDeleteReq = mod.artsReqJson(Action.delete)
    scene.mqttc.publish(
        f"{REALM}/{config['arts']['ctl']}", artsModDeleteReq)


def user_join_callback(scene, event, msg):
    populateControls(scene)


def end_program_callback(scene, event, msg):
    global init3d_root
    scene.delete_object(init3d_root)  # clear root


# setup and launch
init_args()
kwargs = {}
if NAMESPACE:
    kwargs["namespace"] = NAMESPACE
scene = Scene(
    host=HOST,
    realm=REALM,
    scene=SCENE,
    user_join_callback=user_join_callback,
    end_program_callback=end_program_callback,
    **kwargs)
NAMESPACE = scene.namespace  # update actual
scene.message_callback_add(TOPIC_ALL, runtime_callback)
scene.run_after_interval(startup_state(scene), 1000)
scene.run_tasks()
