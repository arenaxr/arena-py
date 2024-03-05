from config import *
from Button import *
from mappings import *
from YarnParser import *
from ColorPrinter import *

import sys
if(USE_DEV_ARENAPY):
    sys.path.append(ARENAPY_DEV_PATH)

from arena import *

from asyncio import create_subprocess_exec

import string
import random

# ------------------------------------------ #
# -----------ARENA BUBBLE GROUP------------- #
# ------------------------------------------ #

class ArenaDialogueBubbleGroup():
    def __init__(self, scene, npc, gltf, image, video, dialogue):
        #Persistent ARENA objects
        self.scene = scene
        self.npc = npc
        self.gltf = gltf
        self.image = image
        self.video = video
        self.linkButton = None

        #Dialogue stuff
        self.dialogue = dialogue
        self.speech = ""
        self.speechIndex = 0

        #"Used this line" vars (if command was used this line. Needed to reset things correctly.)
        self.animationUsedThisLine = False
        self.transformUsedThisLine = False
        self.imageUsedThisLine = False
        self.videoUsedThisLine = False
        self.soundUsedThisLine = False

        self.lastImageSize = Scale(0,0,0)
        self.lastVideoSize = Scale(0,0,0)

        self.lastTransform = TRANSFORM_RESET

        self.transformTimer = 0
        self.resetTimer = 0

        #Init Everything First time        
        self.initializeBubbles()

    def addResetClickHandler(self):
        self.gltf.data.evt_handler=self.OnClickReloadCurrentLine
        self.gltf.data["remote-render"] = {"enabled": False}
        self.scene.update_object(self.gltf)
        
    #reinitializes and restarts the interaction
    def start(self):
        printGreenB("\n(---Starting NPC interaction:---)")
        self.clearButtons()
        self.initializeBubbles()

        self.addResetClickHandler()

        #self.PlayLastTransform()

    #creates new bubbles
    def initializeBubbles(self, line = None):
        if(line == None):
            self.dialogue.currentNode.currentLine = self.dialogue.currentNode.lines[0]
            line = self.dialogue.currentNode.currentLine

    # ------------------------------------------ #
    # ------------RUNNING COMMANDS-------------- #
    # ------------------------------------------ #

    #Sounds
    def PlaySoundFromMapping(self, key):
        if(key in soundMappings):
            self.PlaySound(soundMappings[key])
        else:
            if(PRINT_VERBOSE):
                printWarning("    " + "Attempting to play sound from URL \"" + key + "\" because no such mapping exists in mappings.py.")
            
            self.PlaySoundFromUrl(key)
    def PlaySoundFromUrl(self, url):
        if(PRINT_VERBOSE):
            printWhiteB("Play sound from url \'" + url + "\"")
        sound = Sound(volume=1, autoplay=True, src=url)
        self.PlaySound(sound)
    def PlaySound(self, sound):
        if(PRINT_VERBOSE):
            printWhiteB("Playing sound...")
        self.npc.data.sound=None #resets so can play same sound again

        self.npc.data["remote-render"] = {"enabled": False}        
        self.scene.update_object(self.npc)
        self.npc.data.sound=sound

        self.npc.data["remote-render"] = {"enabled": False}
        self.scene.update_object(self.npc)

    #Animations
    def PlayAnimationFromMapping(self, key):
        if(key in animationMappings):
            self.PlayAnimation(animationMappings[key])
        else:     
            if(PRINT_VERBOSE):
                printWarning("    " + "Attempting to play animation from name \"" + key + "\" because no such mapping exists in mappings.py.")
            self.PlayAnimationFromName(key)

    def PlayAnimationFromName(self, name):
        if(PRINT_VERBOSE):
            printWhiteB("Play animation from name \'" + name + "\"")
        animation = AnimationMixer(clip=name, loop="once", crossFadeDuration=0.5, timeScale = 1)
        self.PlayAnimation(animation)

    def PlayAnimation(self, animation):
        if(PRINT_VERBOSE):
            printWhiteB("Playing animation...")
        self.gltf.dispatch_animation(animation)
        self.scene.run_animations(self.gltf)
        
    #Transforms
    def PlayTransformFromMapping(self, key):
        if(key in transformMappings):
            self.PlayTransform(transformMappings[key])
        else:
            if(PRINT_VERBOSE):
                printWarning("    " + "Cannot play transform \"" + key + "\" because no such mapping exists in mappings.py.")
    def PlayTransform(self, transform):
        
        if(PRINT_VERBOSE):
            printWhiteB("Playing transform...")
        
        self.npc.dispatch_animation(transform)
        self.scene.run_animations(self.npc)

        if(self.lastTransform == transform):
            self.transformUsedThisLine = False
        
        self.lastTransform = transform


    def UpdateLastPosition(self):
        transform = self.lastTransform
        p = getVectorFromString(transform[0].end)
        self.npc.data.position = Position(p[0], p[1], p[2])

        self.npc.data["remote-render"] = {"enabled": False}
        self.scene.update_object(self.npc)

    def PlayLastTransform(self):
        #self.PlayTransform(self.lastTransform)
        printWhite("Play Last Transform...")

    #Morphs
    def PlayMorphFromMapping(self, key):
        if(key in morphMappings):
            self.PlayMorph(morphMappings[key])
        else:
            if(PRINT_VERBOSE):
                printWarning("    " + "Cannot play morph \"" + key + "\" because no such mapping exists in mappings.py.")
    def PlayMorph(self, morphs):
        if(PRINT_VERBOSE):
            printWhiteB("Playing morph...")
        self.gltf.update_morph(morphs)
        self.gltf.data["remote-render"] = {"enabled": False}
        self.scene.update_object(self.gltf)

    #GotoUrl
    def PlayUrlFromMapping(self, key):
        if(key in urlMappings):
            self.PlayGotoUrl(urlMappings[key])
        else:
            if(PRINT_VERBOSE):
                printWarning("    " + "Attempting to directly play URL \"" + key + "\" because no such mapping exists in mappings.py.")
            self.PlayUrl(key)
    def PlayUrl(self, link):
        if(PRINT_VERBOSE):
            printWhiteB("Play url with link \'" + link + "\"")
        
        gotoUrl = GotoUrl(dest="popup", on="mousedown", url=link)
        self.PlayGotoUrl(gotoUrl)
    def PlayGotoUrl(self, gotoUrl):
        if(PRINT_VERBOSE):
            printWhiteB("Playing BLOB gotoUrl...")
        
        self.linkButton = NPCButton(self.scene, self.npc, self.npc.object_id + "(LINK)", "[Next]", self.onClickLinkButton, 
                            position = LINK_BUBBLE_POSITION, rotation = LINK_BUBBLE_ROTATION, buttonScale = LINK_BUBBLE_SCALE, 
                            textScale = LINK_TEXT_SCALE, color = LINK_BUBBLE_COLOR, textColor = LINK_TEXT_COLOR, persist=False)
        
        '''
        self.prompt = Prompt(
            object_id=HEADER + "_ConfirmationPrompt",
            look_at="#my-camera",
            
            title="Confirmation",
            description="Are you sure you want to make this move?",
            
            buttons=["Yes","No"],
            
            fontSize = 0.05,
       
            evt_handler=self.onClickLinkButton,


            position=LINK_BUBBLE_POSITION,
            rotation=LINK_BUBBLE_ROTATION,
            scale=LINK_BUBBLE_SCALE,



            parent=self.npc,
            persist = True
        )
        self.scene.add_object(self.prompt)
        '''

        self.linkButton.box.data.goto_url = gotoUrl
        self.linkButton.text.data.text = gotoUrl.url
        
        self.linkButton.box.data["remote-render"] = {"enabled": False}
        self.scene.update_object(self.linkButton.box)

        self.linkButton.text.data["remote-render"] = {"enabled": False}
        self.scene.update_object(self.linkButton.text)

    #Videos
    def PlayVideoFromMapping(self, key):
        if(key in videoMappings):
            if(videoMappings[key] is not None):
                self.PlayVideo(videoMappings[key])
            else:
                self.HideVideo()
        else:
            if(PRINT_VERBOSE):
                printWarning("    " + "Hiding video \"" + key + "\" because no such mapping exists in mappings.py.")
            self.HideVideo()
    def PlayVideoFromUrl(self, url):
        if(PRINT_VERBOSE):
            printWhiteB("Play video from url \'" + url + "\":")        
        
        #VideoControl Method
        #video = VideoControl(video_path = url, frame_object = DEFAULT_VIDEO_FRAME_OBJECT, video_object = None, 
        #                     anyone_clicks = True, video_loop = True, autoplay = True, volume = 1, w = 1920, h = 1080, size = 1),

        #Src Video Material Method
        video = Material(src = url, transparent = True, opacity = PLANE_OPACITY, w = 1920, h = 1080, size = 1)

        self.PlayVideo(video)
    
    def PlayVideo(self, video):
        if(PRINT_VERBOSE):
            printWhiteB("Playing video...")
        
        #Src Video Material Method
        self.video.data.material=None 
        
        self.video.data["remote-render"] = {"enabled": False}
        self.scene.update_object(self.video)
        
        self.ShowVideo(self.getNewScale(video.w, video.h, video.size))
        self.video.data.material=video

        self.video.data["remote-render"] = {"enabled": False}
        self.scene.update_object(self.video)

    def HideVideo(self):
        self.ScaleAnimation(self.video, self.lastVideoSize, Scale(0,0,random.uniform(0, 0.01)))        
        self.lastVideoSize = Scale(0,0,0)
    def ShowVideo(self, scale):
        self.ScaleAnimation(self.video, Scale(0,0,random.uniform(0, 0.01)), scale)
        self.lastVideoSize = scale

    #Images
    def PlayImageFromMapping(self, key):
        if(key in imageMappings):
            if(imageMappings[key] is not None):
                self.PlayImage(imageMappings[key])
            else:
                self.HideImage()
        else:
            if(PRINT_VERBOSE):
                printWarning("    " + "Hiding image with \"" + key + "\" because no such mapping exists in mappings.py.")
            self.HideImage()
    def PlayImageFromUrl(self, src):
        if(PRINT_VERBOSE):
            printWhiteB("Play image from url \'" + src + "\":")        
        img = IMG(url = src, w = 1000, h = 1000, size = 1)
        self.PlayImage(img)
    def PlayImage(self, img):
        if(PRINT_VERBOSE):
            printWhiteB("Playing image...")
        
        self.ShowImage(self.getNewScale(img.w, img.h, img.size))
        self.image.data["remote-render"] = {"enabled": False}
        self.scene.update_object(self.image, url = img.url)

    def HideImage(self):
        self.ScaleAnimation(self.image, self.lastImageSize, Scale(0,0,random.uniform(0, 0.01)))
        self.lastImageSize = Scale(0,0,0)
    def ShowImage(self, scale):
        self.ScaleAnimation(self.image, Scale(0,0,random.uniform(0, 0.01)), scale)
        self.lastImageSize = scale

        if(USE_DEFAULT_SOUNDS and not self.soundUsedThisLine):
            self.PlaySound(SOUND_IMAGE)

    #Scaling helper functions.
    def ScaleAnimation(self, plane, startScale, endScale):
        animation = Animation(property="scale", start=startScale, end=endScale, easing="easeInOutQuad", dur=PLANE_SCALE_DURATION)
        plane.dispatch_animation(animation)
        self.scene.run_animations(plane)
        plane.update_attributes(scale = endScale)

    def getNewScale(self, w, h, size):
        aspect = ( w * 1.0 ) / ( h * 1.0 )
        scale = 1
        
        if( w > h):
            scale = (w + h) * 0.5 / (w * 1.0)
        else:
            scale = (w + h) * 0.5 / (h * 1.0)
            
        nw = aspect * scale * size * PLANE_SCALE
        nh = 1.0 * scale * size * PLANE_SCALE

        return Scale(nw, nh, 1)
    
    #Visibility
    def SetVisible(self, key, visible):            
        if (self.scene.all_objects.get(key) is not None):
            self.scene.all_objects.get[key].data.visible = visible
            self.scene.all_objects.get[key].data["remote-render"] = {"enabled": False}
            self.scene.update_object(self.scene.all_objects.get[key])
        else:
            if(PRINT_VERBOSE):
                printWarning("    " + "Cannot set visibility of object with name \"" + key + "\" because no such object exists in scene.")

    
    
    #Clear extra properties
    def ClearCommandProperties(self):
        #scale the link button out because delete won't work
        if(self.linkButton != None and self.checkIfArenaObjectExists(self.linkButton.box)):
            self.ScaleAnimation(self.linkButton.box, LINK_BUBBLE_SCALE, Scale(0,0,random.uniform(0, 0.01)))
            self.scene.delete_object(self.linkButton.text)
            self.scene.delete_object(self.linkButton.box)
        
    #runs commands
    def runCommands(self, line):
        commands = line.commands
        self.animationUsedThisLine = False
        self.transformUsedThisLine = False

        self.imageUsedThisLine = False
        self.videoUsedThisLine = False
        self.soundUsedThisLine = False

        #print details
        for c in range(len(commands)):            
            printGreen("    <<"+str(c)+">> commandType: " + commands[c].type)
            printGreen(         "          commandText: " + commands[c].text)
            if(len(commands[c].args) > 0):
                for a in range(len(commands[c].args)):
                    printGreen(     "          --commandArgs["+str(a)+"]: " + commands[c].args[a])

        #self.PlayLastTransform()

        #run through each command: 
        #--parentheses () optional for one argument, required for multiple, separated by commas.
        for command in commands:
        
            ###------MISCELLANEOUS------###

            #<<print ("text")>>
            if(command.type.lower() == "print".lower()):
                printYellow("    " + command.text)

            ###------VISIBILITY------###

            #<<show ("objectName")>> (this shows an object with the name if it exists)
            elif(command.type.lower() == "show".lower()):
                self.SetVisible(command.args[0], True)
            #<<hide ("objectName")>> (this shows an object with the name if it exists)
            elif(command.type.lower() == "hide".lower()):
                self.SetVisible(command.args[0], False)

            ###------QUICK ACTION MAPPINGS------###

            #<<sound ("soundMappingName")>>
            elif(command.type.lower() == "sound".lower()):
                self.soundUsedThisLine = True
                self.PlaySoundFromMapping(command.args[0])

            #<<animation ("animationMappingName")>>
            elif(command.type.lower() == "animation".lower()):
                self.animationUsedThisLine = True
                self.PlayAnimationFromMapping(command.args[0])
                
            #<<transform ("transformMappingName")>>
            elif(command.type.lower() == "transform".lower()):
                self.transformUsedThisLine = True
                self.PlayTransformFromMapping(command.args[0])
                
            #<<morph ("morphMappingName")>>
            elif(command.type.lower() == "morph".lower()):
                self.PlayMorphFromMapping(command.args[0])

            #<<url ("urlMappingName")>>
            elif(command.type.lower() == "url".lower()):
                self.PlayUrlFromMapping(command.args[0])

            #<<image ("imageMappingName")>>
            elif(command.type.lower() == "image".lower()):
                self.imageUsedThisLine = True
                self.PlayImageFromMapping(command.args[0])

            #<<video ("imageMappingName")>>
            elif(command.type.lower() == "video".lower()):
                self.videoUsedThisLine = True
                self.PlayVideoFromMapping(command.args[0])

        #If moving, then play walk animation if enabled. 
        if(self.transformUsedThisLine):
            if(USE_DEFAULT_ANIMATIONS):
                self.PlayAnimation(ANIM_WALK)
            self.transformTimer = TRANSFORM_TIMER
        #else: #If not moving, reset transform:
        #    self.PlayTransform(self.lastTransform)

    # ------------------------------------------ #
    # -------------BUTTON CREATION-------------- #
    # ------------------------------------------ #

    def createNewButtons(self, line):
        self.createSpeechBubbleCard(line)
        self.createButtonPanel(line)
        self.runCommands(line)
        
    def clearButtons(self):
        self.ClearCommandProperties()
        self.commands = []

    def createSpeechBubbleCard(self, line):
        self.speech = line.text
        self.speechIndex = 0

        self.speechBubble = Card(
            object_id=NPC_NAME + "_speechBubbleCard",
            
            title=NPC_NAME,
            imgCaption=NPC_NAME,

            body=self.speech,
            bodyAlign="center",

            fontSize = 0.05,

            img = NPC_ICON_URL,
            imgDirection="left",
            imgSize="contain", #cover, contain, stretch
            
            widthScale=0.5,

            position=SPEECH_BUBBLE_POSITION,
            scale=SPEECH_BUBBLE_SCALE,
            parent=self.npc,
            persist = True
        )
        self.scene.add_object(self.speechBubble) # add the box
        
        self.speechBubble.data["textImageRatio"] = 2.5

        self.speechBubble.data["remote-render"] = {"enabled": False}
        self.scene.update_object(self.speechBubble) # add the box
        

        return self.speechBubble



    def buttonPanelHandler(self, _scene, evt, _msg):
        if evt.type == "buttonClick":
            buttonName = evt.data.buttonName
            buttonIndex = evt.data.buttonIndex
            
            printCyan("  Choice Button with text \"" + buttonName + "\" and index " + str(buttonIndex) + " pressed!")

            if(buttonName == "[Next]" and buttonIndex == 0):
                self.resetTimer = RESET_TIME

                printCyan("  Next Button Pressed!")
                
                self.advanceToNextLine()

                if(USE_DEFAULT_SOUNDS):
                    self.PlaySound(SOUND_NEXT)  
            
            else:   
                self.resetTimer = RESET_TIME

                printCyan("  Choice Button with text \"" + buttonName + "\" and index " + str(buttonIndex) + " pressed!")

                choiceIndex = len(self.dialogue.currentNode.lines[self.dialogue.currentNode.currentLineIndex].choices)-buttonIndex

                choiceText = self.dialogue.currentNode.lines[self.dialogue.currentNode.currentLineIndex].choices[buttonIndex].text
                choiceNodeName = self.dialogue.currentNode.lines[self.dialogue.currentNode.currentLineIndex].choices[buttonIndex].node
                
            
                self.gotoNodeWithName(choiceNodeName)

                if(USE_DEFAULT_SOUNDS):
                    self.PlaySound(SOUND_CHOICE)




    def createButtonPanel(self, line):
        

        buttonTexts = []
        choices = line.choices        
        if(len(choices) > 0): 
            for c in range(len(choices)):                
                buttonTexts.append(choices[c].text)
        else: 
            buttonTexts = ["[Next]"]


        self.buttonPanel = ButtonPanel(
            object_id=NPC_NAME + "(Buttons)",

           
            buttons=buttonTexts,
            
            font="Roboto-Mono",

            position=CHOICE_BUBBLE_POSITION,
            rotation=CHOICE_BUBBLE_ROTATION,
            scale=CHOICE_BUBBLE_SCALE,
            
            evt_handler=self.buttonPanelHandler,
            parent=self.npc,
            vertical=True,

            persist=True
        )
        self.scene.add_object(self.buttonPanel)

        self.buttonPanel.data["remote-render"] = {"enabled": False}
        self.scene.update_object(self.buttonPanel) # add the box
        

    def randomUUID(self, n = 6):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

    def checkIfArenaObjectExists(self, obj):
        if(obj != None):
            return self.checkIfArenaObjectIDExists(obj.object_id)
        return False

    def checkIfArenaObjectIDExists(self, id):
        if(id != None):
            if(self.scene.all_objects.get(id) != None):
                return True
        return False

    # ------------------------------------------ #
    # ------------EVENT PROCESSING-------------- #
    # ------------------------------------------ #

    #functions to control choice button click behaviour
    def onClickChoiceButton(self, scene, evt, msg):
        if evt.type == "mousedown":
            
            self.resetTimer = RESET_TIME

            choiceButtonID = msg["object_id"]
            filterLen = len(self.npc.object_id + "_choiceButton_") + UUID_LEN + 1

            choiceButtonNumber = int(choiceButtonID[filterLen:])
            choiceText = self.dialogue.currentNode.lines[self.dialogue.currentNode.currentLineIndex].choices[choiceButtonNumber].text
            choiceNodeName = self.dialogue.currentNode.lines[self.dialogue.currentNode.currentLineIndex].choices[choiceButtonNumber].node
            
            printCyan("  Choice Button with text \"" + choiceText + "\" pressed!")
                        
            self.gotoNodeWithName(choiceNodeName)

            if(USE_DEFAULT_SOUNDS):
                self.PlaySound(SOUND_CHOICE)

    #functions to control choice button click behaviour
    def onClickNextButton(self, scene, evt, msg):
        if evt.type == "mousedown":
            self.resetTimer = RESET_TIME

            printCyan("  Next Button Pressed!")
            
            self.advanceToNextLine()

            if(USE_DEFAULT_SOUNDS):
                self.PlaySound(SOUND_NEXT)

    #functions to control link button click behaviour
    def onClickLinkButton(self, scene, evt, msg):
        if evt.type == "mousedown":
            
            printCyan("  Link Button Pressed!")
            
            if(USE_DEFAULT_SOUNDS):
                self.PlaySound(SOUND_NEXT)


    def gotoNodeWithName(self, nodeName):
        nodeIndex = self.dialogue.getNodeIndexFromString(nodeName)
        if(nodeIndex >= 0):
            self.gotoNodeWithIndex(nodeIndex)
            printBlueB("Going to node with name \"" + nodeName + "\"...")
        else:
            printWarning("No node with name \"" + nodeName + "\" exists! Ignoring gotoNodeWithName() request.")

    def gotoNodeWithIndex(self, nodeIndex):
        if(0 <= nodeIndex and nodeIndex < len(self.dialogue.nodes)):          
            self.clearButtons()    
            self.dialogue.currentNode = self.dialogue.nodes[nodeIndex]
            self.dialogue.currentNode.currentLineIndex = 0
            self.createNewButtons(self.dialogue.currentNode.lines[0])
        else:
            printWarning("No node with index [" + str(nodeIndex) + "] exists! Ignoring gotoNodeWithIndex() request.")
        
    def advanceToNextLine(self):
        self.clearButtons()
        self.dialogue.currentNode.currentLineIndex = self.dialogue.currentNode.currentLineIndex + 1

        if(self.dialogue.currentNode.currentLineIndex < len(self.dialogue.currentNode.lines)):
            self.createNewButtons(self.dialogue.currentNode.lines[self.dialogue.currentNode.currentLineIndex])
        elif(self.dialogue.currentNode.currentLineIndex == len(self.dialogue.currentNode.lines)):
            printRedB("\n(---Finished NPC interaction.---)")

    def OnClickReloadCurrentLine(self):
        if evt.type == "mousedown":
            self.reloadCurrentLine()

    def reloadCurrentLine(self):
        printGreenB("\n(---Reloaded current line:---)")
        self.clearButtons()
        
        if(self.dialogue.currentNode.currentLineIndex < len(self.dialogue.currentNode.lines)):
            self.createNewButtons(self.dialogue.currentNode.lines[self.dialogue.currentNode.currentLineIndex])
        
    