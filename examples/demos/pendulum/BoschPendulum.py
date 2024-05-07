# ------------------------------------------ #
# ----------IMPORTING EVERYTHING------------ #
# ------------------------------------------ #

from ColorPrinter import *
from arena import *
import math

#FILESTORE SETTINGS
FILESTORE = "https://arenaxr.org/" #main server
FILEPATH = "store/users/johnchoi/BoschPendulum/" #Path
HEADER = "BP"
VERBOSE = False

# ------------------------------------------ #
# ------------CLASS DEFINITIONS------------- #
# ------------------------------------------ #
class ArenaBoschPendulum:
    def __init__(self, scene, position, rotation, scale):
        self.scene = scene
        #State vars
        self.doorsOpen = False
        self.chassisPosition = 0 
        self.pendulumRotation = 0 
        #Timers, only used for example loops
        self.chassisTimer = 0
        self.pendulumTimer = 0
        #Apply CLI Transform Parameters
        self.rootPosition = position
        self.rootRotation = rotation
        self.rootScale = scale
        #Initialize Root/GLB Objects
        self.CreateRoot()
        self.CreateGLBs()
        if(VERBOSE):
            printWhiteB("Bosch Pendulum initialized at position " + str(position) + ", rotation " + str(rotation) + ", and scale "+ str(scale) + ".")

    #-----------INITIALIZATION ROOT/GLB FUNCTIONS-----------#
    def CreateRoot(self):
        self.root = Box(
            object_id=HEADER+"_Root",
            material = Material(color=Color(0,255,0), opacity=0.2, transparent=True, visible=False),

            position = self.rootPosition,
            rotation = self.rootRotation,
            scale = self.rootScale,

            persist=True
        )
        self.scene.add_object(self.root)
    def CreateGLB(self, filename, _position, _rotation, _parent):
        GLBObject = GLTF(
            object_id=HEADER+"_"+filename,
            url=FILESTORE+FILEPATH+filename+".glb",
            
            position=_position,
            rotation=_rotation,
            scale=Scale(1,1,1),

            parent = _parent,
            persist=True
        )
        self.scene.add_object(GLBObject)
        return GLBObject
    def CreateGLBs(self):
        #BoschLogo
        self.BoschLogo = self.CreateGLB("BoschLogo", Position(0,1.62,0), Rotation(0,0,0), self.root)
        #PendulumMachineStatic
        self.PendulumMachineStatic = self.CreateGLB("PendulumMachineStatic", Position(0,0,0), Rotation(0,0,0), self.root)
        #Covers
        self.Cover_Front_Left  = self.CreateGLB("Cover_Front_Left", Position(-0.44,0,0), Rotation(0,0,0), self.root)
        self.Cover_Front_Right = self.CreateGLB("Cover_Front_Right", Position(0.44,0,0), Rotation(0,0,0), self.root)
        self.Cover_Back_Left   = self.CreateGLB("Cover_Back_Left", Position(-0.44,0,0), Rotation(0,0,0), self.root)
        self.Cover_Back_Right  = self.CreateGLB("Cover_Back_Right", Position(0.44,0,0), Rotation(0,0,0), self.root)
        #Doors
        self.Door_Left  = self.CreateGLB("Door_Left", Position(-0.599,0,0.2854), Rotation(0,0,0), self.root)
        self.Door_Right = self.CreateGLB("Door_Right", Position(0.599,0,0.2854), Rotation(0,0,0), self.root)
        #Chassis
        self.Chassis_Front = self.CreateGLB("Chassis_Front", Position(0,0,0), Rotation(0,0,0), self.root)
        self.Chassis_Back  = self.CreateGLB("Chassis_Back", Position(0,0,0), Rotation(0,180,0), self.root)
        #PendulumAxis
        self.PendulumAxis = self.CreateGLB("PendulumAxis", Position(0,1.526,0), Rotation(0,0,0), self.Chassis_Front)

    #-----------MOTION FUNCTIONS-----------#
    def OpenDoor(self):
        if(VERBOSE):
            printMagentaB("Doors open!")
        self.doorsOpen = True  
        self.Door_Left.dispatch_animation(Animation(property="rotation", end=Rotation(0,-89,0), easing="linear", dur=2000))
        self.scene.run_animations(self.Door_Left)
        self.Door_Right.dispatch_animation(Animation(property="rotation", end=Rotation(0,89,0), easing="linear", dur=2000))
        self.scene.run_animations(self.Door_Right)
    def CloseDoor(self):
        if(VERBOSE):
            printMagentaB("Doors closed!")
        self.doorsOpen = False
        self.Door_Left.dispatch_animation(Animation(property="rotation", end=Rotation(0,0,0), easing="linear", dur=2000))
        self.scene.run_animations(self.Door_Left)
        self.Door_Right.dispatch_animation(Animation(property="rotation", end=Rotation(0,0,0), easing="linear", dur=2000))
        self.scene.run_animations(self.Door_Right)

    def _clamp(self, n, min, max): 
        if n < min: 
            return min
        elif n > max: 
            return max
        else: 
            return n 
    def SetChassisPosition(self, pos): #Ranges from -0.15 to 0.15, meters
        pos = self._clamp(pos, -0.15, 0.15)
        if(VERBOSE):
            printGreenB("Position set to " + str(pos) + " meters.")
        self.chassisPosition = pos     
        self.Chassis_Front.data.position = Position(pos,0,0)
        self.scene.update_object(self.Chassis_Front)
        self.Cover_Front_Left.data.scale = Scale(1+pos*3.75,1,1)
        self.scene.update_object(self.Cover_Front_Left)
        self.Cover_Front_Right.data.scale = Scale(1-pos*3.75,1,1)
        self.scene.update_object(self.Cover_Front_Right)

    def SetPendulumRotationRadians(self, degrees): #Ranges from 0 to 360, degrees
        if(VERBOSE):
            printBlueB("Rotation set to " + str(degrees) + " degrees.")
        self._rotatePendulum(degrees)
    def SetPendulumRotationDegrees(self, radians): #Ranges from 0 to 2pi, radians
        if(VERBOSE):
            printBlueB("Rotation set to " + str(radians) + " radians.")
        self._rotatePendulum(radians * 57.2957795131)
    def _rotatePendulum(self, degrees):
        self.pendulumRotation = degrees
        self.PendulumAxis.data.rotation = Rotation(0,0,degrees)
        self.scene.update_object(self.PendulumAxis)

# ------------------------------------------ #
# -----------CLASS USAGE EXAMPLE------------ #
# ------------------------------------------ #

# How to use this example script in Terminal CLI:
#
#   py BoschPendulum.py -mh "arenaxr.org" -n "johnchoi" -s "BoschPendulum" -p 0 0 0 -r 0 0 0 -c 1 1 1
#     -mh = host | -n = namespace | -s = scene | -p = position | -r = rotation | -c = scale
#
if __name__=="__main__":
    def end_program_callback(scene: Scene):
        if(VERBOSE):
            printYellowB("Ending Bosch Pendulum Program. Goodbye :)")

    # command line scene start options
    scene = Scene(cli_args=True, end_program_callback=end_program_callback)
    app_position = scene.args["position"]
    app_rotation = scene.args["rotation"]
    app_scale = scene.args["scale"]

    # manual hardcoded setup ARENA scene
    #scene = Scene(host="arenaxr.org", namespace="johnchoi", scene="BoschPendulum")
    #app_position=Position(1.5,0,-1.5),
    #app_rotation=Rotation(0,45,0),
    #app_scale=Scale(1,1,1),

    #Call this function to create a boschPendulum class instance
    boschPendulum = ArenaBoschPendulum(scene, app_position, app_rotation, app_scale)

    #Loop interval update timers in Milliseconds:
    EXAMPLE_DOOR_INTERVAL = 5000
    EXAMPLE_CHASSIS_INTERVAL = 50
    EXAMPLE_PENDULUM_INTERVAL = 50

    @scene.run_once
    def ProgramStart():
        if(VERBOSE):
            print("Program started.")

    @scene.run_forever(interval_ms=EXAMPLE_DOOR_INTERVAL)
    def ExampleDoorUpdate():
        if(boschPendulum.doorsOpen):
            boschPendulum.CloseDoor()
        else:
            boschPendulum.OpenDoor()
        
    @scene.run_forever(interval_ms=EXAMPLE_CHASSIS_INTERVAL)
    def ExampleChassisUpdate():
        boschPendulum.chassisTimer = boschPendulum.chassisTimer + EXAMPLE_CHASSIS_INTERVAL
        boschPendulum.SetChassisPosition(0.15*math.sin(boschPendulum.chassisTimer * 0.5))
        
    @scene.run_forever(interval_ms=EXAMPLE_PENDULUM_INTERVAL)
    def ExamplePendulumUpdate():
        boschPendulum.pendulumTimer = boschPendulum.pendulumTimer + EXAMPLE_PENDULUM_INTERVAL
        boschPendulum.SetPendulumRotationDegrees(boschPendulum.pendulumTimer * 0.001)

    scene.run_tasks()