from arena import *
from mqtt_spb_wrapper import *
import time


domain_name = "CMU Devices"
app_entity_name = "ROS1 Node"
data_topic = 'spBv1.0/CMU Devices/DDATA/ROS1 Node/ROS1Bridge'

app = MqttSpbEntityApplication(domain_name, app_entity_name)


_connected = False
while not _connected:
    print("Trying to connect to SPB broker...")
    _connected = app.connect("localhost", 1883)
    if not _connected:
        print("  Error, could not connect. Trying again in a few seconds ...")
        time.sleep(3)

JOINTMAP = {
    "yk_builder.joint.1.position": "joint_1_s",
    "yk_builder.joint.2.position": "joint_2_l",
    "yk_builder.joint.3.position": "joint_3_u",
    "yk_builder.joint.4.position": "joint_4_r",
    "yk_builder.joint.5.position": "joint_5_b",
    "yk_builder.joint.6.position": "joint_6_t",
}

scene = Scene(host="arenaxr.org", namespace="agr", scene="mill19")

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
motoman = UrdfModel(
    object_id="motoman",
    position={"x": 6.22, "y": 5.40, "z": 16.84},
    rotation={"x": -90, "y": 0, "z": 0},
    scale={"x": 1, "y": 1, "z": 1},
    url="store/users/mwfarb/xacro/motoman_gp4_support/urdf/gp4.xacro",
    urlBase="/store/users/mwfarb/xacro/motoman_gp4_support",
    persist=True,
)
motoman_sign = ArenauiCard(
    object_id="motoman_sign",
    parent=motoman.object_id,
    title="Motoman GP7 GP8",
    body="Awaiting status update...",
    position=(0, 0, 1),
    look_at="#my-camera",
    persist=True,
)


@scene.run_once
def main():
    scene.add_object(motoman)
    scene.add_object(motoman_sign)


def callback_app_message(topic, payload):
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
                mmj = []
                for joint_metric in joints_metrics:
                    name = joint_metric.get("name", "")
                    joint_name = JOINTMAP[name]
                    mmj.append(
                        f"{joint_name}:{math.degrees(joint_metric.get('value', 0))}"
                    )
                motoman.update_attributes(joints=", ".join(mmj), persist=False)
                scene.update_object(motoman)
                motoman_sign.update_attributes(
                    body="\n".join(mmj).replace(":", "\t"), persist=False
                )
                scene.update_object(motoman_sign)


# Set callbacks
app.on_message = callback_app_message

# start tasks
scene.run_tasks()
