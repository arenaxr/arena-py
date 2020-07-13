# volatile.py
''' Demonstrate setting apriltags which can receive external updates.
    The apriltag #450 must be visible from a webxr browser camera.
    Position, Rotation, and Text(time) should remain in sync across cameras.
    View: https://xr.andrew.cmu.edu/?scene=external&localTagSolver=true
'''
import datetime
import json

import arena

BROKER = "oz.andrew.cmu.edu"
REALM = "realm"
SCENE = "volatile"


def update_text(object_id, text):
    msg = {
        "object_id": object_id,
        "action": "update",
        "type": "object",
        "data": {"text": text},
    }
    arena.arena_publish(REALM + "/s/" + SCENE, msg)


def scene_callback(msg):
    json_msg = json.loads(msg)
    if json_msg["object_id"] == TIME.objName:
        print(msg)
        if json_msg["action"] == "update" and "camera_id" in json_msg:
            update_text(
                TIME.objName,
                datetime.datetime.now().strftime('%H:%M:%S')
            )


arena.init(BROKER, REALM, SCENE, scene_callback)
# TAG = arena.Object(objName="apriltag_450",
#                    #data='{"material": {"transparent": true, "opacity": 0}}',
#                    volatile=True)
# arena.Object(objName="duck",
#              objType=arena.Shape.gltf_model,
#              scale=(0.1, 0.1, 0.1),
#              rotation=(0.7, 0, 0, 0.7),
#              parent=TAG.objName,
#              url="models/Duck.glb",
#              volatile=True)
TIME = arena.Object(objName="apriltag_450",
                    objType=arena.Shape.text,
                    text=datetime.datetime.now().strftime('%H:%M:%S'),
                    # parent=TAG.objName,
                    color=(255, 0, 0),
                    volatile=True)

# our main event loop
arena.handle_events()
