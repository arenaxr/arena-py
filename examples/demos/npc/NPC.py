# ------------------------------------------ #
# ----------IMPORTING EVERYTHING------------ #
# ------------------------------------------ #

from config import *
from mappings import *
from YarnParser import *
from ColorPrinter import *
from ArenaDialogueBubbleGroup import *

import sys
if(USE_DEV_ARENAPY):
    printYellow("Using Development arena-py!")
    sys.path.append(ARENAPY_DEV_PATH)

from arena import *

from asyncio import create_subprocess_exec
from time import gmtime, strftime
from datetime import datetime
from datetime import timezone
import random

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
            object_id=NPC_NAME,
            scale=ROOT_SCALE,
            color=ROOT_COLOR,
            depth=ROOT_SIZE,
            width=ROOT_SIZE,
            height=ROOT_SIZE,
            position=ROOT_POSITION,
            #rotation=ROOT_ROTATION,
            material = Material(opacity=ROOT_OPACITY, transparent=True, visible=False),
            sound = None,
            persist=True
        )
        scene.add_object(self.root)

        self.root.data["remote-render"] = "{enabled: False}"
        scene.update_object(self.root)


        #NPC GLTF
        self.gltf = GLTF(
            object_id=NPC_NAME + "(GLTF)",
            url=NPC_GLTF_URL,
            position=GLTF_POSITION,
            rotation=GLTF_ROTATION,
            scale=GLTF_SCALE,
            #animation_mixer = ANIM_IDLE,
            parent=self.root,
            clickable=True,
            persist=True
        )
        scene.add_object(self.gltf)

        self.gltf.data["remote-render"] = "{enabled: False}"
        scene.update_object(self.gltf)

        '''
        #NPC ROOT OBJECT (with debug box)
        self.collider = Box(
            object_id=NPC_NAME + "(COLLIDER)",
            #position=ROOT_POSITION,
            #rotation=ROOT_ROTATION,
            scale=COLLIDER_SCALE,
            color=COLLIDER_COLOR,
            material = Material(opacity=COLLIDER_OPACITY, transparent=True),


            evt_handler=onCollisionHandler,
            parent=self.root,
            
            sound = None,
            persist=True


        )
        scene.add_object(self.collider)
        
        #functions to control choice button click behaviour
        def onCollisionHandler(self, scene, evt, msg):
            if evt.type == "mousedown":

                printCyan("  Next Button Pressed!")
                

                if(USE_DEFAULT_SOUNDS):
                    self.PlaySound(SOUND_NEXT)
        '''

        '''
        https://docs.arenaxr.org/content/python/tutorial/advanced.html#user-management
        scene.user_join_callback
        user_left_callback
        evt_handler=my_collision_listener
        '''

        #NPC IMAGE
        self.image = Image(
            object_id=NPC_NAME + "(IMAGE)",
            position=PLANE_POSITION,
            rotation=PLANE_ROTATION,
            scale=PLANE_SCALE, #Scale(0,0,0),
            url = FILESTORE+"store/users/johnchoi/Images/nyan.jpg",
            material = Material(transparent = True, opacity = PLANE_OPACITY),
            parent=self.root,
            persist=True
        )
        scene.add_object(self.image)   

        self.image.data["remote-render"] = {"enabled": False}
        scene.update_object(self.image)

        #NPC VIDEO
        self.video = Plane(
            object_id=NPC_NAME + "(VIDEO)",
            position=PLANE_POSITION,
            rotation=PLANE_ROTATION,
            scale=PLANE_SCALE, #Scale(0,0,0),
            material = Material(src = FILESTORE+"store/users/johnchoi/Videos/rays.mp4", transparent = True, opacity = PLANE_OPACITY, w = 1920, h = 1080, size = 1),
            parent=self.root,
            clickable=True,
            persist=True
        )
        scene.add_object(self.video)

        self.video.data["remote-render"] = {"enabled": False}
        scene.update_object(self.video)

        #Create Bubbles
        self.bubbles = ArenaDialogueBubbleGroup(self.scene, self.root , self.gltf, self.image, self.video, self.dialogue)

# ------------------------------------------ #
# --------MAIN LOOPS/INITIALIZATION--------- #
# ------------------------------------------ #

# setup ARENA scene
scene = Scene(host=HOST, namespace=NAMESPACE, scene=SCENE)

# make NPC
npc = NPC(scene)

@scene.run_once
def ProgramStart():
    npc.dialogue.printJson()
    npc.dialogue.printInfo()
    npc.bubbles.start()

def user_join_callback(scene, obj, msg):
    ## Get access to user state
    # camera is a Camera class instance (see Objects)
    #camera.object_id
    #camera.displayName
    #camera.hasVideo
    #camera.displayName
    # etc.
    #npc.bubbles.PlayLastTransform()
    npc.bubbles.reloadCurrentLine()
    npc.bubbles.PlayAnimation(ANIM_IDLE)
scene.user_join_callback = user_join_callback

#def user_left_callback(scene, obj, msg):
    ## Get access to user state
    # camera is a Camera class instance (see Objects)
    #camera.object_id
    #camera.displayName
    #camera.hasVideo
    #camera.displayName
    # etc.
#scene.user_left_callback = user_left_callback

@scene.run_forever(interval_ms=ENTER_INTERVAL)
def EnterExit_Handler(): #checks whether or not a user is in range of NPC
    users = scene.get_user_list()
    sceneUserCount = len(scene.get_user_list())
    userCount = 0

    #strange bug - closing browser does not send exit message?
    if(scene.get_user_list() == None):
        users = []
        sceneUserCount = 0

    '''
    for user in scene.get_user_list():
        if user.data.position.distance_to(npc.root.data.position) <= ENTER_DISTANCE:
            userCount+=1
    '''
            
    if(npc.userCount != userCount):
        printLightRedB(str(userCount) + " users in area of NPC with name \"" + NPC_NAME + "\".")
        if(userCount > 0 and npc.entered == False): # At least one user in range of NPC starts interaction.
            npc.entered = True
            #npc.bubbles.gotoNodeWithName(ENTER_NODE) #doesn't work?
            if(USE_DEFAULT_SOUNDS):
                npc.bubbles.PlaySound(SOUND_ENTER)

        if(userCount == 0 and npc.entered == True): # All users left, so end interaction.
            npc.entered = False
            #npc.bubbles.gotoNodeWithName(EXIT_NODE) #doesn't work?
            if(USE_DEFAULT_SOUNDS):
                npc.bubbles.PlaySound(SOUND_EXIT)
    
    npc.userCount = userCount


@scene.run_forever(interval_ms=RESET_INTERVAL)
def Reset_Handler(): #RESET_TIME milliseconds of no activity resets interaction.
    if(npc.bubbles.resetTimer > 0):
        npc.bubbles.resetTimer = npc.bubbles.resetTimer - RESET_INTERVAL
    else:
        npc.bubbles.resetTimer = RESET_TIME
        npc.bubbles.gotoNodeWithName(ENTER_NODE)
        printLightRedB("NPC with name \"" + NPC_NAME + "\" detected no activity for " + str(RESET_TIME) + " milliseconds. Resetting.")
        

#@scene.run_forever(interval_ms=TRANSFORM_TIMER)
#def Transform_Handler(): #send a heartbeat transform to keep position correct for new players
#    printWhiteB("Playing last transform...")        
#    npc.bubbles.PlayLastTransform()
#    npc.bubbles.reloadCurrentLine()

@scene.run_forever(interval_ms=SPEECH_INTERVAL)
def Speech_Handler(): #iteratively adds characters to speech bubble

    if(npc.bubbles.checkIfArenaObjectExists(npc.bubbles.speechBubble)):
        
        #random blink:
        if(USE_DEFAULT_MORPHS):
            if(random.randint(0, 30) == 0):
                npc.bubbles.PlayMorph(MORPH_BLINK_ON)
                npc.blinked = True
            else:
                if(npc.blinked == True):
                    npc.blinked = False
                    npc.bubbles.PlayMorph(MORPH_BLINK_OFF)
                    
        #if walking, let walk, hide buttons
        if(npc.bubbles.transformTimer > 0):
            npc.bubbles.transformTimer = npc.bubbles.transformTimer - SPEECH_INTERVAL
            npc.moving = True

        #Iterate through speech bubble text
        else:
            #Update Position Manually to prevent slingshotting
            if(npc.moving == True):
                npc.moving = False
                #npc.bubbles.UpdateLastPosition()

            if(0 <= npc.bubbles.speechIndex and npc.bubbles.speechIndex * SPEECH_SPEED < len(npc.bubbles.speech)):
                npc.bubbles.speechIndex += 1
            
                #start talking animation if not started already
                if(USE_DEFAULT_ANIMATIONS and not npc.talking and not npc.bubbles.animationUsedThisLine):
                    npc.bubbles.PlayAnimation(ANIM_TALK)

                #if blendshapes applicable
                if(USE_DEFAULT_MORPHS):
                    #move mouth up and down
                    if((npc.bubbles.speechIndex+0) % 3 == 0):
                        npc.bubbles.PlayMorph(MORPH_OPEN)
                    if((npc.bubbles.speechIndex+1) % 3 == 0):
                        npc.bubbles.PlayMorph(MORPH_CLOSE)
            
                npc.talking = True

            else:
                npc.bubbles.speechIndex = len(npc.bubbles.speech)

                #play idle if not started already.
                if(USE_DEFAULT_ANIMATIONS and npc.talking and not npc.bubbles.animationUsedThisLine):
                    npc.bubbles.PlayAnimation(ANIM_IDLE)

                #close mouth if blendshapes applicable
                if(USE_DEFAULT_MORPHS and npc.talking):
                    npc.bubbles.PlayMorph(MORPH_CLOSE)

                npc.talking = False

            npc.isTalking = npc.talking

        #Iterate through speech bubble text
        npc.bubbles.speechBubble.data.body = npc.bubbles.speech[:npc.bubbles.speechIndex * SPEECH_SPEED]
        #if(npc.bubbles.speechBubble.data.text != npc.bubbles.speech):
        npc.bubbles.speechBubble.data["remote-render"] = {"enabled": False}
        
        scene.update_object(npc.bubbles.speechBubble)
        
        
scene.run_tasks()