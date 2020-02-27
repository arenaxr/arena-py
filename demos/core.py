# core.py
#
# examples of all the functions mentioned in http://github.com/conix-center/arena-core

import arena
import random
import time
import signal

HOST = "oz.andrew.cmu.edu"
SCENE = "core"

arena.init(HOST, "realm", SCENE)


def signal_handler(sig, frame):
    exit()


signal.signal(signal.SIGINT, signal_handler)

cube = arena.Object(
    objName="cube_1", objType=arena.Shape.cube, location=(1, 1, -1), color=(255, 0, 0)
)
time.sleep(1)

cube.update(color=(0, 255, 0))
time.sleep(1)

cube.update(data='{"material": {"transparent": true, "opacity": 0.5}}')
time.sleep(1)

cube.update(location=(2, 2, -1))
time.sleep(1)

cube.update(rotation=(0.4, 0.4, 0.4, 0.4))
time.sleep(1)

cube.update(
    data='{"animation": {"property":"rotation","to":"0 360 0","loop":"true","dur":10000}}'
)
time.sleep(2)

cube.delete()
time.sleep(1)

floor = arena.Object(
    objName="my_image_floor",
    objType=arena.Shape.image,
    location=(0, 0, 0.4),
    rotation=(-0.7, 0, 0, 0.7),
    scale=(12, 12, 12),
    data='{"url": "images/floor.png", "material": {"repeat": {"x":4, "y":4}}}',
)
time.sleep(1)

floor.update(
    data='{"material": {"src": "https://xr.andrew.cmu.edu/abstract/downtown.png"}}'
)
time.sleep(1)

torus = arena.Object(
    objName="", objType=arena.Shape.torusKnot, color=(255, 0, 0), location=(0, 3, -6)
)
time.sleep(1)

torus.update(color=(0, 0, 255))
time.sleep(1)

arena.Object(
    objName="model1",
    objType=arena.Shape.gltf_model,
    location=(0, 0, -4),
    url="https://xr.andrew.cmu.edu/models/Duck.glb",
)
time.sleep(1)

cow = arena.Object(
    objName="model2",
    objType=arena.Shape.gltf_model,
    location=(-21, 1.8, -8),
    scale=(0.02, 0.02, 0.02),
    url="https://xr.andrew.cmu.edu/models/cow2/scene.gltf",
)
time.sleep(2)

arena.updateRig("camera_er1k_er1k", (1, 1, 1), (0, 0, 0, 1))
time.sleep(1)

cow.update(data='{"animation-mixer": {"clip": "*"}}')
time.sleep(1)

text = arena.Object(
    objName="text_3",
    objType=arena.Shape.text,
    color=(255, 0, 0),
    location=(0, 3, -4),
    data='{"text":"Hello world!"}',
)
time.sleep(1)

text.update(color=(0, 255, 0))
time.sleep(1)

arena.Object(
    objName="myLight",
    objType=arena.Shape.light,
    location=(1, 1, 1),
    rotation=(0.25, 0.25, 0.25, 1),
    color=(255, 0, 0),
)
time.sleep(1)

arena.Object(
    objName="line1",
    objType=arena.Shape.line,
    data='{"start": {"x":3, "y": 2, "z": -4}, "end": {"x":3, "y": 3, "z": -4}, "color": "#CE00FF"}',
)
time.sleep(1)

arena.Object(
    objName="line2",
    objType=arena.Shape.thickline,
    data='{"lineWidth": 11, "color": "#FF88EE", "path": "3 4 -4, 4 4 -4, 4 5 -4, 4 5 -5"}',
)
time.sleep(1)

torus.update(physics=arena.Physics.dynamic)
time.sleep(2)

torus.update(ttl=2)
time.sleep(2)

rig=arena.Object(objName="cameraRig")
rig.update(data='{"animation": {"property": "position","to": "0 10 20","easing": "linear","dur": 1000}}')
time.sleep(2)
rig.update(data='{"animation": {"property": "position","to": "0 10 -200","easing": "linear","dur": 1000}}')

arena.handle_events()
