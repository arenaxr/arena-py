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

RIGS = {}
VIO_STATE = {}
FRAME_COUNTER = {}
ADDED_TAGS = {}

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
    print(pose1_vertical)
    print(pose2_vertical)
    print(vio_vertical)
    return pose1, err1


test_pose1 = np.array(
    [[.72, -.01, -.69, -.06],
     [-.05, 1.00, -.06, -.03],
     [.69, .07, .72, -1.15],
     [.00, .00, .00, 1.00]])
test_error1 = 1e-6
test_pose2 = np.array(
    [[.65, -.02, .76, -.05],
     [-.09, .99, .10, -.03],
     [-.75, -.13, .65, -1.14],
     [.00, .00, .00, 1.00]])
test_error2 = 181e-6
test_vio = np.identity(4)
test_pose, test_error = resolve_pose_ambiguity(
    test_pose1, test_error1, test_pose2, test_error2, test_vio)
print(test_pose)
print(test_error)
sys.exit()


def on_tag_detect(client, userdata, msg):
    json_msg = None
    try:
        json_msg = json.loads(msg.payload.decode(
            "utf-8"), object_hook=dict_to_sns)
    except ValueError:
        pass
    client_id = msg.topic.split("/")[-1]
    scene = json_msg.scene
    if hasattr(json_msg, "vio"):
        # Only take first marker for now, later iterate and avg all markers
        detected_tag = json_msg.detections[0]
        pos = json_msg.vio.position
        rot = json_msg.vio.rotation

        # Construct pose matrix4 for camera
        vio_pose = np.identity(4)
        vio_pose[0:3, 0:3] = Rotation.from_quat(
            [rot._x, rot._y, rot._z, rot._w]
        ).as_matrix()
        vio_pose[0:3, 3] = [pos.x, pos.y, pos.z]

        # Construct pose matrix for detected tag
        dtag_pose_s1 = np.identity(4)
        # Correct for column-major format of detected tag pose
        R_correct = np.array(detected_tag.s1.R).T
        dtag_pose_s1[0:3, 0:3] = R_correct
        dtag_pose_s1[0:3, 3] = detected_tag.s1.t
        # Swap x/y axis of detected tag coordinate system
        dtag_pose_s1 = np.array(FLIP) @ dtag_pose_s1 @ np.array(FLIP)
        dtag_error_s1 = detected_tag.s1.e

        # Construct pose matrix for detected tag
        dtag_pose_s2 = np.identity(4)
        # Correct for column-major format of detected tag pose
        R_correct = np.array(detected_tag.s2.R).T
        dtag_pose_s2[0:3, 0:3] = R_correct
        dtag_pose_s2[0:3, 3] = detected_tag.s2.t
        # Swap x/y axis of detected tag coordinate system
        dtag_pose_s2 = np.array(FLIP) @ dtag_pose_s2 @ np.array(FLIP)
        dtag_error_s2 = detected_tag.s2.e

        dtag_pose, dtag_error = resolve_pose_ambiguity(
            dtag_pose_s1, dtag_error_s1, dtag_pose_s2, dtag_error_s2, vio_pose)

        # Just guessed the threshold for tag error
        if dtag_error > 5e-6:
            log("Too tag much error")
            return

        mqtt_response = None

        unknown_tag = hasattr(json_msg, "refTag") and json_msg.refTag is None
        builder = hasattr(json_msg, "builder") and json_msg.builder

        # Solve for tag, not for user
        if (builder or unknown_tag) and detected_tag.id != 0:
            log("Solve for tag", str(detected_tag.id))

            if not vio_filter(vio_pose, client_id, VIO_MAX_DIFF_LOW):
                return

            rig_pose = RIGS.get(client_id)
            if rig_pose is None:
                # Don't have client RIG offset, can't solve
                log("Don't have client rig pose:", client_id)
                return

            # Calculate pose of apriltag
            ref_tag_pose = rig_pose @ vio_pose @ dtag_pose
            ref_tag_pos = ref_tag_pose[0:3, 3]
            ref_tag_rotq = Rotation.from_matrix(
                ref_tag_pose[0:3, 0:3]).as_quat()

            if builder:
                if not hasattr(json_msg, "geolocation"):
                    log("Builder provided no geolocation")
                    return
                newu_uuid_name = (
                    str(detected_tag.id)
                    + "_"
                    + str(json_msg.geolocation.latitude)
                    + "_"
                    + str(json_msg.geolocation.longitude)
                )
                new_uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, newu_uuid_name))

                # either UUID is supplied from builder request, or its recently
                # added as new
                ref_uuid = None
                if hasattr(detected_tag, "refTag") and hasattr(detected_tag.refTag, "uuid"):
                    ref_uuid = json_msg.refTag.uuid
                elif ADDED_TAGS.get(new_uuid) is not None:
                    ref_uuid = new_uuid
                if ref_uuid is not None:
                    log("Builder updating existing tag")
                    resp = requests.patch(
                        TAG_URLBASE + "/" + ref_uuid,
                        json={"pose": ref_tag_pose.tolist()},
                        auth=HTTPBasicAuth("conix", "conix"),
                    )
                else:
                    log("Builder create new tag")
                    # retain tags known to be have been created as hashed by
                    # tagid, lat, long. Prevents duplicated entries (ideally)
                    if ADDED_TAGS.get(new_uuid) is not None:
                        log("Tag already added recently")
                    else:
                        ADDED_TAGS[new_uuid] = True
                        new_tag = {
                            "id": new_uuid,
                            "name": "apriltag_" + str(detected_tag.id),
                            "pose": ref_tag_pose.tolist(),
                            "lat": json_msg.geolocation.latitude,
                            "long": json_msg.geolocation.longitude,
                            "ele": 0,
                            "objectType": "apriltag",
                            "url": "https://conix.io",
                        }
                        log(new_tag)
                        resp = requests.post(
                            TAG_URLBASE, json=new_tag, auth=HTTPBasicAuth(
                                "conix", "conix"),
                        )
                print("Updating Tag %d", detected_tag.id)
                print(ref_tag_pos)
                print(ref_tag_rotq)

            mqtt_response = {
                "object_id": "apriltag_" + str(detected_tag.id),
                "action": "update",
                "type": "object",
                "data": {
                    "position": {
                        "x": ref_tag_pos[0],
                        "y": ref_tag_pos[1],
                        "z": ref_tag_pos[2],
                    },
                    "rotation": {
                        "x": ref_tag_rotq[0],
                        "y": ref_tag_rotq[1],
                        "z": ref_tag_rotq[2],
                        "w": ref_tag_rotq[3],
                    },

                },
            }
            if builder:
                builder_mqtt = {
                    "action": "create",
                    "data": {
                        "object_type": "cube",
                        "scale": {"x": 0.15, "y": 0.15, "z": 0.02},
                        "color": "#ff0000"
                    }
                }
                mqtt_response = {**mqtt_response, **builder_mqtt}
        else:  # Solving for client rig, default localization operation
            log("Localizing", client_id, "on", str(detected_tag.id))
            if not vio_filter(vio_pose, client_id, VIO_MAX_DIFF_HIGH):
                return
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
            rig_pose = ref_tag_pose @ np.linalg.inv(
                dtag_pose) @ np.linalg.inv(vio_pose)
            rig_pos = rig_pose[0:3, 3]
            rig_rotq = Rotation.from_matrix(rig_pose[0:3, 0:3]).as_quat()
            RIGS[client_id] = rig_pose
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

        # mqtt_response = {
        #    "new_pose": {
        #        'position': { 'x': new_pos[0], 'y': new_pos[1], 'z': new_pos[2]},
        #        'rotation': { 'x': new_rotq[0],'y': new_rotq[1],'z': new_rotq[2],'w': new_rotq[3]}
        #    }
        # }
        if mqtt_response is not None:
            client.publish("realm/s/" + scene, json.dumps(mqtt_response))
        # client.publish(TOPIC + client_id, json.dumps(mqtt_response))
    elif hasattr(json_msg, "rigMatrix"):  # Local solved, probably tag 0
        RIGS[client_id] = json_msg.rigMatrix


def start_mqtt():
    mttqc = mqtt.Client(CLIENT_ID, clean_session=True, userdata=None)
    mttqc.connect(HOST, PORT)
    print("Connected MQTT")
    mttqc.subscribe(TOPIC + "#")
    mttqc.message_callback_add(TOPIC + "#", on_tag_detect)
    mttqc.loop_forever()


start_mqtt()
