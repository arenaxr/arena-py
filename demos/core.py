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
arena.debug()


def signal_handler(sig, frame):
    exit()


signal.signal(signal.SIGINT, signal_handler)

cube = arena.Object(
    objName="cube_1", objType=arena.Shape.cube, location=(1, 1, -1), color=(255, 0, 0)
)
input("")

cube.update(color=(0, 255, 0))
input("")

cube.update(data='{"material": {"transparent": true, "opacity": 0.5}}')
input("")

cube.position((2, 2, -1))
input("")

cube.update(rotation=(0.4, 0.4, 0.4, 0.4))
input("")

cube.update(
    data='{"animation": {"property":"rotation","to":"0 360 0","loop":"true","dur":10000}}'
)
input("")

cube.delete()
input("")

floor = arena.Object(
    objName="my_image_floor",
    objType=arena.Shape.image,
    location=(0, 0, 0.4),
    rotation=(-0.7, 0, 0, 0.7),
    scale=(12, 12, 12),
    data='{"url": "images/floor.png", "material": {"repeat": {"x":4, "y":4}}}',
)
input("")

floor.update(
    data='{"material": {"src": "https://xr.andrew.cmu.edu/abstract/downtown.png"}}'
)
input("")

torus = arena.Object(
    objName="", objType=arena.Shape.torusKnot, color=(255, 0, 0), location=(0, 3, -6)
)
input("")

torus.update(color=(0, 0, 255))
input("")

arena.Object(
    objName="model1",
    objType=arena.Shape.gltf_model,
    location=(0, 0, -4),
    url="models/Duck.glb",
)
input("")

cow = arena.Object(
    objName="model2",
    objType=arena.Shape.gltf_model,
    location=(-21, 1.8, -8),
    scale=(0.02, 0.02, 0.02),
    url="models/cow2/scene.gltf",
)
input("")

# (dangerous) technique to update everyone's camera rig without knowing name
rig=arena.Object(objName="cameraRig")
rig.update(location=(1, 1, 1))
input("")

cow.update(data='{"animation-mixer": {"clip": "*"}}')
input("")

text = arena.Object(
    objName="text_3",
    objType=arena.Shape.text,
    color=(255, 0, 0),
    location=(0, 3, -4),
    data='{"text":"Hello world!"}',
)
input("")

text.update(color=(0, 255, 0))
input("")

arena.Object(
    objName="myLight",
    objType=arena.Shape.light,
    location=(1, 1, 1),
    rotation=(0.25, 0.25, 0.25, 1),
    color=(255, 0, 0),
)
input("")

arena.Object(
    objName="line1",
    objType=arena.Shape.line,
    data='{"start": {"x":3, "y": 2, "z": -4}, "end": {"x":3, "y": 3, "z": -4}, "color": "#CE00FF"}',
)
input("")

arena.Object(
    objName="line2",
    objType=arena.Shape.thickline,
    data='{"lineWidth": 11, "color": "#FF88EE", "path": "3 4 -4, 4 4 -4, 4 5 -4, 4 5 -5"}',
)
input("")

torus.update(physics=arena.Physics.dynamic)
input("")

torus.update(ttl=2)
input("")

# trick: obtain an arena.py Object for an already-existing global scene object named "cameraRig"
# in order to update it's data attributes
rig=arena.Object(objName="cameraRig")
rig.update(data='{"animation": {"property": "position","to": "0 10 20","easing": "linear","dur": 1000}}')
input("")
rig.update(data='{"animation": {"property": "position","to": "0 10 -200","easing": "linear","dur": 1000}}')

arena.handle_events()
