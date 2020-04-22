import json
import random
import uuid
from types import SimpleNamespace

import requests
from requests.auth import HTTPBasicAuth

import numpy as np
import paho.mqtt.client as mqtt
from scipy.spatial.transform import Rotation

with open('config.json') as config_file:
    CONFIG = json.load(config_file)

CLIENT_ID = "apriltag_solver_" + str(random.randint(0, 100))

HOST = CONFIG['host']
PORT = CONFIG['port']
TOPIC = CONFIG['default_realm'] + "/g/a/"
TAGLOAD_URL = "https://atlas.conix.io/lookup/geo?lat=0&long=0&distance=20000&units=km&objectType=apriltag"
TAG_URLBASE = "https://atlas.conix.io/record"

# fmt: off

TAGS = {  # Local cache, TBD how it's invalidated or refreshed from MongoDB
    0: {
        "id": "Origin",
        "pose":
            [[1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, -1, 0, 0],
            [1, 0, 0, 1]],
    }
}

FLIP = [[1, 0, 0, 0],
        [0, -1, 0, 0],
        [0, 0, -1, 0],
        [0, 0, 0, 1]]

# fmt: on

RIGS = {}
VIO_STATE = {}
FRAME_COUNTER = {}

def dict_to_sns(d):
    return SimpleNamespace(**d)


def on_tag_detect(client, userdata, msg):
    json_msg = None
    try:
        json_msg = json.loads(msg.payload.decode("utf-8"), object_hook=dict_to_sns)
    except ValueError:
        pass
    if hasattr(json_msg, "vio"):
        client_id = msg.topic.split("/")[-1]
        scene = json_msg.scene

        # Only take first marker for now, later iterate and avg all markers
        detected_tag = json_msg.detections[0]
        pos = json_msg.vio.position
        rot = json_msg.vio.rotation

        vio_pose = np.identity(4)
        vio_pose[0:3, 0:3] = Rotation.from_quat(
            [rot._x, rot._y, rot._z, rot._w]
        ).as_matrix()
        vio_pose[0:3, 3] = [pos.x, pos.y, pos.z]

        dtag_pose = np.identity(4)
        R_correct = np.array(detected_tag.pose.R).T
        dtag_pose[0:3, 0:3] = R_correct
        # dtag_pose[0:3, 0:3] = detected_tag.pose.R
        dtag_pose[0:3, 3] = detected_tag.pose.t
        dtag_pose = np.array(FLIP) @ dtag_pose @ np.array(FLIP)

        mqtt_response = None

        # Add some extremely simple filtering based on camera motion
        # make sure we get two readings with minimal vio movement
        vio_max_diff=100.0;  # set diff to a large value
        vio_pose_last=VIO_STATE.get(client_id)
        if vio_pose_last is None: 
             print( "skip, no previous camera location" )
             VIO_STATE[client_id] = vio_pose
             return
        else:
             # Directly subtract the current and previous pose matrix
             vio_pose_delta=np.subtract(vio_pose,vio_pose_last)
             # take absolute value of matrix elements and find max change value
             vio_pose_delta=abs(vio_pose_delta)
             vio_max_diff=vio_pose_delta.max()
        # save state of last vio position for this camera
        VIO_STATE[client_id] = vio_pose
        # Just guessed the threshold for motion
        if abs(vio_max_diff)>0.80:
             print( "Too much camera movement" )
             return 
        # Just guessed the threshold for tag error 
        if detected_tag.pose.e>5e-6:
             print( "Too tag much error" )
             return 


        if (
            hasattr(json_msg, "localize_tag")
            and json_msg.localize_tag
            and detected_tag.id != 0
        ):
            print("Solve for tag", str(detected_tag.id))
            # Solve for tag, not client
            rig_pose = RIGS.get(client_id)
            if rig_pose is None:
                # Don't have client RIG offset, can't solve
                print("Don't have client rig pose:", client_id)
            else:
                ref_tag_pose = rig_pose @ vio_pose @ dtag_pose
                ref_tag_pos = ref_tag_pose[0:3, 3]
                ref_tag_rotq = Rotation.from_matrix(ref_tag_pose[0:3, 0:3]).as_quat()
                if detected_tag.id in TAGS:
                    print("Builder updating existing tag")
                    # Update existing tag
                    TAGS[detected_tag.id]["pose"] = ref_tag_pose
                    resp = requests.patch(
                        TAG_URLBASE + "/" + TAGS[detected_tag.id]["id"],
                        json={"pose": ref_tag_pose.tolist()},
                        auth=HTTPBasicAuth("conix", "conix"),
                    )
                else:
                    # New tag, store it in memory and ATLAS
                    print("Builder create new tag")
                    TAGS[detected_tag.id] = {
                        "id": str(uuid.uuid4()),
                        "name": "apriltag_" + str(detected_tag.id),
                        "pose": ref_tag_pose.tolist(),
                        "lat": 0,  # TODO: get and pass along client lat/long
                        "long": 0,
                        "ele": 0,
                        "objectType": "apriltag",
                        "url": "https://conix.io",
                    }
                    print(TAGS[detected_tag.id])
                    resp = requests.post(
                        TAG_URLBASE,
                        json=TAGS[detected_tag.id],
                        auth=HTTPBasicAuth("conix", "conix"),
                    )
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
        else:  # Solving for client rig, default localization operation
            print("Localizing", client_id, "on", str(detected_tag.id))
            ref_tag = TAGS.get(detected_tag.id)
            if ref_tag is None:
                # Tag not found. TODO: query ATLAS for it
                print("Tag not found, not in build mode")
                return
            ref_tag_pose = ref_tag["pose"]
            rig_pose = ref_tag_pose @ np.linalg.inv(dtag_pose) @ np.linalg.inv(vio_pose)
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


def start_mqtt():
    mttqc = mqtt.Client(CLIENT_ID, clean_session=True, userdata=None)
    mttqc.connect(HOST, PORT)
    print("Connected MQTT")
    mttqc.subscribe(TOPIC + "#")
    mttqc.message_callback_add(TOPIC + "#", on_tag_detect)
    mttqc.loop_forever()


r = requests.get(TAGLOAD_URL)
loaded_tags = r.json()
for tag in loaded_tags:
    if tag["name"][0:9] == "apriltag_":
        tagid = int(tag["name"][9:])
        TAGS[tagid] = {
            "id": tag["id"],
            "name": tag["name"],
            "pose": tag["pose"],
            "lat": tag["lat"],
            "long": tag["long"],
            "ele:": tag["ele"],
            "objectType": "apriltag",
            "url": tag["url"],
        }
        print("Loaded tag", str(tagid))
start_mqtt()
