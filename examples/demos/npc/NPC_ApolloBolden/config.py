from arena import *

#DIALOGUE TREE FILE
DIALOGUE_FILENAME = "apollo_bolden.json"

#ARENA SETTINGS
FILESTORE = "https://arenaxr.org/" #main server
HOST = "arenaxr.org"          #main server
NAMESPACE = "johnchoi" #"johnchoi"
SCENE = "Astronaut" #"NPC"

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
NPC_NAME = "NPC_ApolloBolden"
NPC_GLTF_URL = FILESTORE+"store/users/johnchoi/Objects/Apollo/FlightSuitCharlesFBolden_2014-243-4-10k-2048_std_draco.glb"
NPC_ICON_URL = FILESTORE+"store/users/johnchoi/Objects/Apollo/NMAAHC-2014_243_4_011_screen.jpg"

#ENTER/EXIT SPECIAL EVENT NODES 
ENTER_INTERVAL = 100
ENTER_DISTANCE = 10
ENTER_NODE = "Charles F. Bolden's Flight Suit"
EXIT_NODE = "Exit"

#NO ACTIVITY RESET
RESET_INTERVAL = 100
RESET_TIME = 5*60000 #x min of no activity resets interaction.

#MISCELLANEOUS
TRANSFORM_INTERVAL = 500
TRANSFORM_TIMER = 3000
UUID_LEN = 6
USE_NAME_AS_TITLE = False

#UI
UI_THEME = "light" #"light" or "dark"
UI_VERTICAL_BUTTONS = True
UI_SPEECH_FONT_SIZE = 0.05
UI_SPEECH_ICON_WIDTH = 0.5
UI_SPEECH_TEXT_WIDTH = 0.5
UI_SPEECH_ICON_FILL = "cover", #cover, contain, stretch

#USE DEFAULT ACTIONS
USE_DEFAULT_ANIMATIONS = True
USE_DEFAULT_MORPHS = True
USE_DEFAULT_SOUNDS = True

#NPC ROOT TRANSFORM
ROOT_PARENT = "marker1"

ROOT_SCALE = Scale(1,1,1)
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
GLTF_POSITION = Position(.6,-.6,0)
GLTF_ROTATION = Rotation(0,-15,0) #radians, not degrees??

#NPC PLANE SETTINGS (for both images and videos)
PLANE_SCALE = 0.4
PLANE_SCALE_DURATION = 500
PLANE_POSITION = Position(.6,-0.1,0.2)
PLANE_ROTATION = Rotation(0,0,0) #radians, not degrees??

PLANE_OPACITY = 0.9

#SPEECH SETTINGS
SPEECH_INTERVAL = 100
SPEECH_SPEED = 3
SPEECH_TEXT_COLOR = Color(250,100,250)

SPEECH_BUBBLE_POSITION = Position(-.0,-.4,0.15)
SPEECH_BUBBLE_ROTATION = Rotation(0,5,0)
SPEECH_BUBBLE_SCALE = Scale(.35,.35,.35)

#CHOICE SETTINGS
CHOICE_TEXT_COLOR = Color(255,255,255)
CHOICE_BUBBLE_COLOR = Color(0,0,200)
CHOICE_BUBBLE_OPACITY = 0.5

CHOICE_BUBBLE_POSITION = Position(1.1, -.4, 0.2)
CHOICE_BUBBLE_ROTATION = Rotation(0,-15,0)
CHOICE_BUBBLE_SCALE = Scale(0.35, 0.35, 0.35)

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