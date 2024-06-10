import math
import time

import numpy as np

from arena import *

scene = Scene(host="arena-dev1.conix.io", namespace="mwfarb", scene="mill19")

# {"object_id":"motoman","persist":true,"type":"object","action":"update","data":{"object_type":"urdf-model","url":"store/users/mwfarb/xacro/motoman_gp4_support/urdf/gp4.xacro","urlBase":"/store/users/mwfarb/xacro/motoman_gp4_support","position":{"x":6.22109,"y":5.30667,"z":16.84618},"rotation":{"w":0.707,"x":-0.707,"y":0,"z":0},"scale":{"x":1,"y":1,"z":1}}}
motoman = UrdfModel(
    object_id="motoman",
    position={"x": 6.22, "y": 5.30, "z": 16.84},
    rotation={"w": 0.70711, "x": -0.70711, "y": 0, "z": 0},
    scale={"x": 1, "y": 1, "z": 1},
    url="store/users/mwfarb/xacro/motoman_gp4_support/urdf/gp4.xacro",
    urlBase="/store/users/mwfarb/xacro/motoman_gp4_support",
    persist=True,
)
motoman_sign = ArenauiCard(
    object_id="motoman_sign",
    parent=motoman.object_id,
    title="Motoman GP7 GP8",
    body="You found me!!!",
    position=(0, 0, 1),
    look_at="#my-camera",
    persist=True,
)
# {"object_id":"mp400","persist":true,"type":"object","action":"update","data":{"object_type":"urdf-model","url":"store/users/mwfarb/xacro/neo_mp_400/robot_model/mp_400/mp_400.urdf.xacro","urlBase":"/store/users/mwfarb/xacro/neo_mp_400","position":{"x":-4.068,"y":0.06,"z":-4.37729},"rotation":{"w":0.707,"x":-0.707,"y":0,"z":0},"scale":{"x":1,"y":1,"z":1}}}
mp400 = UrdfModel(
    object_id="mp400",
    position={"x": -4.06, "y": 0.06, "z": -4.37},
    rotation={"w": 0.70711, "x": -0.70711, "y": 0, "z": 0},
    scale={"x": 1, "y": 1, "z": 1},
    url="store/users/mwfarb/xacro/neo_mp_400/robot_model/mp_400/mp_400.urdf.xacro",
    urlBase="/store/users/mwfarb/xacro/neo_mp_400",
    persist=True,
)
mp400_sign = ArenauiCard(
    object_id="mp400_sign",
    parent=mp400.object_id,
    title="Mobile Robot MP-400",
    body="Follow me!!!",
    position=(0, 0, 1),
    look_at="#my-camera",
    persist=True,
)


@scene.run_once
def main():
    scene.add_object(motoman)
    scene.add_object(motoman_sign)
    scene.add_object(mp400)
    scene.add_object(mp400_sign)


mmjoints = [
    # 'base_link-base',
    # 'flange-tool0',
    'joint_1_s',
    'joint_2_l',
    'joint_3_u',
    'joint_4_r',
    'joint_5_b',
    'joint_6_t',
    # 'joint_6_t-flange',
]
mpjoints = [
    # 'base_footprint_joint',
    # 'lidar_1_joint',
    'mp_400_wheel_back_left_joint',
    'mp_400_wheel_back_right_joint',
    'mp_400_wheel_front_left_joint',
    'mp_400_wheel_front_right_joint',
    'mp_400_wheel_left_joint',
    'mp_400_wheel_right_joint',
]
sec_range = 10


@scene.run_forever(interval_ms=100)
def bend_joints():
    mmj = []
    # mpj = []
    t = time.time() * 1000 / 3**2
    for i in range(1, 6 + 1):

        offset = i * math.pi / 3
        ratio = max(0, math.sin(t + offset))
        # joints.append(f"HP{i}:{np.interp(ratio, [0, 1], [30, 0])}")
        # joints.append(f"KP{i}:{np.interp(ratio, [0, 1], [90, 150])}")
        # joints.append(f"AP{i}:{np.interp(ratio, [0, 1], [-30, -60])}")
        angle = np.interp(ratio, [0, 1], [30, 0])
        mmj.append(f"{mmjoints[i-1]}:{angle}")

    motoman.update_attributes(joints=", ".join(mmj), persist=False)
    scene.update_object(motoman)
    motoman_sign.update_attributes(body="\n".join(mmj), persist=False)
    scene.update_object(motoman_sign)


# start tasks
scene.run_tasks()

# for docs
# motoman.getObject3D('mesh').joints

# high bay model and second floor
# {"object_id":"highbay","persist":true,"type":"object","action":"update","data":{"object_type":"gltf-model","url":"/store/users/agr/scans/mill19_2M_8K_v2.glb","position":{"x":0,"y":0.02108,"z":0},"rotation":{"w":1,"x":0,"y":0,"z":0},"scale":{"x":1,"y":1,"z":1},"hide-on-enter-ar":true}}
# {"object_id":"floor2","persist":true,"type":"object","action":"update","data":{"object_type":"plane","height":12.31,"width":7.58,"position":{"x":5.20345,"y":4.536,"z":16.907},"rotation":{"w":0.7064337796563814,"x":0.7064337647694028,"y":0.03084356492222166,"z":-0.03084356427224214},"material":{"color":"#111111","side":"double"},"hide-on-enter-ar":true}}

# way points
# {"object_id":"wp1","persist":true,"type":"object","action":"update","data":{"object_type":"entity","position":{"x":-4.06,"y":0.06,"z":-4.37}}}
# {"object_id":"wp2","persist":true,"type":"object","action":"update","data":{"object_type":"entity","position":{"x":-1.85,"y":0.06,"z":20.69}}}

# motoman.getObject3D('mesh').joints
# dY {isObject3D: true, uuid: '58518d01-2224-4bb8-93ef-383038637514', name: 'base_link-base', type: 'URDFJoint', parent: d$, …}
# dY {isObject3D: true, uuid: 'ccd1c2bb-20be-4679-8e61-3205a79ff0a8', name: 'flange-tool0', type: 'URDFJoint', parent: dX, …}
# dY {isObject3D: true, uuid: 'eb34929e-7d83-4f32-a57b-635ea138293d', name: 'joint_1_s', type: 'URDFJoint', parent: d$, …}
# dY {isObject3D: true, uuid: '9282662a-cf40-4770-aaa9-5945a73507a4', name: 'joint_2_l', type: 'URDFJoint', parent: dX, …}
# dY {isObject3D: true, uuid: 'f2315018-4721-401f-a5a9-5295ebdcbafc', name: 'joint_3_u', type: 'URDFJoint', parent: dX, …}
# dY {isObject3D: true, uuid: '93f1dfa3-3625-40c4-8ceb-60a19302d42c', name: 'joint_4_r', type: 'URDFJoint', parent: dX, …}
# dY {isObject3D: true, uuid: '006e718d-14b6-4dab-a772-fe15ea61ba4b', name: 'joint_5_b', type: 'URDFJoint', parent: dX, …}
# dY {isObject3D: true, uuid: '5a5c3073-080a-403c-bcd4-8411e39ec45c', name: 'joint_6_t', type: 'URDFJoint', parent: dX, …}
# dY {isObject3D: true, uuid: 'e776933e-3873-48fe-9d22-198f45f1add2', name: 'joint_6_t-flange', type: 'URDFJoint', parent: dX, …}

# mp400_model.getObject3D('mesh').joints
# dY {isObject3D: true, uuid: 'd26db5dd-7606-428e-9501-6db85af53d9b', name: 'base_footprint_joint', type: 'URDFJoint', parent: d$, …}
# dY {isObject3D: true, uuid: 'cef17b8e-f57a-4771-a2de-828eeacdc80a', name: 'lidar_1_joint', type: 'URDFJoint', parent: d$, …}
# dY {isObject3D: true, uuid: 'e7c6432b-2e4c-45c4-926e-d3c67294c73b', name: 'mp_400_wheel_back_left_joint', type: 'URDFJoint', parent: dX, …}
# dY {isObject3D: true, uuid: '50c02b1c-6813-494d-a607-54823baab1d1', name: 'mp_400_wheel_back_right_joint', type: 'URDFJoint', parent: dX, …}
# dY {isObject3D: true, uuid: '2a3181b6-dde9-42c2-a863-6da0332596f8', name: 'mp_400_wheel_front_left_joint', type: 'URDFJoint', parent: dX, …}
# dY {isObject3D: true, uuid: '18fb6071-e2d4-4a3b-b519-8ed11e06e9e5', name: 'mp_400_wheel_front_right_joint', type: 'URDFJoint', parent: dX, …}
# dY {isObject3D: true, uuid: 'c2c6780c-4306-43f9-a466-31ec8c5aea85', name: 'mp_400_wheel_left_joint', type: 'URDFJoint', parent: dX, …}
# dY {isObject3D: true, uuid: '1b43fddd-5515-43a7-80fd-25ba94a12cd7', name: 'mp_400_wheel_right_joint', type: 'URDFJoint', parent: dX, …}
