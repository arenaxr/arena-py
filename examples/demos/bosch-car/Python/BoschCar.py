from ColorPrinter import *
from arena import *

import serial
import time

#FILESTORE SETTINGS
FILESTORE = "https://arenaxr.org/" #main server
FILEPATH = "store/users/johnchoi/BoschCar_Simplified/" #Path
HEADER = "BoschCar"

DISTANCE = 0.2
SEPARATOR = 0.4
ANIMATE_DURATION = 1500

VERBOSE = True

#make sure Arduino with correct serial port name is attached!
arduino = serial.Serial(port='COM4',  baudrate=115200, timeout=1)

class BoschCar:

    def __init__(self, scene, position, rotation, scale):
        self.scene = scene
        #State vars
        self.HOOD = 0
        self.ENGINE = 0
        self.WHEEL_L = 0
        self.WHEEL_R = 0
        self.HEADLIGHT_L = 0
        self.HEADLIGHT_R = 0
        #Apply CLI Transform Parameters
        self.rootPosition = position
        self.rootRotation = rotation
        self.rootScale = scale
        #Initialize Root/GLB Objects
        self.CreateRoot()
        self.CreateGLBs()
        if(VERBOSE):
            printWhiteB("Bosch Car initialized at position " + str(position) + ", rotation " + str(rotation) + ", and scale "+ str(scale) + ".")

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
        #Body
        self.Body = self.CreateGLB("Body", Position(0,0,0), Rotation(0,0,0), self.root)
        #Hood
        self.Hood = self.CreateGLB("Hood", Position(0,0.3524,0.1218), Rotation(0,0,0), self.root)
        
        #Engine
        self.Engine_Block = self.CreateGLB("Engine_Block", Position(0,0,0), Rotation(0,0,0), self.root)
        self.Engine_Exhaust = self.CreateGLB("Engine_Exhaust", Position(0,0,0), Rotation(0,0,0), self.root)
        self.Engine_Exhaust_Screw = self.CreateGLB("Engine_Exhaust_Screw", Position(0,0,0), Rotation(0,0,0), self.root)
        self.Engine_Screws = self.CreateGLB("Engine_Screws", Position(0,0,0), Rotation(0,0,0), self.root)
        
        #Left Wheel
        self.Wheel_L_Brake = self.CreateGLB("Wheel_L_Brake", Position(0,0,0), Rotation(0,0,0), self.root)
        self.Wheel_L_Screws = self.CreateGLB("Wheel_L_Screws", Position(0,0,0), Rotation(0,0,0), self.root)
        self.Wheel_L_Tire = self.CreateGLB("Wheel_L_Tire", Position(0,0,0), Rotation(0,0,0), self.root)
        #Right Wheel
        self.Wheel_R_Brake = self.CreateGLB("Wheel_R_Brake", Position(0,0,0), Rotation(0,0,0), self.root)
        self.Wheel_R_Screws = self.CreateGLB("Wheel_R_Screws", Position(0,0,0), Rotation(0,0,0), self.root)
        self.Wheel_R_Tire = self.CreateGLB("Wheel_R_Tire", Position(0,0,0), Rotation(0,0,0), self.root)
        
        #Left Headlight
        self.HeadLight_L = self.CreateGLB("HeadLight_L", Position(0,0,0), Rotation(0,0,0), self.root)
        self.HeadLight_L_Screw = self.CreateGLB("HeadLight_L_Screw", Position(0,0,0), Rotation(0,0,0), self.root)
        #Right Headlight
        self.HeadLight_R = self.CreateGLB("HeadLight_R", Position(0,0,0), Rotation(0,0,0), self.root)
        self.HeadLight_R_Screw = self.CreateGLB("HeadLight_R_Screw", Position(0,0,0), Rotation(0,0,0), self.root)

    #-----------MOTION FUNCTIONS-----------#
    
    def AnimatePart(self, part, position, rotation, duration):
        part.dispatch_animation( [ Animation(property="position", end=position, easing="linear", dur=duration),
                                   Animation(property="rotation", end=rotation, easing="linear", dur=duration) ] )
        self.scene.run_animations(part)
    def ResetParts(self, parts, duration):
        for part in parts:
            self.AnimatePart(part, Position(0,0,0), Rotation(0,0,0), duration)

    def AnimateHood(self,isOn):
        if(isOn):
            self.AnimatePart(self.Hood, Position(0,0.3524,0.1218), Rotation(0,0,0), ANIMATE_DURATION)
        else:
            self.AnimatePart(self.Hood, Position(0,0.3524,0.1218), Rotation(89,0,0), ANIMATE_DURATION)
    
    def AnimateEngine(self,isOn):
        if(isOn):
            self.ResetParts([self.Engine_Block, self.Engine_Screws, self.Engine_Exhaust, self.Engine_Exhaust_Screw], ANIMATE_DURATION)
        else:
            self.AnimatePart(self.Engine_Block, Position(0,DISTANCE*(1+SEPARATOR*0),0), Rotation(0,0,0), ANIMATE_DURATION)
            self.AnimatePart(self.Engine_Screws, Position(0,DISTANCE*(1+SEPARATOR*1),0), Rotation(0,0,0), ANIMATE_DURATION)
            self.AnimatePart(self.Engine_Exhaust, Position(0,DISTANCE*(1+SEPARATOR*2),0), Rotation(0,0,0), ANIMATE_DURATION)
            self.AnimatePart(self.Engine_Exhaust_Screw, Position(0,DISTANCE*(1+SEPARATOR*3),0), Rotation(0,0,0), ANIMATE_DURATION)
    
    def AnimateLeftWheel(self,isOn):
        if(isOn):
            self.ResetParts([self.Wheel_L_Brake, self.Wheel_L_Tire, self.Wheel_L_Screws], ANIMATE_DURATION)
        else:
            self.AnimatePart(self.Wheel_L_Brake, Position(-DISTANCE*(1+SEPARATOR*0),0,0), Rotation(0,0,0), ANIMATE_DURATION)
            self.AnimatePart(self.Wheel_L_Tire, Position(-DISTANCE*(1+SEPARATOR*1),0,0), Rotation(0,0,0), ANIMATE_DURATION)
            self.AnimatePart(self.Wheel_L_Screws, Position(-DISTANCE*(1+SEPARATOR*2),0,0), Rotation(0,0,0), ANIMATE_DURATION)
    
    def AnimateRightWheel(self,isOn):
        if(isOn):
            self.ResetParts([self.Wheel_R_Brake, self.Wheel_R_Tire, self.Wheel_R_Screws], ANIMATE_DURATION)
        else:
            self.AnimatePart(self.Wheel_R_Brake, Position(DISTANCE*(1+SEPARATOR*0),0,0), Rotation(0,0,0), ANIMATE_DURATION)
            self.AnimatePart(self.Wheel_R_Tire, Position(DISTANCE*(1+SEPARATOR*1),0,0), Rotation(0,0,0), ANIMATE_DURATION)
            self.AnimatePart(self.Wheel_R_Screws, Position(DISTANCE*(1+SEPARATOR*2),0,0), Rotation(0,0,0), ANIMATE_DURATION)

    def AnimateLeftHeadlight(self,isOn):
        if(isOn):
            self.ResetParts([self.HeadLight_L, self.HeadLight_L_Screw], ANIMATE_DURATION)
        else:
            self.AnimatePart(self.HeadLight_L, Position(0,0,-DISTANCE), Rotation(0,0,0), ANIMATE_DURATION)
            self.AnimatePart(self.HeadLight_L_Screw, Position(0,DISTANCE*0.5,0), Rotation(0,0,0), ANIMATE_DURATION)
    def AnimateRightHeadlight(self,isOn):
        if(isOn):
            self.ResetParts([self.HeadLight_R, self.HeadLight_R_Screw], ANIMATE_DURATION)
        else:
            self.AnimatePart(self.HeadLight_R, Position(0,0,-DISTANCE), Rotation(0,0,0), ANIMATE_DURATION)
            self.AnimatePart(self.HeadLight_R_Screw, Position(0,DISTANCE*0.5,0), Rotation(0,0,0), ANIMATE_DURATION)
        
    #-----------STRING PROCESSING FUNCTIONS-----------#
    
    def processValues(self, a, b, c, d, e, f):
        if(self.HOOD!=a):
            self.HOOD=a

            if(self.HOOD==1):
                if(VERBOSE):
                    printBlue("Hood closed!")
                self.AnimateHood(True)
            else:
                if(VERBOSE):
                    printLightBlue("Hood opened!")
                self.AnimateHood(False)
                
        if(self.ENGINE!=b):
            self.ENGINE=b
    
            if(self.ENGINE==1):
                if(VERBOSE):
                    printRed("Engine placed!")
                self.AnimateEngine(True)
            else:
                if(VERBOSE):
                    printLightRed("Engine removed!")
                self.AnimateEngine(False)

        if(self.WHEEL_L!=c):
            self.WHEEL_L=c
        
            if(self.WHEEL_L==1):
                if(VERBOSE):
                    printGreen("Left wheel connected!")
                self.AnimateLeftWheel(True)
            else:
                if(VERBOSE):
                    printLightGreen("Left wheel disconnected!")
                self.AnimateLeftWheel(False)
            
        if(self.WHEEL_R!=d):
            self.WHEEL_R=d
    
            if(self.WHEEL_R==1):
                if(VERBOSE):
                    printMagenta("Right wheel connected!")
                self.AnimateRightWheel(True)
            else:
                if(VERBOSE):
                    printMagenta("Right wheel disconnected!")
                self.AnimateRightWheel(False)
            
        if(self.HEADLIGHT_L!=e):
            self.HEADLIGHT_L=e
        
            if(self.HEADLIGHT_L==1):
                if(VERBOSE):
                    printYellow("Left Headlight inserted!")
                self.AnimateLeftHeadlight(True)
            else:
                if(VERBOSE):
                    printLightYellow("Left Headlight removed!")
                self.AnimateLeftHeadlight(False)
            
        if(self.HEADLIGHT_R!=f):
            self.HEADLIGHT_R=f

            if(self.HEADLIGHT_R==1):
                if(VERBOSE):
                    printCyan("Right Headlight inserted!")
                self.AnimateRightHeadlight(True)
            else:
                if(VERBOSE):
                    printLightCyan("Right Headlight removed!")
                self.AnimateRightHeadlight(False)

# ------------------------------------------ #
# -----------CLASS USAGE EXAMPLE------------ #
# ------------------------------------------ #

# How to use this example script in Terminal CLI: (make sure Arduino with correct serial port name is attached!)
#
#   py BoschCar.py -mh "arenaxr.org" -n "johnchoi" -s "BoschCarArduino" -p 0 0 0 -r 0 0 0 -c 1 1 1
#   py BoschCar.py -mh "arenaxr.org" -n "public" -s "arena" -p 0 0.85 -2.9 -r 0 180 0 -c 1 1 1
#     -mh = host | -n = namespace | -s = scene | -p = position | -r = rotation | -c = scale
#
if __name__=="__main__":

    def end_program_callback(scene: Scene):
        if(VERBOSE):
            printYellowB("Ending Bosch Car Program. Goodbye :)")

    # command line scene start options
    scene = Scene(cli_args=True, end_program_callback=end_program_callback)
    app_position = scene.args["position"]
    app_rotation = scene.args["rotation"]
    app_scale = scene.args["scale"]

    # manual hardcoded setup ARENA scene
    #scene = Scene(host="arenaxr.org", namespace="johnchoi", scene="BoschCarArduino")
    #app_position=Position(0,0.85,-2.9),
    #app_rotation=Rotation(0,180,0),
    #app_scale=Scale(1,1,1),

    #Call this function to create a boschPendulum class instance
    boschCar = BoschCar(scene, app_position, app_rotation, app_scale)

    @scene.run_once
    def ProgramStart():
        if(VERBOSE):
            print("Program started.")

    @scene.run_forever(interval_ms=10)
    def ExampleDoorUpdate():
    
        value = ""

        try:
            value = arduino.readline().decode('utf-8').rstrip()
        except:
            if(VERBOSE):
                printRedB("Failed to read serial from arduino.")
        
        if (len(value) >= 6):

            a = int(value[0])
            b = int(value[1])
            c = int(value[2])
            d = int(value[3])
            e = int(value[4])
            f = int(value[5])

            boschCar.processValues(a,b,c,d,e,f)

            '''
            print("HO=" + str(HOOD) + " | EN="  + str(ENGINE) + 
                " | WL="  + str(WHEEL_L) + " | WR="  + str(WHEEL_R) + 
                " | HL="  + str(HEADLIGHT_L) + " | HR="  + str(HEADLIGHT_R))
            '''

    scene.run_tasks()