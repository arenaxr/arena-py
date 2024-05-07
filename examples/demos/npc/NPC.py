# ------------------------------------------ #
# ----------IMPORTING EVERYTHING------------ #
# ------------------------------------------ #
import sys
from config import *
from mappings import *
from YarnParser import *
from ColorPrinter import *
from ArenaDialogueBubbleGroup import *

if(USE_DEV_ARENAPY):
    printYellow("Using Development arena-py!")
    sys.path.append(ARENAPY_DEV_PATH)
from arena import *

from asyncio import create_subprocess_exec
from time import gmtime, strftime
from datetime import datetime
from datetime import timezone
import random

# total arguments
n = len(sys.argv)
printGreen("Total arguments passed:" + str(n))
# Arguments passed
printGreen("Name of Python script: " + sys.argv[0])
printGreen("Arguments passed:")
for i in range(1, n):
    printGreen("    [" + str(i) + "] " + sys.argv[i])
printGreen("")

# ------------------------------------------ #
# -----------MAIN NPC MASTERCLASS----------- #
# ------------------------------------------ #
class NPC:
    def __init__(self, scene):
        self.scene = scene

        self.entered = False
        self.userCount = 0

        self.blinked = False
        self.talking = False
        self.moving = False

        # create Dialogue, and show contents
        self.dialogue = Dialogue(DIALOGUE_FILENAME)

        #NPC ROOT OBJECT (with debug box)
        self.root = Box(
            object_id=CFG.NPC_NAME,
            scale=CFG.ROOT_SCALE,
            color=CFG.ROOT_COLOR,
            depth=CFG.ROOT_SIZE,
            width=CFG.ROOT_SIZE,
            height=CFG.ROOT_SIZE,
            position=CFG.ROOT_POSITION,
            #rotation=CFG.ROOT_ROTATION,
            material = Material(opacity=CFG.ROOT_OPACITY, transparent=True, visible=False),
            sound = None,
            persist=True
        )
        scene.add_object(self.root)
        printLightRedB(CFG.ROOT_PARENT)
        if(CFG.ROOT_PARENT != ""):
            self.root.data.parent = CFG.ROOT_PARENT
            scene.update_object(self.root)

        #NPC GLTF
        self.gltf = GLTF(
            object_id=CFG.NPC_NAME + "(GLTF)",
            url=CFG.NPC_GLTF_URL,
            position=CFG.GLTF_POSITION,
            rotation=CFG.GLTF_ROTATION,
            scale=CFG.GLTF_SCALE,
            animation_mixer = MAP.ANIM_IDLE,
            parent=self.root,
            clickable=True,
            persist=True
        )
        scene.add_object(self.gltf)
        
        #NPC IMAGE
        self.image = Image(
            object_id=CFG.NPC_NAME + "(IMAGE)",
            position=CFG.PLANE_POSITION,
            rotation=CFG.PLANE_ROTATION,
            scale=Scale(random.uniform(0, 0.001),random.uniform(0, 0.001),random.uniform(0, 0.001)), #Start at zero, not PLANE_SIZE to hide at start
            url = "https://arenaxr.org/store/users/johnchoi/Images/nyan.jpg",
            material = Material(transparent = True, opacity = CFG.PLANE_OPACITY, visible = False),
            parent=self.root,

            persist=True
        )
        scene.add_object(self.image)    
        #NPC VIDEO
        self.video = Plane(
            object_id=CFG.NPC_NAME + "(VIDEO)",
            position=CFG.PLANE_POSITION,
            rotation=CFG.PLANE_ROTATION,
            scale=Scale(random.uniform(0, 0.001),random.uniform(0, 0.001),random.uniform(0, 0.001)), #Start at zero, not PLANE_SIZE to hide at start
            material = Material(src = "https://arenaxr.org/store/users/johnchoi/Videos/rays.mp4", transparent = True, opacity = CFG.PLANE_OPACITY, w = 1920, h = 1080, size = 1, visible = False),
            parent=self.root,
            clickable=True,
            persist=True
        )
        scene.add_object(self.video)
        
        #Create Bubbles
        self.bubbles = ArenaDialogueBubbleGroup(self.scene, self.root, self.gltf, self.image, self.video, self.dialogue)

# ------------------------------------------ #
# --------MAIN LOOPS/INITIALIZATION--------- #
# ------------------------------------------ #

# setup ARENA scene
scene = Scene(host=CFG.HOST, namespace=CFG.NAMESPACE, scene=CFG.SCENE)

# make NPC
npc = NPC(scene)

@scene.run_once
def ProgramStart():
    npc.dialogue.printJson()
    npc.dialogue.printInfo()
    npc.bubbles.start()

@scene.run_forever(interval_ms=CFG.RESET_INTERVAL)
def Reset_Handler(): #RESET_TIME milliseconds of no activity resets interaction.
    if(npc.bubbles.resetTimer > 0):
        npc.bubbles.resetTimer = npc.bubbles.resetTimer - CFG.RESET_INTERVAL
    else:
        npc.bubbles.resetTimer = CFG.RESET_TIME
        npc.bubbles.gotoNodeWithName(CFG.ENTER_NODE)
        printLightRedB("NPC with name \"" + CFG.NPC_NAME + "\" detected no activity for " + str(CFG.RESET_TIME) + " milliseconds. Resetting.")

@scene.run_forever(interval_ms=CFG.SPEECH_INTERVAL)
def Speech_Handler(): #iteratively adds characters to speech bubble

    if(npc.bubbles.checkIfArenaObjectExists(npc.bubbles.speechBubble)):
        
        #random blink:
        if(CFG.USE_DEFAULT_MORPHS):
            if(random.randint(0, 30) == 0):
                npc.bubbles.PlayMorph(MAP.MORPH_BLINK_ON)
                npc.blinked = True
            else:
                if(npc.blinked == True):
                    npc.blinked = False
                    npc.bubbles.PlayMorph(MAP.MORPH_BLINK_OFF)
                    
        #if walking, let walk, hide buttons
        if(npc.bubbles.transformTimer > 0):
            npc.bubbles.transformTimer = npc.bubbles.transformTimer - CFG.SPEECH_INTERVAL
            npc.moving = True

        #Iterate through speech bubble text
        else:
            #Update Position Manually to prevent slingshotting
            if(npc.moving == True):
                npc.moving = False

            if(0 <= npc.bubbles.speechIndex and npc.bubbles.speechIndex * CFG.SPEECH_SPEED < len(npc.bubbles.speech)):
                npc.bubbles.speechIndex += 1
            
                #start talking animation if not started already
                if(CFG.USE_DEFAULT_ANIMATIONS and not npc.talking and not npc.bubbles.animationUsedThisLine):
                    npc.bubbles.PlayAnimation(MAP.ANIM_TALK)

                #if blendshapes applicable
                if(CFG.USE_DEFAULT_MORPHS):
                    #move mouth up and down
                    if((npc.bubbles.speechIndex+0) % 3 == 0):
                        npc.bubbles.PlayMorph(MAP.MORPH_OPEN)
                    if((npc.bubbles.speechIndex+1) % 3 == 0):
                        npc.bubbles.PlayMorph(MAP.MORPH_CLOSE)
            
                npc.talking = True

            else:
                npc.bubbles.speechIndex = len(npc.bubbles.speech)

                #play idle if not started already.
                if(CFG.USE_DEFAULT_ANIMATIONS and npc.talking and not npc.bubbles.animationUsedThisLine):
                    npc.bubbles.PlayAnimation(MAP.ANIM_IDLE)

                #close mouth if blendshapes applicable
                if(CFG.USE_DEFAULT_MORPHS and npc.talking):
                    npc.bubbles.PlayMorph(MAP.MORPH_CLOSE)

                npc.talking = False

            npc.isTalking = npc.talking

        #Iterate through speech bubble text
        npc.bubbles.speechBubble.data.body = npc.bubbles.speech[:npc.bubbles.speechIndex * CFG.SPEECH_SPEED]
        #if(npc.bubbles.speechBubble.data.text != npc.bubbles.speech):
        scene.update_object(npc.bubbles.speechBubble)
        
scene.run_tasks()

