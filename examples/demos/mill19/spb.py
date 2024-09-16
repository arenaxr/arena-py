import asyncio
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
    # 'base_link-base',  # limit: {lower: 0, upper: 0}, fixed
    # 'flange-tool0',  # limit: {lower: 0, upper: 0}, fixed
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
    # 'joint_6_t-flange',  # limit: {lower: 0, upper: 0}, fixed
}


# ########### table ##########
table = Box(
    object_id="table",
    depth=1.5,
    height=1,
    width=6,
    position={"x": -2.5, "y": -0.5, "z": 0},
    material={"color": "#7f7f7f"},
    material_extras={"transparentOccluder": True},
    persist=True,
    hide_on_enter_ar=True,
)


# motoman robots offset
mo = (0, -.66, 0)
# mo = (0, -10, 0)


# ########### moto_arch ##########
moto_arch = UrdfModel(
    object_id="moto_arch",
    # position={"x": 7, "y": 6.40, "z": 16.25},
    position={"x": 0+mo[0], "y": 0.66+mo[1], "z": -0.45+mo[2]},
    # rotation={"x": -90, "y": 180, "z": 0},
    rotation={"x": -90, "y": -90, "z": 0},
    scale={"x": 0.8, "y": 0.8, "z": 0.8},
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
    # position={"x": 6.22, "y": 6.40, "z": 16.25},
    position={"x": 0+mo[0], "y": 0.66+mo[1], "z": 0.4+mo[2]},
    scale={"x": 0.8, "y": 0.8, "z": 0.8},
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
    # rotation={"x": -90, "y": 0, "z": 0},
    rotation={"x": -90, "y": 90, "z": 0},
    scale={"x": 1, "y": 1, "z": 1},
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
    scale={"x": .1, "y": .1, "z": .1},
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
    position={"x": (0 - 4), "y": 0.66, "z": 0.4},
    # position={"x": (6.22 - 4), "y": 6.40, "z": 16.25},
    scale={"x": .1, "y": .1, "z": .1},
    material={"color": "#00ff00"},
    evt_handler=sensor_on_callback,
    clickable=True,
    persist=True,
    remote_render={"enabled": False},
)
moto_dest_off = Box(
    object_id="moto_dest_off",
    position={"x": (0 - 4.1), "y": 0.66, "z": 0.4},
    # position={"x": (6.22 - 4.1), "y": 6.40, "z": 16.25},
    scale={"x": .1, "y": .1, "z": .1},
    material={"color": "#ff0000"},
    evt_handler=sensor_off_callback,
    clickable=True,
    persist=True,
    remote_render={"enabled": False},
)

# ########### AMR MP400 ##########
# {"x": 5.20, "y": 4.60, "z": 17.90},
# {"x": 5.20, "y": 4.60, "z": 12.90},
# {"x": 7.95, "y": 4.60, "z": 12.90},
# {"x": 7.95, "y": 4.60, "z": 17.90},
y1 = -1

x1 = 1.1
x2 = -3

z1 = -2
z2 = 1.5

wps = [
    {"x": x1, "y": y1, "z": z1},
    {"x": x1, "y": y1, "z": z2},
    {"x": x2, "y": y1, "z": z2},
    {"x": x2, "y": y1, "z": z1},

    # {"x": x1, "y": y1, "z": z2},
    # {"x": x2, "y": y1, "z": z2},
    # {"x": x2, "y": y1, "z": z2},
    # {"x": x1, "y": y1, "z": z2},
]
mp400_base = Object(
    object_id="mp400_base",
    position=wps[0],
    # position=(1.1, -1, -2),
    rotation={"x": 0, "y": 90, "z": 0},
    scale={"x": 1, "y": 1, "z": 1},
    persist=True,
)
mp400 = UrdfModel(
    object_id="mp400",
    parent="mp400_base",
    position={'x': 0, 'y': 0, 'z': 0},
    rotation={'x': -90, 'y': 270, 'z': 0},
    scale={"x": 1, "y": 1, "z": 1},
    url="store/users/mwfarb/xacro/neo_mp_400/robot_model/mp_400/mp_400.urdf.xacro",
    urlBase="/store/users/mwfarb/xacro/neo_mp_400",
    persist=True,
    visible=True,
)
mp400_sign = ArenauiCard(
    object_id="mp400_sign",
    title="Mobile Robot MP-400",
    body="Awaiting status update...",
    position=(wps[0]['x'], wps[0]['y']+2, wps[0]['z']),
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
    # scene.add_object(
    #     Sphere(scale=(.1, .1, .1), position=wps[0], remote_render={"enabled": False}))
    # scene.add_object(
    #     Sphere(scale=(.1, .1, .1), position=wps[1], remote_render={"enabled": False}))
    # scene.add_object(
    #     Sphere(scale=(.1, .1, .1), position=wps[2], remote_render={"enabled": False}))
    # scene.add_object(
    #     Sphere(scale=(.1, .1, .1), position=wps[3], remote_render={"enabled": False}))


@ scene.run_forever(interval_ms=100)
def update_mp400():
    t = time.time()
    # move mp400 along floor
    offset = math.pi
    ratio = math.sin(t + offset)
    if -1 <= ratio <= -.5:
        wp1 = 0
        wp2 = 1
        r = -180
    elif -.5 <= ratio <= 0:
        wp1 = 1
        wp2 = 2
        r = -180
    elif 0 <= ratio <= .5:
        wp1 = 2
        wp2 = 3
        r = -180
    else:
        wp1 = 3
        wp2 = 0
        r = -180
    xp = [-1+(wp1*.5), -.5+(wp1*.5)]

    x = np.interp(ratio, xp, [wps[wp1]['x'], wps[wp2]['x']])
    z = np.interp(ratio, xp, [wps[wp1]['z'], wps[wp2]['z']])
    position = {'x': x, 'y': wps[wp1]['y'], 'z': z}
    mp400_base.update_attributes(
        position=position,
        look_at=f"{wps[wp2]['x']} {wps[wp2]['y']} {wps[wp2]['z']}",
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
