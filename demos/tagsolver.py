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

with open("config.json") as config_file:
    CONFIG = json.load(config_file)

CLIENT_ID = "apriltag_solver_" + str(random.randint(0, 100))

HOST = CONFIG["host"]
PORT = CONFIG["port"]
TOPIC = CONFIG["default_realm"] + "/g/a/"
TAG_URLBASE = "https://atlas.conix.io/record"
DEBUG = True


def log(*s):
    if DEBUG:
        print(*s)


# fmt: off

ORIGINTAG = [
    [1, 0, 0, 0],
    [0, 0, 1, 0],
    [0, -1, 0, 0],
    [0, 0, 0, 1]
]

FLIP = [[1, 0, 0, 0],
        [0, -1, 0, 0],
        [0, 0, -1, 0],
        [0, 0, 0, 1]]

# fmt: on

VIO_STATE = {}
VIO_MAX_DIFF_LOW = 0.05  # set diff to a more strict threshold
VIO_MAX_DIFF_HIGH = 0.2  # set diff to a less strict threshold


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


def resolve_pose_ambiguity(pose1, err1, pose2, err2, vio):
    vertical_vector = np.array([[0, 1, 0]]).T
    pose1_vertical = pose1[0:3, 0:3] @ vertical_vector
    pose2_vertical = pose2[0:3, 0:3] @ vertical_vector
    vio_vertical = vio[0:3, 0:3].T @ vertical_vector
    pose1_vertical = pose1_vertical / np.linalg.norm(pose1_vertical)
    pose2_vertical = pose2_vertical / np.linalg.norm(pose2_vertical)
    vio_vertical = vio_vertical / np.linalg.norm(vio_vertical)
    verr1 = 1.0 - abs(np.dot(pose1_vertical.T, vio_vertical))
    verr2 = 1.0 - abs(np.dot(pose2_vertical.T, vio_vertical))
    if verr1 <= verr2 and err1 <= err2:
        return pose1, err1
    if verr2 <= verr1 and err2 <= err1:
        return pose2, err2
    if verr1 <= verr2:
        return pose1, 99999999.9
    return pose2, 99999999.9


# test_pose1 = np.array(
#     [[.72, -.01, -.69, -.06],
#      [-.05, 1.00, -.06, -.03],
#      [.69, .07, .72, -1.15],
#      [.00, .00, .00, 1.00]])
# test_error1 = 1e-6
# test_pose2 = np.array(
#     [[.65, -.02, .76, -.05],
#      [-.09, .99, .10, -.03],
#      [-.75, -.13, .65, -1.14],
#      [.00, .00, .00, 1.00]])
# test_error2 = 181e-6
# test_vio = np.identity(4)
# test_pose, test_error = resolve_pose_ambiguity(
#     test_pose1, test_error1, test_pose2, test_error2, test_vio)
# print(test_pose)
# print(test_error)
# sys.exit()


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
    pos = json_msg.vio.position
    rot = json_msg.vio.rotation

    # Construct pose matrix4 for camera
    vio_pose = np.identity(4)
    vio_pose[0:3, 0:3] = Rotation.from_quat(
        [rot._x, rot._y, rot._z, rot._w]).as_matrix()
    vio_pose[0:3, 3] = [pos.x, pos.y, pos.z]

    # Construct pose matrix for detected tag solution 1
    dtag_pose_s1 = np.identity(4)
    # Correct for column-major format of detected tag pose
    R_correct = np.array(detected_tag.pose.R).T
    dtag_pose_s1[0:3, 0:3] = R_correct
    dtag_pose_s1[0:3, 3] = detected_tag.pose.t
    # Swap x/y axis of detected tag coordinate system
    dtag_pose_s1 = np.array(FLIP) @ dtag_pose_s1 @ np.array(FLIP)
    dtag_error_s1 = detected_tag.pose.e

    # Construct pose matrix for detected tag solution 2
    dtag_pose_s2 = np.identity(4)
    # Correct for column-major format of detected tag pose
    R_correct = np.array(detected_tag.pose.asol.R).T
    dtag_pose_s2[0:3, 0:3] = R_correct
    dtag_pose_s2[0:3, 3] = detected_tag.pose.asol.t
    # Swap axes of detected tag to our coordinate system
    dtag_pose_s2 = np.array(FLIP) @ dtag_pose_s2 @ np.array(FLIP)
    dtag_error_s2 = detected_tag.pose.asol.e

    # Require camera to be stationary
    if not vio_filter(vio_pose, client_id, VIO_MAX_DIFF_HIGH):
        return

    # Get pose of tag in arena coords
    if detected_tag.id == 0:
        ref_tag_pose = ORIGINTAG
    elif hasattr(detected_tag, "refTag"):
        # comes in as col-major
        arr = detected_tag.refTag.pose.elements
        ref_tag_pose = np.array(
            [arr[0:4], arr[4:8], arr[8:12], arr[12:16]]
        ).T
    else:
        # Tag not found. TODO: query ATLAS for it
        log("Tag not found, not in build mode")
        return

    # Fix detection ambiguity using gravity from vio
    dtag_pose, dtag_error = resolve_pose_ambiguity(
        dtag_pose_s1, dtag_error_s1, dtag_pose_s2, dtag_error_s2, vio_pose)
    if dtag_error > 5e-6:
        log("Too tag much error")
        return

    mqtt_response = None
    log("Localizing", client_id, "on", str(detected_tag.id))

    rig_pose = ref_tag_pose @ np.linalg.inv(
        dtag_pose) @ np.linalg.inv(vio_pose)
    rig_pos = rig_pose[0:3, 3]
    rig_rotq = Rotation.from_matrix(rig_pose[0:3, 0:3]).as_quat()

    # fmt: off
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
    # fmt: on

    if mqtt_response is not None:
        client.publish("realm/s/" + scene, json.dumps(mqtt_response))


def start_mqtt():
    mttqc = mqtt.Client(CLIENT_ID, clean_session=True, userdata=None)
    mttqc.connect(HOST, PORT)
    print("Connected MQTT")
    mttqc.subscribe(TOPIC + "#")
    mttqc.message_callback_add(TOPIC + "#", on_tag_detect)
    mttqc.loop_forever()


start_mqtt()
