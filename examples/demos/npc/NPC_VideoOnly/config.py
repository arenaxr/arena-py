from arena import *

#DIALOGUE TREE FILE
DIALOGUE_FILENAME = "video_only.json"

#ARENA SETTINGS
FILESTORE = "https://arenaxr.org/" #main server
HOST = "arenaxr.org"          #main server
NAMESPACE = "public" #"johnchoi"
SCENE = "poster" #"NPC"

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

#NPC (name Alphanumeric only plus '_', no spaces!)
NPC_NAME = "ARENA Video Player"
NPC_GLTF_URL = "" #FILESTORE+"store/users/johnchoi/Characters/RobotBuddy/RobotBuddyBlue.glb"
NPC_ICON_URL = FILESTORE+"store/users/johnchoi/Images/xr-logo.png"

#ENTER/EXIT SPECIAL EVENT NODES 
ENTER_INTERVAL = 100
ENTER_DISTANCE = 10
ENTER_NODE = "ARENA Videos"
EXIT_NODE = "Exit"

#NO ACTIVITY RESET
RESET_INTERVAL = 100
RESET_TIME = 5*60000 #x min of no activity resets interaction.

#MISCELLANEOUS
TRANSFORM_TIMER = 3000
UUID_LEN = 6

TRANSFORM_INTERVAL = 500

#USE DEFAULT ACTIONS
USE_DEFAULT_ANIMATIONS = True
USE_DEFAULT_MORPHS = True
USE_DEFAULT_SOUNDS = True

#NPC ROOT TRANSFORM
ROOT_PARENT = ""

ROOT_SCALE = Scale(0.8,0.8,0.8)
ROOT_SIZE = 0.2

ROOT_POSITION = Position(0,0,0) #This is the start position
ROOT_ROTATION = Rotation(0,0,0)

ROOT_COLOR = Color(255,100,16)
ROOT_OPACITY = 0.5

COLLIDER_SCALE   = Scale(5,5,5)
COLLIDER_COLOR   = Color(255,100,16)
COLLIDER_OPACITY = 0.5

#NPC GLTF TRANSFORM
GLTF_SCALE = Scale(1,1,1)
GLTF_POSITION = Position(0,0,0)
GLTF_ROTATION = Rotation(0,180,0) #radians, not degrees??

#NPC PLANE SETTINGS (for both images and videos)
PLANE_SCALE = 0.6
PLANE_SCALE_DURATION = 500
PLANE_POSITION = Position(.7,1.9,0)

PLANE_ROTATION = Rotation(0,-5,0) #radians, not degrees??

PLANE_OPACITY = 0.9

#SPEECH SETTINGS
SPEECH_INTERVAL = 100
SPEECH_SPEED = 3
SPEECH_TEXT_COLOR = Color(250,100,250)

SPEECH_TEXT_POSITION = Position(0,2.5,0)
SPEECH_TEXT_SCALE = Scale(1,1,1)

SPEECH_BUBBLE_POSITION = Position(0,2.3,0)
SPEECH_BUBBLE_SCALE = Scale(.5,.5,.5)

#CHOICE SETTINGS
CHOICE_TEXT_COLOR = Color(255,255,255)
CHOICE_BUBBLE_COLOR = Color(0,0,200)
CHOICE_BUBBLE_OPACITY = 0.5

CHOICE_BUBBLE_ROTATION = Rotation(0,-5,0)
CHOICE_BUBBLE_POSITION = Position(.7,1.5,0)
CHOICE_BUBBLE_SCALE = Scale(0.3, 0.3, 0.3)

CHOICE_TEXT_SCALE = Scale(0.4, 2, .5)

CHOICE_SCALE_DURATION = 500

#URL SETTINGS
LINK_TEXT_COLOR = Color(255,255,255)
LINK_BUBBLE_COLOR = Color(0,200,100)
LINK_BUBBLE_OPACITY = 0.8

LINK_BUBBLE_POSITION = Position(0,0.8,0.7)
LINK_BUBBLE_ROTATION = Rotation(0,0,0)
LINK_BUBBLE_SCALE = Scale(1.5, 0.2, 0.08)
LINK_TEXT_SCALE = Scale(0.2, 2, .5)
