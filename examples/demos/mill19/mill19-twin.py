import json
import math
import time

import numpy as np

from arena import *

scene = Scene(host="arena-dev1.conix.io", namespace="mwfarb", scene="mill19")

# motoman joints
mmjoints = {
    # 'base_link-base',  # limit: {lower: 0, upper: 0}, fixed
    # 'flange-tool0',  # limit: {lower: 0, upper: 0}, fixed
    # revolute
    'joint_1_s': {'limit': {'lower': -2.9670597283903604, 'upper': 2.9670597283903604}},
    # revolute
    'joint_2_l': {'limit': {'lower': -1.9198621771937625, 'upper': 2.2689280275926285}},
    # revolute
    'joint_3_u': {'limit': {'lower': -1.1344640137963142, 'upper': 3.490658503988659}},
    # revolute
    'joint_4_r': {'limit': {'lower': -3.490658503988659, 'upper': 3.490658503988659}},
    # revolute
    'joint_5_b': {'limit': {'lower': -2.1467549799530254, 'upper': 2.1467549799530254}},
    # revolute
    'joint_6_t': {'limit': {'lower': -7.941248096574199, 'upper': 7.941248096574199}},
    # 'joint_6_t-flange',  # limit: {lower: 0, upper: 0}, fixed
}
# mp400 joints
mpjoints = [
    'base_footprint_joint',  # limit: {lower: 0, upper: 0}, fixed
    'lidar_1_joint',  # limit: {lower: 0, upper: 0}, fixed
    # limit: {lower: -10000000000000000, upper: 10000000000000000}, fixed
    'mp_400_wheel_back_left_joint',
    # limit: {lower: -10000000000000000, upper: 10000000000000000}, fixed
    'mp_400_wheel_back_right_joint',
    # limit: {lower: -10000000000000000, upper: 10000000000000000}, fixed
    'mp_400_wheel_front_left_joint',
    # limit: {lower: -10000000000000000, upper: 10000000000000000}, fixed
    'mp_400_wheel_front_right_joint',
    # limit: {lower: -10000000000000000, upper: 10000000000000000}, fixed
    'mp_400_wheel_left_joint',
    # limit: {lower: -10000000000000000, upper: 10000000000000000}, fixed
    'mp_400_wheel_right_joint',
]
# waypoints, 2nd floor
wps = [
    {"x": 5.20, "y": 4.60, "z": 17.90},
    {"x": 5.20, "y": 4.60, "z": 12.90},
    {"x": 7.95, "y": 4.60, "z": 12.90},
    {"x": 7.95, "y": 4.60, "z": 17.90},
]

# {"object_id":"motoman","persist":true,"type":"object","action":"update","data":{"object_type":"urdf-model","url":"store/users/mwfarb/xacro/motoman_gp4_support/urdf/gp4.xacro","urlBase":"/store/users/mwfarb/xacro/motoman_gp4_support","position":{"x":6.22109,"y":5.30667,"z":16.84618},"rotation":{"w":0.707,"x":-0.707,"y":0,"z":0},"scale":{"x":1,"y":1,"z":1}}}
motoman = UrdfModel(
    object_id="motoman",
    position={"x": 6.22, "y": 5.40, "z": 16.84},
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
    position=wps[1],
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
    # scene.add_object(Sphere(scale=(.1, .1, .1), position=waypoints[0]))
    # scene.add_object(Sphere(scale=(.1, .1, .1), position=waypoints[1]))
    # scene.add_object(Sphere(scale=(.1, .1, .1), position=waypoints[2]))
    # scene.add_object(Sphere(scale=(.1, .1, .1), position=waypoints[3]))


@scene.run_forever(interval_ms=100)
def update_bots():
    mmj = []
    t = time.time()

    # bend motoman arm joints
    offset = math.pi
    ratio = math.sin(t + offset)
    print(ratio)
    for jointname, joint in mmjoints.items():
        lower_deg = math.degrees(joint['limit']['lower'])
        upper_deg = math.degrees(joint['limit']['upper'])
        angle = np.interp(ratio, [-1, 1], [lower_deg, upper_deg])
        mmj.append(f"{jointname}:{angle}")

    motoman.update_attributes(joints=", ".join(mmj), persist=False)
    scene.update_object(motoman)
    motoman_sign.update_attributes(body="\n".join(
        mmj).replace(':', '\t'), persist=False)
    scene.update_object(motoman_sign)

    # move mp400 along floor
    x = np.interp(ratio, [-1, 1], [wps[0]['x'], wps[1]['x']])
    z = np.interp(ratio, [-1, 1], [wps[0]['z'], wps[1]['z']])
    position = {'x': x, 'y': wps[0]['y'], 'z': z}
    mp400.update_attributes(position=position, persist=False)
    scene.update_object(mp400)
    mp400_sign.update_attributes(body=json.dumps(position), persist=False)
    scene.update_object(mp400_sign)


# start tasks
scene.run_tasks()

# for docs
# names: motoman.getObject3D('mesh').joints
# named joint lower limit: motoman.getObject3D('mesh').joints.joint_1_s.limit.lower
# named joint lower upper: motoman.getObject3D('mesh').joints.joint_1_s.limit.upper

# high bay model and second floor
# {"object_id":"highbay","persist":true,"type":"object","action":"update","data":{"object_type":"gltf-model","url":"/store/users/agr/scans/mill19_2M_8K_v2.glb","position":{"x":0,"y":0,"z":0},"rotation":{"w":1,"x":0,"y":0,"z":0},"scale":{"x":1,"y":1,"z":1},"hide-on-enter-ar":true}}
# {"object_id":"floor2","persist":true,"type":"object","action":"update","data":{"object_type":"plane","height":12.31,"width":7.58,"position":{"x":5.20345,"y":4.556,"z":16.907},"rotation":{"w":0.7064337796563814,"x":0.7064337647694028,"y":0.03084356492222166,"z":-0.03084356427224214},"material":{"color":"#111111","side":"double"},"hide-on-enter-ar":true}}

# waypoints, 1st floor
# {"object_id":"wp1","persist":true,"type":"object","action":"update","data":{"object_type":"entity","position":{"x":-4.06,"y":0.06,"z":-4.37}}}
# {"object_id":"wp2","persist":true,"type":"object","action":"update","data":{"object_type":"entity","position":{"x":-1.85,"y":0.06,"z":20.69}}}
