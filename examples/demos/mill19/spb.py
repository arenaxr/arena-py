from arena import *
from mqtt_spb_wrapper import *
import time


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


# {"object_id":"motoman","persist":true,"type":"object","action":"update","data":{"object_type":"urdf-model","url":"store/users/mwfarb/xacro/motoman_gp4_support/urdf/gp4.xacro","urlBase":"/store/users/mwfarb/xacro/motoman_gp4_support","position":{"x":6.22109,"y":5.30667,"z":16.84618},"rotation":{"w":0.707,"x":-0.707,"y":0,"z":0},"scale":{"x":1,"y":1,"z":1}}}
moto_arch = UrdfModel(
    object_id="moto_arch",
    # position={"x": 7, "y": 6.40, "z": 16.25},
    position={"x": 0, "y": 0.66, "z": -0.45},
    # rotation={"x": -90, "y": 180, "z": 0},
    rotation={"x": -90, "y": -90, "z": 0},
    scale={"x": 0.8, "y": 0.8, "z": 0.8},
    url="store/users/mwfarb/xacro/motoman_gp4_support/urdf/gp4.xacro",
    urlBase="/store/users/mwfarb/xacro/motoman_gp4_support",
    persist=True,
)
moto_arch_sign = ArenauiCard(
    object_id="moto_arch_sign",
    parent=moto_arch.object_id,
    title="Motoman Architect",
    body="Awaiting status update...",
    position=(-0.25, 0, 1),
    look_at="#my-camera",
    persist=True,
    widthScale=0.5,
)

moto_dest = UrdfModel(
    object_id="moto_dest",
    # position={"x": 6.22, "y": 6.40, "z": 16.25},
    position={"x": 0, "y": 0.66, "z": 0.4},
    # rotation={"x": -90, "y": 0, "z": 0},
    rotation={"x": -90, "y": 90, "z": 0},
    scale={"x": 0.8, "y": 0.8, "z": 0.8},
    url="store/users/mwfarb/xacro/motoman_gp4_support/urdf/gp4.xacro",
    urlBase="/store/users/mwfarb/xacro/motoman_gp4_support",
    persist=True,
)
moto_dest_sign = ArenauiCard(
    object_id="moto_dest_sign",
    parent=moto_dest.object_id,
    title="Motoman Destroyer",
    body="Awaiting status update...",
    position=(-0.25, 0, 1),
    look_at="#my-camera",
    persist=True,
    widthScale=0.5,
)


@scene.run_once
def main():
    scene.add_object(moto_arch)
    scene.add_object(moto_arch_sign)
    scene.add_object(moto_dest)
    scene.add_object(moto_dest_sign)


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
                    moto_arch_sign.update_attributes(body="\n".join(mmj_arch).replace(":", "\t"))
                    updates.append(moto_arch_sign)

                if len(mmj_dest) > 0 and str_mmj_dest != last_dest:
                    last_dest = str_mmj_dest
                    moto_dest.update_attributes(joints=str_mmj_dest)
                    updates.append(moto_dest)
                    moto_dest_sign.update_attributes(body="\n".join(mmj_dest).replace(":", "\t"))
                    updates.append(moto_dest_sign)

                scene.update_objects(updates)


# Set callbacks
app.on_message = callback_app_message

# start tasks
scene.run_tasks()
