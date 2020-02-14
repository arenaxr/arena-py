import json
import random
from types import SimpleNamespace

import numpy as np
import paho.mqtt.client as mqtt
from scipy.spatial.transform import Rotation

CLIENT_ID = 'apriltag_solver' + str(random.randint(0, 100))
HOST = "oz.andrew.cmu.edu"
TOPIC = "realm/g/a/"

TAGS = {
    12: [[1, 0, 0, 0.149],
         [0, 1, 0, 1.401],
         [0, 0, 1, -3.666],
         [1, 0, 0, 1]],
}


def dict_to_sns(d):
    return SimpleNamespace(**d)


def on_tag_detect(client, userdata, msg):
    json_msg = None
    try:
        json_msg = json.loads(msg.payload.decode("utf-8"),
                              object_hook=dict_to_sns)
    except ValueError:
        pass
    if hasattr(json_msg, 'vio'):
        client_id = msg.topic.split('/')[-1]

        # Only take first marker for now, later iterate and avg all markers
        this_tag = json_msg.detections[0]

        tag_pose = TAGS[this_tag.id]

        pos = json_msg.vio.position
        rot = json_msg.vio.rotation

        vio_pose = np.identity(4)
        vio_pose[0:3, 0:3] = Rotation.from_quat(
            [rot._x, rot._y, rot._z, rot._w]).as_matrix()
        vio_pose[0:3, 3] = [pos.x, pos.y, pos.z]

        dtag_pose = np.identity(4)
        dtag_pose[0:3, 0:3] = this_tag.pose.R
        dtag_pose[0:3, 3] = this_tag.pose.t

        new_pose = tag_pose @ np.linalg.inv(dtag_pose) @ np.linalg.inv(vio_pose)
        new_pos = new_pose[0:3, 3]
        new_rotq = Rotation.from_matrix(new_pose[0:3, 0:3]).as_quat()

        mqtt_response = {
            'object_id': client_id,
            'action': 'update',
            'type': 'rig',
            'data': {
                'position': {
                    'x': new_pos[0],
                    'y': new_pos[1],
                    'z': new_pos[2]
                },
                'rotation': {
                    'x': new_rotq[0],
                    'y': new_rotq[1],
                    'z': new_rotq[2],
                    'w': new_rotq[3]
                }
            }
        }

        #mqtt_response = {
        #    "new_pose": {
        #        'position': {
        #            'x': new_pos[0],
        #            'y': new_pos[1],
        #            'z': new_pos[2]
        #        },
        #        'rotation': {
        #            'x': new_rotq[0],
        #            'y': new_rotq[1],
        #            'z': new_rotq[2],
        #            'w': new_rotq[3]
        #        }
        #    }
        #}
        client.publish("realm/s/render", json.dumps(mqtt_response))
        # client.publish(TOPIC + client_id, json.dumps(mqtt_response))


mttqc = mqtt.Client(CLIENT_ID, clean_session=True, userdata=None)
mttqc.connect(HOST)
mttqc.subscribe(TOPIC + "#")
mttqc.message_callback_add(TOPIC + "#", on_tag_detect)
mttqc.loop_forever()
