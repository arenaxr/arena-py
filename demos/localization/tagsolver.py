import sys
import json
import random
import uuid
from types import SimpleNamespace

import requests
from requests.auth import HTTPBasicAuth

import numpy as np
import paho.mqtt.client as mqtt
from scipy.spatial.transform import Rotation

from pose import resolve_pose_ambiguity


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


def msg_to_pose(msg_pose):
    FLIP = np.diag([1, -1, -1, 1])
    dtag_pose = np.identity(4)
    # Correct for column-major format of detected tag pose
    R_correct = np.array(msg_pose.R).T
    dtag_pose[0:3, 0:3] = R_correct
    dtag_pose[0:3, 3] = msg_pose.t
    # Swap x/y axis of detected tag coordinate system
    dtag_pose = FLIP @ dtag_pose @ FLIP
    dtag_error = msg_pose.e
    return dtag_pose, dtag_error


def on_tag_detect(client, userdata, msg):
    json_msg = None
    try:
        json_msg = json.loads(msg.payload.decode(
            "utf-8"), object_hook=dict_to_sns)
    except ValueError:
        pass
    client_id = msg.topic.split("/")[-1]
    scene = json_msg.scene
    if not hasattr(json_msg, "vio"):
        return

    builder = hasattr(json_msg, "builder") and json_msg.builder
    if builder:
        return

    # Only take first marker for now, later iterate and avg all markers
    detected_tag = json_msg.detections[0]

    # Construct pose matrix4 for camera from vio
    pos = json_msg.vio.position
    rot = json_msg.vio.rotation
    vio_pose = np.identity(4)
    vio_pose[0:3, 0:3] = Rotation.from_quat(
        [rot._x, rot._y, rot._z, rot._w]).as_matrix()
    vio_pose[0:3, 3] = [pos.x, pos.y, pos.z]

    # Require camera to be stationary
    if not vio_filter(vio_pose, client_id, VIO_MAX_DIFF_HIGH):
        return

    # Construct pose matrix for detected tag solutions 1 and 2
    dtag_pose1, dtag_error1 = msg_to_pose(detected_tag.pose)
    dtag_pose2, dtag_error2 = msg_to_pose(detected_tag.pose.asol)

    # Determine arena pose of the tag
    if hasattr(detected_tag, "refTag"):
        # comes in as col-major
        arr = detected_tag.refTag.pose.elements
        ref_tag_pose = np.array(
            [arr[0:4], arr[4:8], arr[8:12], arr[12:16]]).T
    else:
        # Tag not found. TODO: query ATLAS for it
        log("Tag not found, not in build mode")
        return

    # Fix detection ambiguity using gravity from vio
    dtag_pose, dtag_error = resolve_pose_ambiguity(
        dtag_pose_s1, dtag_error_s1, dtag_pose_s2, dtag_error_s2, vio_pose, ref_tag_pose)
    if dtag_error > 5e-6:
        log("Too tag much error")
        return

    # Localize and publish result
    log("Localizing", client_id, "on", str(detected_tag.id))
    rig_pose = ref_tag_pose @ np.linalg.inv(
        dtag_pose) @ np.linalg.inv(vio_pose)
    rig_pos = rig_pose[0:3, 3]
    rig_rotq = Rotation.from_matrix(rig_pose[0:3, 0:3]).as_quat()
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
    client.publish("realm/s/" + scene, json.dumps(mqtt_response))


def start_mqtt():
    mttqc = mqtt.Client(CLIENT_ID, clean_session=True, userdata=None)
    mttqc.connect(HOST, PORT)
    print("Connected MQTT")
    mttqc.subscribe(TOPIC + "#")
    mttqc.message_callback_add(TOPIC + "#", on_tag_detect)
    mttqc.loop_forever()


start_mqtt()
