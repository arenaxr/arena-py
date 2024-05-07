from ColorPrinter import *
from arena import *
import json
import sys

import os.path

#DEVELOPER DEBUG SETTINGS
USE_DEV_ARENAPY = False
ARENAPY_DEV_PATH = "D:/Github/arena-py/"  # Linux/Mac (Civilized)
ARENAPY_DEV_PATH = "D:\\Github\\arena-py" # Windows   (Uncivilized)

USE_DEV_SERVER = False
if(USE_DEV_SERVER):
    HOST = "arena-dev1.conix.io" #dev server
if(USE_DEV_SERVER):
    FILESTORE = "https://arena-dev1.conix.io/" #dev server
PRINT_VERBOSE = False

# CLI ARGUMENT: FOLDERNAME (Contains path to config file, dialogue file, and mappings file)
FOLDERNAME = sys.argv[1]
CONFIG_FILENAME   = os.path.join(sys.argv[1] , "config.json")   #"config.json"
DIALOGUE_FILENAME = os.path.join(sys.argv[1] , "dialogue.json") #"dialogue.json"
MAPPINGS_FILENAME = os.path.join(sys.argv[1] , "mappings.json") #"mappings.json"

#QUICK HELPER FUNCTIONS TO CONVERT JSON -> ARENA-PY DATA TYPES
def ToPosition(json):
    return Position(json["x"],json["y"],json["z"])
def ToRotation(json):
    return Rotation(json["x"],json["y"],json["z"])
def ToScale(json):
    return Scale(json["x"],json["y"],json["z"])
def ToColor(json):
    return Color(json["r"],json["g"],json["b"])

class Config:
    def __init__(self):

        # Open config file
        f = open(CONFIG_FILENAME)
        jsonString = f.read()
        configJson = json.loads(jsonString) 

        #ARENA CONNECTION
        self.HOST = configJson["ARENA"]["HOST"]           #"arenaxr.org"      
        self.NAMESPACE = configJson["ARENA"]["NAMESPACE"] #"johnchoi"
        self.SCENE = configJson["ARENA"]["SCENE"]         #"arena"

        #ENTER/EXIT SPECIAL EVENT NODES 
        self.ENTER_NODE = configJson["NODE"]["ENTER"] #"Enter"
        self.EXIT_NODE = configJson["NODE"]["EXIT"]   #"Exit"

        #NPC (name Alphanumeric only plus '_', no spaces!)
        self.NPC_NAME = configJson["NPC"]["NAME"]         #"NPC_RobotBuddy"
        self.NPC_GLTF_URL = configJson["NPC"]["GLTF_URL"] #"https://arenaxr.org/store/users/johnchoi/Characters/RobotBuddy/RobotBuddyBlue.glb"
        self.NPC_ICON_URL = configJson["NPC"]["ICON_URL"] #"https://arenaxr.org/store/users/johnchoi/Characters/RobotBuddy/RobotBuddyBlue.png"

        #USE DEFAULT ACTIONS
        self.USE_DEFAULT_ANIMATIONS = configJson["USE_DEFAULTS"]["ANIMATIONS"] #True
        self.USE_DEFAULT_MORPHS = configJson["USE_DEFAULTS"]["MORPHS"]         #True
        self.USE_DEFAULT_SOUNDS = configJson["USE_DEFAULTS"]["SOUNDS"]         #True

        #NO ACTIVITY RESET TIMER
        self.RESET_INTERVAL = configJson["TIMERS"]["RESET"]["INTERVAL"] #100
        self.RESET_TIME = configJson["TIMERS"]["RESET"]["TIME"] #5*60000 #x min of no activity resets interaction.
        #TRANSFORM MOVE TIMER
        self.TRANSFORM_INTERVAL = configJson["TIMERS"]["TRANSFORM"]["INTERVAL"] #500
        self.TRANSFORM_TIMER = configJson["TIMERS"]["TRANSFORM"]["TIMER"]       #3000
        #SPEECH TIMER
        self.SPEECH_INTERVAL = configJson["TIMERS"]["SPEECH"]["INTERVAL"] #100
        self.SPEECH_SPEED = configJson["TIMERS"]["SPEECH"]["SPEED"]       #3

        #UI
        self.USE_NAME_AS_TITLE = configJson["UI"]["USE_NAME_AS_TITLE"]       #False
        self.UI_THEME = configJson["UI"]["THEME"]                         #"light" or "dark"
        self.UI_VERTICAL_BUTTONS = configJson["UI"]["VERTICAL_BUTTONS"]   #True
        self.UI_SPEECH_FONT_SIZE = configJson["UI"]["FONT_SIZE"]   #0.05
        self.UI_SPEECH_TEXT_WIDTH = configJson["UI"]["TEXT_WIDTH"] #0.5
        self.UI_SPEECH_ICON_WIDTH = configJson["UI"]["ICON_WIDTH"] #0.5
        self.UI_SPEECH_ICON_FILL = configJson["UI"]["ICON_FILL"]   #cover, contain, stretch

        #NPC ROOT TRANSFORM
        self.ROOT_PARENT = configJson["ROOT"]["PARENT"]     #"" or "marker1"
        self.ROOT_SCALE = ToScale(configJson["ROOT"]["SCALE"])       #Scale(0.8,0.8,0.8)
        self.ROOT_SIZE = configJson["ROOT"]["SIZE"]         #0.2
        self.ROOT_POSITION = ToPosition(configJson["ROOT"]["POSITION"]) #Position(7.2, 0.0, -2.8) #This is the start position
        self.ROOT_ROTATION = ToRotation(configJson["ROOT"]["ROTATION"]) #Rotation(0,0,0)
        self.ROOT_COLOR = ToColor(configJson["ROOT"]["COLOR"])       #Color(255,100,16)
        self.ROOT_OPACITY = configJson["ROOT"]["OPACITY"]   #0.5

        #NPC GLTF TRANSFORM
        self.GLTF_SCALE = ToScale(configJson["GLTF"]["SCALE"])       #Scale(1,1,1)
        self.GLTF_POSITION = ToPosition(configJson["GLTF"]["POSITION"]) #Position(0,0,0)
        self.GLTF_ROTATION = ToRotation(configJson["GLTF"]["ROTATION"]) #Rotation(0,180,0) 

        #NPC PLANE SETTINGS (for both images and videos)
        self.PLANE_SIZE = configJson["PLANE"]["SIZE"]                  #1.2
        self.PLANE_SIZE_DURATION = configJson["PLANE"]["SIZE_DURATION"] #500
        self.PLANE_POSITION = ToPosition(configJson["PLANE"]["POSITION"])             #Position(1.5,0.8,0)
        self.PLANE_ROTATION = ToRotation(configJson["PLANE"]["ROTATION"])             #Rotation(0,-15,0) 
        self.PLANE_OPACITY = configJson["PLANE"]["OPACITY"]               #0.9

        #SPEECH TEXT SETTINGS
        self.SPEECH_TEXT_COLOR = configJson["SPEECH"]["TEXT"]["COLOR"]       #Color(250,100,250)
        self.SPEECH_TEXT_POSITION = configJson["SPEECH"]["TEXT"]["POSITION"] #Position(0,1.6,0)
        self.SPEECH_TEXT_SCALE = configJson["SPEECH"]["TEXT"]["SCALE"]       #Scale(0.6,0.7,0.7)
        #SPEECH BUBBLE SETTINGS
        self.SPEECH_BUBBLE_POSITION = ToPosition(configJson["SPEECH"]["BUBBLE"]["POSITION"]) #Position(0,1.7,0)
        self.SPEECH_BUBBLE_ROTATION = ToRotation(configJson["SPEECH"]["BUBBLE"]["ROTATION"]) #Rotation(0,5,0)
        self.SPEECH_BUBBLE_SCALE = ToScale(configJson["SPEECH"]["BUBBLE"]["SCALE"])       #Scale(1,1,1)

        #CHOICE TEXT SETTINGS
        self.CHOICE_TEXT_COLOR = ToColor(configJson["CHOICE"]["TEXT"]["COLOR"])         #Color(255,255,255)
        self.CHOICE_TEXT_SCALE = ToScale(configJson["CHOICE"]["TEXT"]["SCALE"])        #Scale(0.4, 2, .5)
        #CHOICE BUBBLE SETTINGS
        self.CHOICE_BUBBLE_COLOR = ToColor(configJson["CHOICE"]["BUBBLE"]["COLOR"])     #Color(0,0,200)
        self.CHOICE_BUBBLE_OPACITY = configJson["CHOICE"]["BUBBLE"]["OPACITY"] #0.5
        self.CHOICE_BUBBLE_POSITION = ToPosition(configJson["CHOICE"]["BUBBLE"]["POSITION"]) #Position(-0.95,0.6,0.4)
        self.CHOICE_BUBBLE_ROTATION = ToRotation(configJson["CHOICE"]["BUBBLE"]["ROTATION"]) #Rotation(0,15,0)
        self.CHOICE_BUBBLE_OFFSET_Y = configJson["CHOICE"]["BUBBLE"]["OFFSET_Y"] #0.25
        self.CHOICE_BUBBLE_SCALE = ToScale(configJson["CHOICE"]["BUBBLE"]["SCALE"])     #Scale(0.8, 0.8, 0.8)

        #LINK TEXT SETTINGS
        self.LINK_TEXT_COLOR = ToColor(configJson["LINK"]["TEXT"]["COLOR"])         #Color(255,255,255)
        self.LINK_TEXT_SCALE = ToScale(configJson["LINK"]["TEXT"]["SCALE"])           #Scale(0.2, 2, .5)
        #LINK BUBBLE SETTINGS
        self.LINK_BUBBLE_COLOR = ToColor(configJson["LINK"]["BUBBLE"]["COLOR"])     #Color(0,200,100)
        self.LINK_BUBBLE_OPACITY = configJson["LINK"]["BUBBLE"]["OPACITY"] #0.8
        self.LINK_BUBBLE_POSITION = ToPosition(configJson["LINK"]["BUBBLE"]["POSITION"]) #Position(0,0.8,0.7)
        self.LINK_BUBBLE_ROTATION = ToRotation(configJson["LINK"]["BUBBLE"]["ROTATION"]) #Rotation(0,0,0)
        self.LINK_BUBBLE_SCALE = ToScale(configJson["LINK"]["BUBBLE"]["SCALE"])       #Scale(1.5, 0.2, 0.08)

CFG = Config()