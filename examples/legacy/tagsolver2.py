import arena
import json
import random
from types import SimpleNamespace

import numpy as np
from scipy.spatial.transform import Rotation

CLIENT_ID = 'apriltag_solver_' + str(random.randint(0, 100))
HOST = "oz.andrew.cmu.edu"
TOPIC = "a"

# fmt: off

TAGS = {  # Local cache, TBD how it's invalidated or refreshed from MongoDB
    0: [[1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, -1, 0, 0],
        [1, 0, 0, 1]],
}

FLIP = [[1, 0, 0, 0],
        [0, -1, 0, 0],
        [0, 0, -1, 0],
        [0, 0, 0, 1]]

# fmt: on


def dict_to_sns(d):
    return SimpleNamespace(**d)


def on_tag_detect(msg):
    json_msg = None
    try:
        json_msg = json.loads(msg.payload.decode("utf-8"), object_hook=dict_to_sns)
    except ValueError:
        pass
    if hasattr(json_msg, 'vio'):
        client_id = msg.topic.split('/')[-1]
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
        dtag_pose[0:3, 3] = detected_tag.pose.t

        dtag_pose = np.array(FLIP) @ dtag_pose @ np.array(FLIP)

        update_type = ""

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

                TAGS[detected_tag.id] = ref_tag_pose  # Store as reference

                arena.Object(
                    objId = "apriltag_" + str(detected_tag.id),
                    position = (
                        ref_tag_pos[0],
                        ref_tag_pos[1],
                        ref_tag_pos[2]
                        ),
                    rotation = {
                        ref_tag_rotq[0],
                        ref_tag_rotq[1],
                        ref_tag_rotq[2],
                        ref_tag_rotq[3]
                        }
                    )

        else:  # Solving for client rig, default localization operation
            print("Localizing", client_id, "on", str(detected_tag.id))
            ref_tag_pose = TAGS.get(detected_tag.id)
            if ref_tag_pose is None:
                # Tag not found. TODO: query ATLAS for it
                print("Tag not found, not in build mode")
                return
            rig_pose = ref_tag_pose @ np.linalg.inv(dtag_pose) @ np.linalg.inv(vio_pose)
            rig_pos = rig_pose[0:3, 3]
            rig_rotq = Rotation.from_matrix(rig_pose[0:3, 0:3]).as_quat()

            RIGS[client_id] = rig_pose
            scene.updateRig(
                client_id,
                (rig_pos[0],
                 rig_pos[1],
                 rig_pos[2]),
                (rig_rotq[0],
                 rig_rotq[1],
                 rig_rotq[2],
                 rig_rotq[3])
            )

        # mqtt_response = {
        #    "new_pose": {
        #        'position': { 'x': new_pos[0], 'y': new_pos[1], 'z': new_pos[2]},
        #        'rotation': { 'x': new_rotq[0],'y': new_rotq[1],'z': new_rotq[2],'w': new_rotq[3]}
        #    }
        # }

arena.init(HOST, "realm", TOPIC, on_tag_detect)
arena.handle_events()
