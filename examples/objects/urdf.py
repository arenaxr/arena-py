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

@scene.run_after_interval(interval_ms=1000)
def bend_joints():
    joints = []
    for i in range(6):
        joints.append(f"HP{i}:{30}")
        joints.append(f"KP{i}:{120}")
        joints.append(f"AP{i}:{-60}")

    # update joints
    athlete_model.update_attributes(joints=",".join(joints))
    scene.update_object(athlete_model)


# start tasks
scene.run_tasks()
