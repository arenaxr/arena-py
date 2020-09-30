# core.py
#
# examples of all the functions mentioned in http://github.com/conix-center/arena-core

import arena
import random
import time
import signal

arena.init("arena.andrew.cmu.edu", "realm", "examples")


def signal_handler(sig, frame):
    exit()


signal.signal(signal.SIGINT, signal_handler)

cube = arena.Object(
    objName="cube_1", objType=arena.Shape.cube, location=(1, 1, -1), color=(255, 0, 0)
)

cube.update(color=(0, 255, 0))

cube.update(data='{"material": {"transparent": true, "opacity": 0.5}}')

cube.position((2, 2, -1))

cube.update(rotation=(0.4, 0.4, 0.4, 0.4))

cube.update(
    data='{"animation": {"property":"rotation","to":"0 360 0","loop":"true","dur":10000}}'
)

cube.delete()

floor = arena.Object(
    objName="my_image_floor",
    objType=arena.Shape.image,
    location=(0, 0, 0.4),
    rotation=(-0.7, 0, 0, 0.7),
    scale=(12, 12, 12),
    data='{"url": "images/floor.png", "material": {"repeat": {"x":4, "y":4}}}',
)

floor.update(
    data='{"material": {"src": "https://arena.andrew.cmu.edu/abstract/downtown.png"}}'
)

torus = arena.Object(
    objName="", objType=arena.Shape.torusKnot, color=(255, 0, 0), location=(0, 3, -6)
)

torus.update(color=(0, 0, 255))

arena.Object(
    objName="model1",
    objType=arena.Shape.gltf_model,
    location=(0, 0, -4),
    url="https://arena.andrew.cmu.edu/models/Duck.glb",
)

cow = arena.Object(
    objName="model2",
    objType=arena.Shape.gltf_model,
    location=(-21, 1.8, -8),
    scale=(0.02, 0.02, 0.02),
    url="https://arena.andrew.cmu.edu/models/cow2/scene.gltf",
)

arena.updateRig("camera_er1k_er1k", (1, 1, 1), (0, 0, 0, 1))

cow.update(data='{"animation-mixer": {"clip": "*"}}')

text = arena.Object(
    objName="text_3",
    objType=arena.Shape.text,
    color=(255, 0, 0),
    location=(0, 3, -4),
    data='{"text":"Hello world!"}',
)

text.update(color=(0, 255, 0))

arena.Object(
    objName="myLight",
    objType=arena.Shape.light,
    location=(1, 1, 1),
    rotation=(0.25, 0.25, 0.25, 1),
    color=(255, 0, 0),
)

arena.Object(
    objName="line1",
    objType=arena.Shape.line,
    data='{"start": {"x":3, "y": 2, "z": -4}, "end": {"x":3, "y": 3, "z": -4}, "color": "#CE00FF"}',
)

arena.Object(
    objName="line2",
    objType=arena.Shape.thickline,
    data='{"lineWidth": 11, "color": "#FF88EE", "path": "3 4 -4, 4 4 -4, 4 5 -4, 4 5 -5"}',
)

torus.update(physics=arena.Physics.dynamic)

torus.update(ttl=2)

# trick: obtain an arena.py Object for an already-existing global scene object named "cameraRig"
# in order to update it's data attributes
rig = arena.Object(objName="cameraRig")
rig.update(
    data='{"animation": {"property": "position","to": "0 10 20","easing": "linear","dur": 1000}}')
rig.update(
    data='{"animation": {"property": "position","to": "0 10 -200","easing": "linear","dur": 1000}}')

arena.handle_events()
