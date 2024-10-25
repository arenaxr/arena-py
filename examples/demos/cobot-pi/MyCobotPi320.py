import math
import os
import random
import sys
import time

import serial
import serial.tools.list_ports
from pymycobot.genre import Angle, Coord
from pymycobot.mycobot import MyCobot

from arena import *

#------MAKE ROBOT ARM------#
USE_ROBOT = False

if(USE_ROBOT):
    #myCobot = MyCobot(port = "/dev/cu.usbserial-023EDC85", baudrate = 115200, debug=True)
    myCobot = MyCobot(port = "/dev/ttyAMA0", baudrate = 115200, debug=True)
    myCobot.send_angles([0,0,0,0,0,0], 50) #reset pose
    myCobot.set_color(0,255,0)
    myCobot.set_gripper_value(99, 80)

#------MAKE CONNECT TO ARENA------#
#scene = Scene(host="mqtt.arenaxr.org", namespace = "johnchoi", scene="MyCobotPi320")
scene = Scene(host="arenaxr.org", namespace = "public", scene="arena")

#------MAKE ROBOT ARM------#
MyCobotPi_Base = Box(
    object_id = "MyCobotPi_Base",
    position = (-2, 0.8, -3),
    rotation = (0,0,0),
    material = Material(opacity = 0.0, transparent = True, visible = False),
    persist = True
)
MyCobotPi_J0 = GLTF(
    object_id="MyCobotPi_J0",
    url="/store/users/johnchoi/MyCobotPi/MyCobotPi_J0/MyCobotPi_J0.gltf",
    position=(0,0,0),
    rotation=(0,90,0),
    scale=(1,1,1),
    parent = MyCobotPi_Base,
    persist=True
)
MyCobotPi_J1 = GLTF(
    object_id="MyCobotPi_J1",
    url="/store/users/johnchoi/MyCobotPi/MyCobotPi_J1/MyCobotPi_J1.gltf",
    position=(0,0,0),
    rotation=(0,0,0),
    scale=(1,1,1),
    parent=MyCobotPi_J0,
    persist=True
)
MyCobotPi_J2 = GLTF(
    object_id="MyCobotPi_J2",
    url="/store/users/johnchoi/MyCobotPi/MyCobotPi_J2/MyCobotPi_J2.gltf",
    position=(0,0.1433,0),
    rotation=(0,0,0),
    scale=(1,1,1),
    parent=MyCobotPi_J1,
    persist=True
)
MyCobotPi_J3 = GLTF(
    object_id="MyCobotPi_J3",
    url="/store/users/johnchoi/MyCobotPi/MyCobotPi_J3/MyCobotPi_J3.gltf",
    position=(0,0.1075,0),
    rotation=(0,0,0),
    scale=(1,1,1),
    parent=MyCobotPi_J2,
    persist=True
)
MyCobotPi_J4 = GLTF(
    object_id="MyCobotPi_J4",
    url="/store/users/johnchoi/MyCobotPi/MyCobotPi_J4/MyCobotPi_J4.gltf",
    position=(0,0.09710006,0),
    rotation=(0,0,0),
    scale=(1,1,1),
    parent=MyCobotPi_J3,
    persist=True
)
MyCobotPi_J5 = GLTF(
    object_id="MyCobotPi_J5",
    url="/store/users/johnchoi/MyCobotPi/MyCobotPi_J5/MyCobotPi_J5.gltf",
    position=(0.06340005,0,0),
    rotation=(0,0,0),
    scale=(1,1,1),
    parent=MyCobotPi_J4,
    persist=True
)
MyCobotPi_J6 = GLTF(
    object_id="MyCobotPi_J6",
    url="/store/users/johnchoi/MyCobotPi/MyCobotPi_J6/MyCobotPi_J6.gltf",
    position=(0,0.07610026,0),
    rotation=(0,0,0),
    scale=(1,1,1),
    parent=MyCobotPi_J5,
    persist=True
)

#------MAKE BUTTON FUNCTIONS ------#
def rotateMyCobot(angles):
    if(len(angles) != 6):
        print("Error: angles must have exactly 6 values. Ignoring!")
        return
    #update arena virtual robot
    MyCobotPi_J1.update_attributes(rotation=Rotation(0,angles[0],0))
    MyCobotPi_J2.update_attributes(rotation=Rotation(angles[1],0,0))
    MyCobotPi_J3.update_attributes(rotation=Rotation(angles[2],0,0))
    MyCobotPi_J4.update_attributes(rotation=Rotation(angles[3],0,0))
    MyCobotPi_J5.update_attributes(rotation=Rotation(0,angles[4],0))
    MyCobotPi_J6.update_attributes(rotation=Rotation(0,0,angles[5]))
    scene.update_object(MyCobotPi_J1)
    scene.update_object(MyCobotPi_J2)
    scene.update_object(MyCobotPi_J3)
    scene.update_object(MyCobotPi_J4)
    scene.update_object(MyCobotPi_J5)
    scene.update_object(MyCobotPi_J6)
    #update real robot
    if(USE_ROBOT):
        myCobot.send_angles(angles, 50)
    print("::send_angles() ==> angles {}, speed 100\n".format(angles))

def setMyCobotColor(r,g,b):
    #update arena virtual robot
    randomColorObject.update_attributes(color=(r,g,b,))
    scene.update_object(randomColorObject)
    #update real robot
    if(USE_ROBOT):
        myCobot.set_color(r,g,b)
    print("::set_color() ==> color {}\n".format("255 255 0"))

def randomColorButton_handler():
    print("Random Color Button pressed!")
    r = random.randrange(0, 255)
    g = random.randrange(0, 255)
    b = random.randrange(0, 255)
    setMyCobotColor(r,g,b)

def randomAngleButton_handler():
    print("Random Angle Button pressed!")
    maxAngle = 80
    j1 = random.uniform(-maxAngle,maxAngle)
    j2 = random.uniform(-maxAngle,maxAngle)
    j3 = random.uniform(-maxAngle,maxAngle)
    j4 = random.uniform(-maxAngle,maxAngle)
    j5 = random.uniform(-maxAngle,maxAngle)
    j6 = random.uniform(-maxAngle,maxAngle)
    rotateMyCobot([j1,j2,j3,j4,j5,j6])

def resetAngleButton_handler():
    print("Reset Button pressed!")
    rotateMyCobot([0,0,0,0,0,0])

def cobotButtonPanelHandler(_scene, evt, _msg):
    if evt.type == "buttonClick":
        buttonName = evt.data.buttonName
        if buttonName == "Goto random angle":
            randomAngleButton_handler()
        elif buttonName == "Reset angle":
            resetAngleButton_handler()
        elif buttonName == "Set random color":
            randomColorButton_handler()

def jointIncrementHandler(scene, evt, msg):
    if evt.type == "buttonClick":
        buttonName = evt.data.buttonName
        print("Joint (" + buttonName + ") Button pressed!")
        jointNum = int( buttonName[1] )

        increment = 0
        if(buttonName[2] == "+"):
            increment = 10
        elif(buttonName[2] == "-"):
            increment = -10

        if(USE_ROBOT):
            currAngles = myCobot.get_angles()
            currAngles[jointNum-1] = currAngles[jointNum-1] + increment
            rotateMyCobot(currAngles)

def updateJointData():
    if(USE_ROBOT):
        angles = myCobot.get_angles()

        j1 = "{:07.2f}".format(angles[0])
        j2 = "{:07.2f}".format(angles[1])
        j3 = "{:07.2f}".format(angles[2])
        j4 = "{:07.2f}".format(angles[3])
        j5 = "{:07.2f}".format(angles[4])
        j6 = "{:07.2f}".format(angles[5])

        jointDataText.data.text = j1+"\n"+j2+"\n"+j3+"\n"+j4+"\n"+j5+"\n"+j6
        scene.update_object(jointDataText)

        print(jointDataText.data.text)

#------MAKE BUTTON PANELS ------#

buttonPanel = ButtonPanel(
    object_id="cobotButtons",

    title="Cobot Control",
    buttons=["Goto random angle", "Reset angle", "Set random color"],
    font="Roboto-Mono",

    position=(0.0, 0.8, 0.0),
    rotation=(0.0,0.0,0.0),
    scale=(0.5,0.5,0.5),

    evt_handler=cobotButtonPanelHandler,
    parent=MyCobotPi_Base,
    vertical=True,
    persist=True
)

jointIncrementButtons = ButtonPanel(
    object_id="jointIncrementButtons",

    buttons=[Button("J1+"),Button("J2+"),Button("J3+"),Button("J4+"),Button("J5+"),Button("J6+")],
    font="Roboto-Mono",

    position=(0.4, 0.9, 0.0),
    rotation=(0.0,0.0,0.0),
    scale=(0.5,0.5,0.5),

    evt_handler=jointIncrementHandler,
    parent=MyCobotPi_Base,
    vertical=True,
    persist=True
)

jointDecrementButtons = ButtonPanel(
    object_id="jointDecrementButtons",

    buttons=[Button("J1-"),Button("J2-"),Button("J3-"),Button("J4-"),Button("J5-"),Button("J6-")],
    font="Roboto-Mono",

    position=(0.6, 0.9, 0.0),
    rotation=(0.0,0.0,0.0),
    scale=(0.5,0.5,0.5),

    evt_handler=jointIncrementHandler,
    parent=MyCobotPi_Base,
    vertical=True,
    persist=True
)

jointDataText = Text(
    object_id="jointDataText",

    value="000.00"+"\n"+"000.00"+"\n"+"000.00"+"\n"+"000.00"+"\n"+"000.00"+"\n"+"000.00",
    color=(100,255,255),

    position=(0.9, 0.9, 0.0),
    rotation=(0.0,0.0,0.0),
    scale=(0.44,0.44,0.44),

    parent=MyCobotPi_Base,
    persist=True
)

randomColorObject = Box(
    object_id="randomColorObject",
    material = Material(color = (0,255,0), transparent = True, opacity=0.5),

    position=(-0.5, 0.8, 0.0),
    rotation=(0,0,0),
    scale=(.3,.3,.1),

    parent = MyCobotPi_Base,
    persist=True
)

#------ PROGRAM INIT/UPDATE ------#

@scene.run_once
def programStart():
    # Add myCobotPi
    scene.add_object(MyCobotPi_Base)
    scene.add_object(MyCobotPi_J0)
    scene.add_object(MyCobotPi_J1)
    scene.add_object(MyCobotPi_J2)
    scene.add_object(MyCobotPi_J3)
    scene.add_object(MyCobotPi_J4)
    scene.add_object(MyCobotPi_J5)
    scene.add_object(MyCobotPi_J6)

    # Add myCobotPi UI
    scene.add_object(buttonPanel)
    scene.add_object(jointIncrementButtons)
    scene.add_object(jointDecrementButtons)
    scene.add_object(randomColorObject)
    scene.add_object(jointDataText)

@scene.run_forever(interval_ms=500)
def updateData():
    # updating data text display and gripper text display ever second
    updateJointData()

scene.run_tasks()
