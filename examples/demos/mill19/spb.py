import asyncio
import threading
import time

import numpy as np
from mqtt_spb_wrapper import *

from arena import *

domain_name = "Mill-19"
app_entity_name = "Mezzanine-Lab"
data_topic = "spBv1.0/Mill-19/DDATA/Mezzanine-Lab/"

JOINTMAP = {
    "DATA/joint_states/position/joint_1": "joint_1_s",
    "DATA/joint_states/position/joint_2": "joint_2_l",
    "DATA/joint_states/position/joint_3": "joint_3_u",
    "DATA/joint_states/position/joint_4": "joint_4_r",
    "DATA/joint_states/position/joint_5": "joint_5_b",
    "DATA/joint_states/position/joint_6": "joint_6_t",
}


scene = Scene(host="arenaxr.org", namespace="public", scene="mill19-mezzlab")

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
mo = (0, -0.66, 0)
# mo = (0, -10, 0)


# ########### moto_arch ##########
moto_arch = UrdfModel(
    object_id="yk_architect",
    # position=(7, 6.40, 16.25),
    position=(0 + mo[0], 0.66 + mo[1], -0.45 + mo[2]),
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
    widthScale=0.33,
)

# ########### creator ##########
moto_creator = UrdfModel(
    object_id="yk_creator",
    # position=(7, 6.40, 16.25),
    position=(-1 + mo[0], 0.66 + mo[1], -0.45 + mo[2]),
    # rotation=(-90, 180, 0),
    rotation=(-90, -90, 0),
    scale=(0.8, 0.8, 0.8),
    url="store/users/mwfarb/xacro/motoman_gp4_support/urdf/gp4.xacro",
    urlBase="/store/users/mwfarb/xacro/motoman_gp4_support",
    persist=True,
    visible=True,
    hide_on_enter_ar=True,
)
moto_creator_sign = ArenauiCard(
    object_id="moto_creator_sign",
    parent=moto_creator.object_id,
    title="Motoman Creator",
    body="Awaiting status update...",
    position=(-0.25, 0, 1.5),
    look_at="#my-camera",
    persist=True,
    widthScale=0.33,
)

# ########### builder ##########
moto_builder = UrdfModel(
    object_id="yk_builder",
    # position=(7, 6.40, 16.25),
    position=(-1 + mo[0], 0.66 + mo[1], 0.4 + mo[2]),
    # rotation=(-90, 180, 0),
    rotation=(-90, 90, 0),
    scale=(0.8, 0.8, 0.8),
    url="store/users/mwfarb/xacro/motoman_gp4_support/urdf/gp4.xacro",
    urlBase="/store/users/mwfarb/xacro/motoman_gp4_support",
    persist=True,
    visible=True,
    hide_on_enter_ar=True,
)
moto_builder_sign = ArenauiCard(
    object_id="moto_builder_sign",
    parent=moto_builder.object_id,
    title="Motoman Builder",
    body="Awaiting status update...",
    position=(-0.25, 0, 1.5),
    look_at="#my-camera",
    persist=True,
    widthScale=0.33,
)


# ########### moto_dest ##########
moto_dest_base = Object(
    object_id="moto_dest_base",
    # position=(6.22, 6.40, 16.25},
    position=(0 + mo[0], 0.66 + mo[1], 0.4 + mo[2]),
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
    object_id="yk_destroyer",
    parent="moto_dest_base",
    position=(0, 0, 0),
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
    widthScale=0.33,
)

# ########### dest sensor ##########
moto_dest_sensor = Sphere(
    object_id="moto_dest_sensor",
    # parent=moto_dest.object_id,
    # position=(.2, .2, 0),
    position=(0 + mo[0], 0.66 + mo[1], 0.4 + mo[2]),
    scale=(0.1, 0.1, 0.1),
    material={"color": "#00ff00"},
    clickable=True,
    persist=True,
    remote_render={"enabled": False},
)

# ########### arch sensor ##########
moto_architect_sensor = Sphere(
    object_id="moto_architect_sensor",
    # parent=moto_dest.object_id,
    # position=(.2, .2, 0),
    position=(0 + mo[0], 0.66 + mo[1], -0.45 + mo[2]),
    scale=(0.1, 0.1, 0.1),
    material={"color": "#00ff00"},
    clickable=True,
    persist=True,
    remote_render={"enabled": False},
)

# ########### creat sensor ##########
moto_creator_sensor = Sphere(
    object_id="moto_creator_sensor",
    # parent=moto_dest.object_id,
    # position=(.2, .2, 0),
    position=(-1 + mo[0], 0.66 + mo[1], -0.45 + mo[2]),
    scale=(0.1, 0.1, 0.1),
    material={"color": "#00ff00"},
    clickable=True,
    persist=True,
    remote_render={"enabled": False},
)

# ########### build sensor ##########
moto_builder_sensor = Sphere(
    object_id="moto_builder_sensor",
    # parent=moto_dest.object_id,
    # position=(.2, .2, 0),
    position=(-1 + mo[0], 0.66 + mo[1], 0.4 + mo[2]),
    scale=(0.1, 0.1, 0.1),
    material={"color": "#00ff00"},
    clickable=True,
    persist=True,
    remote_render={"enabled": False},
)

signs = {
    "yk_destroyer": moto_dest_sign,
    "yk_architect": moto_arch_sign,
    "yk_creator": moto_creator_sign,
    "yk_builder": moto_builder_sign,
}

robots = {
    "yk_destroyer": moto_dest,
    "yk_architect": moto_arch,
    "yk_creator": moto_creator,
    "yk_builder": moto_builder,
}

force_spheres = {
    "yk_destroyer": moto_dest_sensor,
    "yk_architect": moto_architect_sensor,
    "yk_creator": moto_creator_sensor,
    "yk_builder": moto_builder_sensor,
}


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
    widthScale=0.5,
)


# ########### INIT ##########
@scene.run_once
def main():
    scene.add_object(moto_dest_base)
    for o in (
        list(robots.values()) + list(signs.values()) + list(force_spheres.values())
    ):
        scene.add_object(o)
    scene.add_object(mp400_base)
    scene.add_object(mp400)
    scene.add_object(mp400_sign)
    scene.add_object(table)
    for wp in wps:
        scene.add_object(
            Sphere(scale=(0.1, 0.1, 0.1), position=wp, remote_render={"enabled": False})
        )


@scene.run_forever(interval_ms=100)
def update_mp400():
    global duration_s
    t = time.time()
    # move mp400 along floor
    sec = t % duration_s
    ratio, wp1, wp2 = pos_by_time(sec)
    xp = [0, 1]

    x = np.interp(ratio, xp, [wps[wp1][0], wps[wp2][0]])
    y = np.interp(ratio, xp, [wps[wp1][1], wps[wp2][1]])
    z = np.interp(ratio, xp, [wps[wp1][2], wps[wp2][2]])
    position = (x, y, z)
    mp400_base.update_attributes(
        position=position,
        look_at=f"{wps[wp2][0]} {wps[wp2][1]} {wps[wp2][2]}",
        persist=False,
    )
    scene.update_object(mp400_base)
    mp400_sign.update_attributes(
        body=json.dumps({"position": position}, indent=4), persist=False
    )
    scene.update_object(mp400_sign)


def force_rgb(n):
    # Calculate the red and green components
    r = int((n / 100) * 255)
    g = int((1 - (n / 100)) * 255)

    # Return the RGB color as a hex string
    return f"#{r:02X}{g:02X}00"


def start_spb_listener(loop):
    app = MqttSpbEntityApplication(domain_name, app_entity_name)
    _connected = False
    while not _connected:
        print("Trying to connect to SPB broker...")
        _connected = app.connect("localhost", 1883)
        if not _connected:
            print("  Error, could not connect. Trying again in a few seconds ...")
            time.sleep(3)
        else:
            print("Connected to SPB broker.")

    last_joints = {
        "yk_destroyer": "",
        "yk_architect": "",
        "yk_creator": "",
        "yk_builder": "",
    }
    last_forces = {
        "yk_destroyer": 0,
        "yk_architect": 0,
        "yk_creator": 0,
        "yk_builder": 0,
    }

    async def async_update_attrs(obj, **kwargs):
        obj.update_attributes(**kwargs)

    async def async_update_objs(objs):
        scene.update_objects(objs)

    # ########### MQTT motoman Bridge ##########
    def callback_app_message(topic, payload):
        str_topic = str(topic)
        if str_topic.startswith(data_topic):
            robot_name = str_topic.split("/")[-1]
            if robot_name not in robots:
                return
            metrics = payload.get("metrics", [])
            updates = []
            if metrics:
                joints_metrics = [
                    m for m in metrics if "joint_states/position" in m.get("name", "")
                ]
                if joints_metrics:
                    joints = []
                    for joint_metric in joints_metrics:
                        name = joint_metric.get("name", "")
                        joint_name = JOINTMAP[name]
                        joints.append(
                            f"{joint_name}:{math.degrees(joint_metric.get('value', 0)):.3f}"
                        )

                    str_joints = ", ".join(joints)
                    if len(joints) > 0 and str_joints != last_joints[robot_name]:
                        last_joints[robot_name] = str_joints
                        asyncio.run_coroutine_threadsafe(
                            async_update_attrs(robots[robot_name], joints=str_joints),
                            loop,
                        )
                        asyncio.run_coroutine_threadsafe(
                            async_update_attrs(
                                signs[robot_name],
                                body="\n".join(joints).replace(":", "\t"),
                            ),
                            loop,
                        )

                        updates.append(signs[robot_name])
                        updates.append(robots[robot_name])
                force_metrics = [m for m in metrics if "force" in m.get("name", "")]
                if force_metrics:
                    forces = []
                    for m in force_metrics:
                        forces.append(m.get("value", 0))
                    force_mag = round(np.linalg.norm(forces), 0)
                    if force_mag != last_forces[robot_name]:
                        last_forces[robot_name] = force_mag
                        asyncio.run_coroutine_threadsafe(
                            async_update_attrs(
                                force_spheres[robot_name],
                                material={"color": force_rgb(force_mag)},
                            ),
                            loop,
                        )
                        updates.append(force_spheres[robot_name])
            if len(updates) > 0:
                asyncio.run_coroutine_threadsafe(async_update_objs(updates), loop)

    app.on_message = callback_app_message


@scene.run_once
def setup_spb():
    loop = asyncio.get_running_loop()
    # Start MQTT listener on a separate thread
    mqtt_thread = threading.Thread(target=start_spb_listener, args=(loop,))
    mqtt_thread.start()


scene.run_tasks()
