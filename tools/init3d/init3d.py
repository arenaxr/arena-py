# init3d.py
#
# 3d program manager: Subscribes to runtime channels to 3d-control programs present int the scene.
import argparse

from arena import *

HOST = None
REALM = None
NAMESPACE = None
SCENE = None
RUNTIME_TOPIC= None


def init_args():
    global HOST, REALM, NAMESPACE, SCENE, RUNTIME_TOPIC

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
    RUNTIME_TOPIC = f"{REALM}/proc"


def runtime_callback(client, userdata, msg):
    try:
        payload_str = msg.payload.decode("utf-8", "ignore")
        payload = json.loads(payload_str)
        print(payload)
    except:
        pass


init_args()
kwargs = {}
if NAMESPACE:
    kwargs["namespace"] = NAMESPACE
scene = Scene(
    host=HOST,
    realm=REALM,
    scene=SCENE,
    **kwargs)
scene.message_callback_add(RUNTIME_TOPIC, runtime_callback)
scene.run_tasks()
