"""URDF Model

Load a URDF model.

See guidance to store paths under <a href='https://docs.arenaxr.org/content/interface/filestore.html'>ARENA File Store, CDN, or DropBox</a>.
"""

import math
import time

import numpy as np

from arena import *

# setup library
scene = Scene(host="arenaxr.org", scene="example")

# make a model
athlete_model = UrdfModel(
    object_id="athlete_model",
    position=(0, 2.35, -7),
    rotation=(90, 0, 0),
    url="store/users/npereira/urdf/T12/urdf/T12_flipped.URDF",
)


@scene.run_once
def main():
    # add the model
    scene.add_object(athlete_model)


@scene.run_forever(interval_ms=100)
def bend_joints():
    # animate the legs
    joints = []
    t = time.time() * 1000 / 3**2
    for i in range(1, 6 + 1):

        offset = i * math.pi / 3
        ratio = max(0, math.sin(t + offset))

        joints.append(f"HP{i}:{np.interp(ratio, [0, 1], [30, 0])}")
        joints.append(f"KP{i}:{np.interp(ratio, [0, 1], [90, 150])}")
        joints.append(f"AP{i}:{np.interp(ratio, [0, 1], [-30, -60])}")

    # update joints
    athlete_model.update_attributes(joints=", ".join(joints))
    scene.update_object(athlete_model)


# start tasks
scene.run_tasks()
