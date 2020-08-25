import json
import paho.mqtt.client as mqtt
import pose
import random
from types import SimpleNamespace


with open("config.json") as config_file:
    CONFIG = json.load(config_file)
CLIENT_ID = "apriltag_solver_" + str(random.randint(0, 100))
HOST = CONFIG["host"]
PORT = CONFIG["port"]
TOPIC = CONFIG["default_realm"] + "/g/a/"
DTAG_ERROR_THRESH = 5e-6
MOVE_THRESH = .05   # 5cm
ROT_THRESH = .087   # 5deg
DEBUG = True

vio_state = {}


def log(*s):
    if DEBUG:
        print(*s)


def dict_to_sns(d):
    return SimpleNamespace(**d)


def vio_filter(vio, client_id):
    global vio_state
    vio_pose_last = vio_state.get(client_id)
    if vio_pose_last is None:
        vio_state[client_id] = vio
        return False
    pos_diff, rot_diff = pose.pose_diff(vio, vio_pose_last)
    vio_state[client_id] = vio
    if pos_diff > MOVE_THRESH or rot_diff > ROT_THRESH:
        return False
    return True


def on_tag_detect(client, userdata, msg):
    json_msg = json.loads(msg.payload.decode("utf-8"), object_hook=dict_to_sns)
    client_id = msg.topic.split("/")[-1]
    dtag = json_msg.detections[0]
    if not hasattr(dtag, 'refTag'):
        print('tag not in atlas: ' + dtag.id)
        return
    vio_pose = pose.get_vio_pose(json_msg)
    if not vio_filter(vio_pose, client_id):
        log('too much movement')
        return
    rig_pose, dtag_error = pose.get_rig_pose(json_msg)
    if dtag_error > 5e-6:
        log("too much detection error")
        return
    rig_pos, rig_rotq = pose.matrix4_to_pose(rig_pose)
    log("Localizing", client_id, "on", str(dtag.id))
    mqtt_response = {
        'object_id': client_id,
        'action': 'update',
        'type': 'rig',
        'data': {
            'position': {
                'x': rig_pos[0],
                'y': rig_pos[1],
                'z': rig_pos[2]
            },
            'rotation': {
                'x': rig_rotq[0],
                'y': rig_rotq[1],
                'z': rig_rotq[2],
                'w': rig_rotq[3]
            }
        }
    }
    client.publish("realm/s/" + json_msg.scene, json.dumps(mqtt_response))


def start_mqtt():
    mqttc = mqtt.Client(CLIENT_ID, clean_session=True, userdata=None)
    mqttc.connect(HOST, PORT)
    print("Connected MQTT")
    mqttc.subscribe(TOPIC + "#")
    mqttc.message_callback_add(TOPIC + "#", on_tag_detect)
    mqttc.loop_forever()


start_mqtt()
