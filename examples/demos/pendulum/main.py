import random
import time

import numpy as np
from BoschPendulum import ArenaBoschPendulum
from pendulum_physical import PendulumPhysical
from utils import *

from arena import *

scene = Scene(host="arenaxr.org", namespace = "johnchoi", scene="pendulum")

VERBOSE = False

grabbing = False
grabber = None
child_pose_relative_to_parent = None

orig_position = (0,1.42,0)
orig_scale = (1.0,1.0,1.0)
grabbed_scale = (1.1,1.1,1.1)

USE_REAL_PENDULUM = False
pendulum = None
if(USE_REAL_PENDULUM):
    pendulum = PendulumPhysical()

BPsimulation = ArenaBoschPendulum(scene, Position(0,0,-1), Rotation(0,0,0), Scale(1,1,1))

def box_click(scene, evt, msg):
    global chasis
    global grabbing
    global grabber
    global orig_scale
    global child_pose_relative_to_parent

    if evt.type == "mousedown":
        clicker = scene.users[evt.object_id]
        handRight = clicker.hands.get("handRight", None)
        # handLeft = clicker.hands.get("handLeft", None)

        if not grabbing:
            if(VERBOSE):
                print("grabbed")

            if handRight is not None:
                grabber = handRight
                #if(VERBOSE):
                    #print("Grabber: ",grabber)

                grabbing = True
                hand_pose = pose_matrix(grabber.data.position, grabber.data.rotation)
                child_pose = pose_matrix(chasis.data.position, chasis.data.rotation)
                child_pose_relative_to_parent = get_relative_pose_to_parent(hand_pose, child_pose)

    elif evt.type == "mouseup":
        if grabbing:
            if(VERBOSE):
                print("released")
            grabbing = False
            chasis.update_attributes(scale=orig_scale)
            scene.update_object(chasis)

chasis = Box(
    object_id="chasis",

    position=orig_position,
    scale=orig_scale,
    rotation=(1,0,0,0),

    width = 0.34,
    height = 0.29,
    depth = 0.26,

    material = Material(color=Color(50,60,200), opacity=0.2, transparent=True, visible=False),

    parent=BPsimulation.root,
    clickable=True,
    evt_handler=box_click
)

arm = Box(
    object_id="arm",

    position=(0,0,0),
    scale=(1,1,1),
    rotation=(1,0,0,0),

    width = 0.05,
    height = 0.7,
    depth = 0.05,

    material = Material(color=Color(50,100,100), opacity=0.2, transparent=True, visible=False),

    parent=chasis,
    clickable=True,
    evt_handler=box_click
)

@scene.run_forever(interval_ms=50)
def move_box():
    global pendulum
    global chasis
    global grabber
    global grabbed_scale
    global child_pose_relative_to_parent

    if grabber is not None and child_pose_relative_to_parent is not None and grabbing:
        hand_pose = pose_matrix(grabber.data.position, grabber.data.rotation)
        new_pose = get_world_pose_when_parented(hand_pose, child_pose_relative_to_parent)


        newPoseX = BPsimulation._clamp(new_pose[0,3], -.15, .15)

        new_position = (newPoseX, orig_position[1], orig_position[2])
        new_rotation = Utils.matrix3_to_quat(new_pose[:3,:3])
        new_rotation = (new_rotation[3], new_rotation[0], new_rotation[1], new_rotation[2])
        if(VERBOSE):
            print("New pos ",new_position[0]) # Virtual position

        if(USE_REAL_PENDULUM):
            pendulum.set_position(new_position[0])

        chasis.update_attributes(position=new_position, scale=grabbed_scale)#, rotation=new_rotation)
        scene.update_object(chasis)
        if(VERBOSE):
            print("Finished move box update")

        BPsimulation.SetChassisPosition(new_position[0])

@scene.run_forever(interval_ms=100)
def update_pendulum():
    global pendulum
    global arm

    BPsimulation.pendulumTimer = BPsimulation.pendulumTimer + 100
    theta_rad = BPsimulation.pendulumTimer * 0.0001
    if(USE_REAL_PENDULUM):
        theta_rad = pendulum.get_rotation()

    if theta_rad is not None:
        theta_deg = np.degrees(theta_rad)

        arm.update_attributes(rotation=(0,0,theta_deg))
        scene.update_object(chasis)

        BPsimulation.SetPendulumRotationDegrees(theta_deg)

@scene.run_once
def make_objects():

    global pendulum

    if(USE_REAL_PENDULUM):
        pendulum.set_position(0)

    scene.add_object(chasis)
    scene.add_object(arm)

# @scene.run_async
# async def update_pendulum():
#     while True:
#         pendulum.set_position(.07)
#         await scene.sleep(1000)
#         pendulum.set_position(-.07)
#         await scene.sleep(1000)

if __name__ == "__main__":
    scene.run_tasks()
