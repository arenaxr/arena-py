# init3d.py
#
# 3d program manager: Subscribes to runtime channels to 3d-control programs present in the scene.
import argparse
import json
import pprint

from arena import Scene

from arts.artsrequests import Action, ARTSRESTRequest, FileType
from arts.module import Module

CFG_FILE = 'config.json'
HOST = None
REALM = "realm"
NAMESPACE = None
SCENE = None
TOPIC_ALL = None
settings = None


def init_args():
    global HOST, REALM, NAMESPACE, SCENE, TOPIC_ALL, settings

    parser = argparse.ArgumentParser(
        description="ARENA init3d manager example.")
    parser.add_argument('-b', dest='host', default=None,
                        help='Hostname/broker for Init3d')
    parser.add_argument('-r', dest='realm', default=None,
                        help='Realm for Init3d')
    parser.add_argument('-n', dest='namespace', default=None,
                        help='Namespace for Init3d')
    parser.add_argument('-s', dest='scenename', default=None,
                        help='Scenename for Init3d (e.g. theme1, theme2)')
    args = parser.parse_args()
    print(args)

    if args.host is not None:
        HOST = args.host
    if args.realm is not None:
        REALM = args.realm
    if args.namespace is not None:
        NAMESPACE = args.namespace
    if args.scenename is not None:
        SCENE = args.scenename

    settings = Settings(CFG_FILE)
    TOPIC_ALL = f"{REALM}/proc/#"


def runtime_callback(client, userdata, msg):
    try:
        payload_str = msg.payload.decode("utf-8", "ignore")
        payload = json.loads(payload_str)
        print(payload)
    except:
        pass


class Settings(dict):

    def __init__(self, cfg_file):
        with open(CFG_FILE) as json_data_file:
            s_dict = json.load(json_data_file)

        dict.__init__(self, s_dict)


def module_test(scene: Scene):
    global HOST, REALM, NAMESPACE, SCENE
    # json pretty printer
    pp = pprint.PrettyPrinter(indent=4)

    # create ARTSRESTRequest object to query arts
    artsRest = ARTSRESTRequest(f"{HOST}/{settings['arts']['rest_url']}")

    # create environment variables to be passed as a *space-separated* string
    env = f"NAMESPACE={NAMESPACE} SCENE={SCENE} MQTTH={HOST} REALM={REALM}"

    # create a module object
    # the minimal arguments to create a module are name and filename (env is optional)
    # these are all the arguments that can be passed and their defaults:
    #    mod_name, mod_filename, mod_uuid=uuid.uuid4(), parent_rt=None, mod_ft=FileType.PY, mod_args='', mod_env=''
    #    Note: filetype will be inferred from filename extension (.py or .wasm)
    mod = Module("wiselab/boxes", "boxes.py", mod_env=env)

    # we can create a module object to a running module (for example, to send a delete request), if we know its uuid:
    # mod = Module("wiselab/boxes", "boxes.py", mod_uuid='4264bac8-13ed-453b-b157-49cc2421a112')

    # get arts request json string (req_uuid will be used to confirm the request)
    req_uuid, artsModCreateReq = mod.artsReqJson(Action.create)
    print(artsModCreateReq)

    # publish request
    #publish.single(f"{REALM}/{settings['arts']['ctl']}", artsModCreateReq, hostname=HOST)
    scene.mqttc.publish(
        f"{REALM}/{settings['arts']['ctl']}", artsModCreateReq)

    # TODO: we can check for arts confirmation:
    #  1. subscribe to reg topic (settings['arts']['ctl'])
    #  2. look for message of type "arts_resp", with the object_id set to the value of req_uuid we saved before

    # we can use arts rest interface to query existing modules
    modulesJson = artsRest.getModules()
    print('** These are all the modules known to ARTS:')
    pp.pprint(modulesJson)

    # query for modules of a particular runtime, given its uuid:
    #  modulesJson = artsRest.getRuntimes('a69e075c-51e5-4555-999c-c49eb283dc1d')
    #
    # we can also query arts for runtimes:
    #  runtimesJson = artsRest.getRuntimes()

    # wait for user
    input("Press Enter to kill the module...")

    # kill the module
    req_uuid, artsModDeleteReq = mod.artsReqJson(Action.delete)
    print(artsModDeleteReq)
    #publish.single(f"{REALM}/{settings['arts']['ctl']}", artsModDeleteReq, hostname=HOST)
    scene.mqttc.publish(
        f"{REALM}/{settings['arts']['ctl']}", artsModDeleteReq)


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
