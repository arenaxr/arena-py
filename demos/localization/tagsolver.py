import json
import random
from types import SimpleNamespace
import numpy as np
import paho.mqtt.client as mqtt
import pose


with open("config.json") as config_file:
    CONFIG = json.load(config_file)
CLIENT_ID = "apriltag_solver_" + str(random.randint(0, 100))
HOST = CONFIG["host"]
PORT = CONFIG["port"]
TOPIC = CONFIG["default_realm"] + "/g/a/"
TAG_URLBASE = "https://atlas.conix.io/record"
DEBUG = True

VIO_STATE = {}
VIO_MAX_DIFF_LOW = 0.05  # set diff to a more strict threshold
VIO_MAX_DIFF_HIGH = 0.2  # set diff to a less strict threshold
DTAG_ERROR_THRESH = 5e-6


def log(*s):
    if DEBUG:
        print(*s)


def dict_to_sns(d):
    return SimpleNamespace(**d)


def vio_filter(vio, client_id, vio_threshold):
    global VIO_STATE
    # Add some extremely simple filtering based on camera motion
    # make sure we get two readings with minimal vio movement
    vio_pose_last = VIO_STATE.get(client_id)
    if vio_pose_last is None:
        log("skip, no previous camera location")
        VIO_STATE[client_id] = vio
        return False
    else:
        # Directly subtract the current and previous pose matrix
        vio_pose_delta = np.subtract(vio, vio_pose_last)
        # take absolute value of matrix elements and find max change value
        vio_pose_delta = abs(vio_pose_delta)
        vio_max_diff = vio_pose_delta.max()
    # save state of last vio position for this camera
    VIO_STATE[client_id] = vio
    # Just guessed the threshold for motion
    if abs(vio_max_diff) > vio_threshold:
        log("Too much camera movement")
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
    if not vio_filter(vio_pose, client_id, VIO_MAX_DIFF_HIGH):
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
