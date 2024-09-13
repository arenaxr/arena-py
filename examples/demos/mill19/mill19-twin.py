import json
import math
import time

import numpy as np

from arena import *

scene = Scene(host="arenaxr.org", namespace="agr", scene="mill19")

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

moto_dest_base = Object(
    object_id="moto_dest_base",
    position={"x": 6.22, "y": 6.40, "z": 16.25},
    # position={"x": 0, "y": 0.66, "z": 0.4},
    animation={
        "property": "rotation",
        "from": "0 0 0",
        "to": "0 360 0",
        "loop": True,
        "dur": 20000,
        "easing": "linear"
    },
    persist=True,
)
moto_dest = UrdfModel(
    object_id="moto_dest",
    parent="moto_dest_base",
    # rotation={"x": -90, "y": 0, "z": 0},
    rotation={"x": -90, "y": 90, "z": 0},
    scale={"x": 1, "y": 1, "z": 1},
    url="store/users/mwfarb/xacro/motoman_gp4_support/urdf/gp4.xacro",
    urlBase="/store/users/mwfarb/xacro/motoman_gp4_support",
    persist=True,
)
moto_dest_sign = ArenauiCard(
    object_id="moto_dest_sign",
    parent=moto_dest.object_id,
    title="Motoman GP7 GP8",
    body="Awaiting status update...",
    position=(0, 0, 1),
    look_at="#my-camera",
    persist=True,
)
moto_dest_sensor = Sphere(
    object_id="moto_dest_sensor",
    parent=moto_dest.object_id,
    position=(0, 0, .75),
    scale={"x": .1, "y": .1, "z": .1},
    material={"color": "#00ff00", "opacity": .75},
    clickable=True,
    persist=True,
)


def sensor_on_callback(scene, evt, msg):
    sensor_animate(scene, evt, "#00ff00", "#ff0000", 2000)


def sensor_off_callback(scene, evt, msg):
    sensor_animate(scene, evt, "#ff0000", "#00ff00", 500)


def sensor_animate(scene, evt, start, end, dur):
    global moto_dest_sensor
    if evt.type == "mousedown":
        moto_dest_sensor.update_attributes(
            animation={
                "property": "components.material.material.color",
                "type": "color",
                "from": start,
                "to": end,
                "dur": dur,
                "easings": "easeInOutBounce",
                "loop": "once",
                "autoplay": True,
            },
        )
        scene.update_object(moto_dest_sensor)


moto_dest_on = Box(
    object_id="moto_dest_on",
    position={"x": (6.22 - 4), "y": 6.40, "z": 16.25},
    scale={"x": .1, "y": .1, "z": .1},
    material={"color": "#00ff00"},
    evt_handler=sensor_on_callback,
    clickable=True,
    persist=True,
)
moto_dest_off = Box(
    object_id="moto_dest_off",
    position={"x": (6.22 - 4.1), "y": 6.40, "z": 16.25},
    scale={"x": .1, "y": .1, "z": .1},
    material={"color": "#ff0000"},
    evt_handler=sensor_off_callback,
    clickable=True,
    persist=True,
)

mp400 = UrdfModel(
    object_id="mp400",
    position=wps[0],
    rotation={"x": -90, "y": -90, "z": 0},
    scale={"x": 1, "y": 1, "z": 1},
    url="store/users/mwfarb/xacro/neo_mp_400/robot_model/mp_400/mp_400.urdf.xacro",
    urlBase="/store/users/mwfarb/xacro/neo_mp_400",
    persist=True,
)
mp400_sign = ArenauiCard(
    object_id="mp400_sign",
    # parent=mp400.object_id,
    title="Mobile Robot MP-400",
    body="Awaiting status update...",
    position=(wps[3]['x'], wps[3]['y']+1, wps[3]['z']),
    look_at="#my-camera",
    persist=True,
)


@scene.run_once
def main():
    scene.add_object(moto_dest_base)
    scene.add_object(moto_dest)
    scene.add_object(moto_dest_sensor)
    scene.add_object(moto_dest_sign)
    scene.add_object(moto_dest_on)
    scene.add_object(moto_dest_off)
    scene.add_object(mp400)
    scene.add_object(mp400_sign)
    # scene.add_object(Sphere(scale=(.1, .1, .1), position=waypoints[0]))
    # scene.add_object(Sphere(scale=(.1, .1, .1), position=waypoints[1]))
    # scene.add_object(Sphere(scale=(.1, .1, .1), position=waypoints[2]))
    # scene.add_object(Sphere(scale=(.1, .1, .1), position=waypoints[3]))


@scene.run_forever(interval_ms=100)
def update_moto_dest():
    mmj = []
    t = time.time()
    # bend motoman arm joints
    offset = math.pi
    ratio = math.sin(t + offset)
    for jointname, joint in mmjoints.items():
        lower_deg = math.degrees(joint['limit']['lower'])
        upper_deg = math.degrees(joint['limit']['upper'])
        angle = np.interp(ratio, [-1, 1], [lower_deg, upper_deg])
        mmj.append(f"{jointname}:{angle}")

    moto_dest.update_attributes(joints=", ".join(mmj), persist=False)
    scene.update_object(moto_dest)
    moto_dest_sign.update_attributes(body="\n".join(
        mmj).replace(':', '\t'), persist=False)
    scene.update_object(moto_dest_sign)


@scene.run_forever(interval_ms=100)
def update_mp400():
    t = time.time()
    # move mp400 along floor
    offset = math.pi
    ratio = math.sin(t + offset)
    if -1 <= ratio <= -.5:
        wp1 = 0
        wp2 = 1
        r = -90
    elif -.5 <= ratio <= 0:
        wp1 = 1
        wp2 = 2
        r = -180
    elif 0 <= ratio <= .5:
        wp1 = 2
        wp2 = 3
        r = -270
    else:
        wp1 = 3
        wp2 = 0
        r = 0
    xp = [-1+(wp1*.5), -.5+(wp1*.5)]

    x = np.interp(ratio, xp, [wps[wp1]['x'], wps[wp2]['x']])
    z = np.interp(ratio, xp, [wps[wp1]['z'], wps[wp2]['z']])
    position = {'x': x, 'y': wps[wp1]['y'], 'z': z}
    rotation = {'x': -90, 'y': r, 'z': 0}
    mp400.update_attributes(
        position=position, rotation=rotation, persist=False)
    scene.update_object(mp400)
    mp400_sign.update_attributes(
        body=json.dumps({'position': position, 'rotation': rotation}, indent=4), persist=False)
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
