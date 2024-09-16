import asyncio
import math
import threading
import time

import numpy as np
from mqtt_spb_wrapper import *

from arena import *

domain_name = "CMU Devices"
app_entity_name = "ROS1 Node"
data_topic = "spBv1.0/CMU Devices/DDATA/ROS1 Node/ROS1Bridge"

app = MqttSpbEntityApplication(domain_name, app_entity_name)


_connected = False
while not _connected:
    print("Trying to connect to SPB broker...")
    _connected = app.connect("wiselambda1.andrew.local.cmu.edu", 1883)
    if not _connected:
        print("  Error, could not connect. Trying again in a few seconds ...")
        time.sleep(3)

JOINTMAP = {
    "yk_destroyer.joint.1.position": "joint_1_s",
    "yk_destroyer.joint.2.position": "joint_2_l",
    "yk_destroyer.joint.3.position": "joint_3_u",
    "yk_destroyer.joint.4.position": "joint_4_r",
    "yk_destroyer.joint.5.position": "joint_5_b",
    "yk_destroyer.joint.6.position": "joint_6_t",
    "yk_architect.joint.1.position": "joint_1_s",
    "yk_architect.joint.2.position": "joint_2_l",
    "yk_architect.joint.3.position": "joint_3_u",
    "yk_architect.joint.4.position": "joint_4_r",
    "yk_architect.joint.5.position": "joint_5_b",
    "yk_architect.joint.6.position": "joint_6_t",
}

scene = Scene(host="arenaxr.org", namespace="public", scene="mill19-mezzlab")

# motoman joints
mmjoints = {
    # 'base_link-base', # limit: {lower: 0, upper: 0}, fixed
    # 'flange-tool0', # limit: {lower: 0, upper: 0}, fixed
    # revolute
    "joint_1_s": {"limit": {"lower": -2.9670597283903604, "upper": 2.9670597283903604}},
    # revolute
    "joint_2_l": {"limit": {"lower": -1.9198621771937625, "upper": 2.2689280275926285}},
    # revolute
    "joint_3_u": {"limit": {"lower": -1.1344640137963142, "upper": 3.490658503988659}},
    # revolute
    "joint_4_r": {"limit": {"lower": -3.490658503988659, "upper": 3.490658503988659}},
    # revolute
    "joint_5_b": {"limit": {"lower": -2.1467549799530254, "upper": 2.1467549799530254}},
    # revolute
    "joint_6_t": {"limit": {"lower": -7.941248096574199, "upper": 7.941248096574199}},
    # 'joint_6_t-flange', # limit: {lower: 0, upper: 0}, fixed
}


# ########### table ##########
table = Box(
    object_id="table",
    depth=1.5,
    height=1,
    width=6,
    position=(-2.5, -0.5, 0),
    material={"color": "#7f7f7f"},
    material_extras={"transparentOccluder": True},
    persist=True,
    hide_on_enter_ar=False,
    hide_on_enter_vr=True,
)


# motoman robots offset
mo = (0, -.66, 0)
# mo = (0, -10, 0)


# ########### moto_arch ##########
moto_arch = UrdfModel(
    object_id="moto_arch",
    # position=(7, 6.40, 16.25),
    position=(0+mo[0], 0.66+mo[1], -0.45+mo[2]),
    # rotation=(-90, 180, 0),
    rotation=(-90, -90, 0),
    scale=(0.8, 0.8, 0.8),
    url="store/users/mwfarb/xacro/motoman_gp4_support/urdf/gp4.xacro",
    urlBase="/store/users/mwfarb/xacro/motoman_gp4_support",
    persist=True,
    visible=True,
    hide_on_enter_ar=True,
)
moto_arch_sign = ArenauiCard(
    object_id="moto_arch_sign",
    parent=moto_arch.object_id,
    title="Motoman Architect",
    body="Awaiting status update...",
    position=(-0.25, 0, 1.5),
    look_at="#my-camera",
    persist=True,
    widthScale=0.5,
)

# ########### moto_dest ##########
moto_dest_base = Object(
    object_id="moto_dest_base",
    # position=(6.22, 6.40, 16.25},
    position=(0+mo[0], 0.66+mo[1], 0.4+mo[2]),
    scale=(0.8, 0.8, 0.8),
    animation=None,
    # animation={
    #     "property": "rotation",
    #     "from": "0 0 0",
    #     "to": "0 360 0",
    #     "loop": True,
    #     "dur": 20000,
    #     "easing": "linear"
    # },
    persist=True,
)
moto_dest = UrdfModel(
    object_id="moto_dest",
    parent="moto_dest_base",
    # rotation=(-90, 0, 0),
    rotation=(-90, 90, 0),
    scale=(1, 1, 1),
    url="store/users/mwfarb/xacro/motoman_gp4_support/urdf/gp4.xacro",
    urlBase="/store/users/mwfarb/xacro/motoman_gp4_support",
    persist=True,
    visible=True,
    hide_on_enter_ar=True,
)
moto_dest_sign = ArenauiCard(
    object_id="moto_dest_sign",
    parent=moto_dest.object_id,
    title="Motoman Destroyer",
    body="Awaiting status update...",
    position=(0, 0, 1.5),
    look_at="#my-camera",
    persist=True,
)

# ########### moto_dest sensor ##########
moto_dest_sensor = Sphere(
    object_id="moto_dest_sensor",
    # parent=moto_dest.object_id,
    # position=(.2, .2, 0),
    position=(-.1, 0, .1),
    scale=(.1, .1, .1),
    material={"color": "#00ff00", "opacity": 0},
    clickable=True,
    persist=True,
    remote_render={"enabled": False},
)


def sensor_on_callback(scene, evt, msg):
    sensor_animate(scene, evt, "#00ff00", "#ff0000", 1500)
    moto_dest_sensor.update_attributes(material={
        "color": "#00ff00",
        "opacity": .5,
    })
    scene.update_object(moto_dest_sensor)


def sensor_off_callback(scene, evt, msg):
    sensor_animate(scene, evt, "#ff0000", "#00ff00", 500)
    moto_dest_sensor.update_attributes(material={
        "color": "#00ff00",
        "opacity": 0,
    })
    scene.update_object(moto_dest_sensor)


def sensor_animate(scene, evt, start, end, dur):
    global moto_dest_sensor
    if evt.type == "mousedown":
        # moto_dest_sensor.update_attributes(visible=True)
        # scene.update_object(moto_dest_sensor)

        moto_dest_sensor.update_attributes(
            # animation={
            #     "property": "components.material.material.color",
            #     "type": "color",
            #     "from": start,
            #     "to": end,
            #     "dur": dur,
            #     # "easings": "easeInOutBounce",
            #     "loop": "once",
            #     "autoplay": True,
            # },
            material={
                "color": "#00ff00",
                "opacity": .5,
            },
        )
        scene.update_object(moto_dest_sensor)

        # await asyncio.sleep(2)
        # moto_dest_sensor.update_attributes(visible=False)
        # scene.update_object(moto_dest_sensor)


moto_dest_on = Box(
    object_id="moto_dest_on",
    position=((0 - 4), 0.66, 0.4),
    # position=((6.22 - 4), 6.40, 16.25),
    scale=(.1, .1, .1),
    material={"color": "#00ff00"},
    evt_handler=sensor_on_callback,
    clickable=True,
    persist=True,
    remote_render={"enabled": False},
)
moto_dest_off = Box(
    object_id="moto_dest_off",
    position=((0 - 4.1), 0.66, 0.4),
    # position=((6.22 - 4.1), 6.40, 16.25),
    scale=(.1, .1, .1),
    material={"color": "#ff0000"},
    evt_handler=sensor_off_callback,
    clickable=True,
    persist=True,
    remote_render={"enabled": False},
)

# ########### AMR MP400 ##########
# (5.20, 4.60, 17.90),
# (5.20, 4.60, 12.90),
# (7.95, 4.60, 12.90),
# (7.95, 4.60, 17.90),

x1, x2 = 1.1, -3
y1 = -1
z1, z2 = -2, 1.5
duration_s = 10
wps = [
    (x1, y1, z1),
    (x1, y1, z2),
    (x2, y1, z2),
    (x2, y1, z1),
]
dist_total = 0.0
for i, wp in enumerate(wps):
    wp1 = i
    if i == len(wps) - 1:
        wp2 = 0
    else:
        wp2 = i + 1
    dist_total = dist_total + math.dist(np.array(wps[wp1]), np.array(wps[wp2]))


def pos_by_time(sec: float):
    global wps, duration_s, dist_total
    ratio_total = sec / duration_s
    dist_total_target = ratio_total * dist_total
    ratio = 1.0
    dist = 0.0
    for i, wp in enumerate(wps):
        wp1 = i
        if i == len(wps) - 1:
            wp2 = 0
        else:
            wp2 = i + 1
        dist_seg = math.dist(np.array(wps[wp1]), np.array(wps[wp2]))

        if (dist + dist_seg) < dist_total_target:
            dist = dist + dist_seg
        else:
            ratio = (dist_total_target - dist) / dist_seg
            break
    # return ratio of the current segment
    return ratio, wp1, wp2


mp400_base = Object(
    object_id="mp400_base",
    position=wps[0],
    # position=(1.1, -1, -2),
    rotation=(0, 90, 0),
    scale=(1, 1, 1),
    persist=True,
)
mp400 = UrdfModel(
    object_id="mp400",
    parent="mp400_base",
    position=(0, 0, 0),
    rotation=(-90, 270, 0),
    scale=(1, 1, 1),
    url="store/users/mwfarb/xacro/neo_mp_400/robot_model/mp_400/mp_400.urdf.xacro",
    urlBase="/store/users/mwfarb/xacro/neo_mp_400",
    persist=True,
    visible=True,
)
mp400_sign = ArenauiCard(
    object_id="mp400_sign",
    title="Autonomous Mobile Robot (AMR) MP-400",
    body="Awaiting status update...",
    position=(wps[0][0], wps[0][1] + 2, wps[0][2]),
    look_at="#my-camera",
    persist=True,
)


# ########### INIT ##########
@ scene.run_once
def main():
    scene.add_object(moto_arch)
    scene.add_object(moto_arch_sign)
    scene.add_object(moto_dest_base)
    scene.add_object(moto_dest)
    scene.add_object(moto_dest_sensor)
    scene.add_object(moto_dest_sign)
    scene.add_object(moto_dest_on)
    scene.add_object(moto_dest_off)
    scene.add_object(mp400_base)
    scene.add_object(mp400)
    scene.add_object(mp400_sign)
    scene.add_object(table)
    for wp in wps:
        scene.add_object(
            Sphere(scale=(.1, .1, .1), position=wp, remote_render={"enabled": False}))


@ scene.run_forever(interval_ms=100)
def update_mp400():
    global duration_s
    t = time.time()
    # move mp400 along floor
    sec = (t % duration_s)
    ratio, wp1, wp2 = pos_by_time(sec)
    xp = [0, 1]

    x = np.interp(ratio, xp, [wps[wp1][0], wps[wp2][0]])
    y = np.interp(ratio, xp, [wps[wp1][1], wps[wp2][1]])
    z = np.interp(ratio, xp, [wps[wp1][2], wps[wp2][2]])
    position = (x, y, z)
    mp400_base.update_attributes(
        position=position,
        look_at=f"{wps[wp2][0]} {wps[wp2][1]} {wps[wp2][2]}",
        persist=False
    )
    scene.update_object(mp400_base)
    mp400_sign.update_attributes(
        body=json.dumps({'position': position}, indent=4), persist=False)
    scene.update_object(mp400_sign)


# ########### MQTT motoman Bridge ##########

last_arch = ""
last_dest = ""


def callback_app_message(topic, payload):
    global last_arch
    global last_dest
    if str(topic) == data_topic:
        metrics = payload.get("metrics", [])
        if metrics:
            joints_metrics = [
                m
                for m in metrics
                if (
                    "joint" in m.get("name", "")
                    and m.get("name", "").endswith("position")
                )
            ]
            if joints_metrics:
                mmj_arch = []
                mmj_dest = []
                for joint_metric in joints_metrics:
                    name = joint_metric.get("name", "")
                    joint_name = JOINTMAP[name]
                    if name.startswith("yk_architect"):
                        mmj_arch.append(
                            f"{joint_name}:{math.degrees(joint_metric.get('value', 0))}"
                        )
                    elif name.startswith("yk_destroyer"):
                        mmj_dest.append(
                            f"{joint_name}:{math.degrees(joint_metric.get('value', 0))}"
                        )
                updates = []
                str_mmj_arch = ", ".join(mmj_arch)
                str_mmj_dest = ", ".join(mmj_dest)
                if len(mmj_arch) > 0 and str_mmj_arch != last_arch:
                    last_arch = str_mmj_arch
                    moto_arch.update_attributes(joints=str_mmj_arch)
                    updates.append(moto_arch)
                    moto_arch_sign.update_attributes(
                        body="\n".join(mmj_arch).replace(":", "\t"))
                    updates.append(moto_arch_sign)

                if len(mmj_dest) > 0 and str_mmj_dest != last_dest:
                    last_dest = str_mmj_dest
                    moto_dest.update_attributes(joints=str_mmj_dest)
                    updates.append(moto_dest)
                    moto_dest_sign.update_attributes(
                        body="\n".join(mmj_dest).replace(":", "\t"))
                    updates.append(moto_dest_sign)

                scene.update_objects(updates)


# Set callbacks
app.on_message = callback_app_message

# start tasks
scene.run_tasks()
