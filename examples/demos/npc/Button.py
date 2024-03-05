from config import *
from mappings import *
from YarnParser import *
from ColorPrinter import *

import sys
if(USE_DEV_ARENAPY):
    sys.path.append(ARENAPY_DEV_PATH)

from arena import *

from asyncio import create_subprocess_exec

class NPCButton():
    def __init__(self, scene, npc, name, text, eventHandler, position, rotation, buttonScale, textScale, color, textColor, persist):
        self.scene = scene
        self.npc = npc

        self.box = self.makeButtonBox(name, text, eventHandler, color, position, rotation, buttonTextColor=textColor, buttonScale = buttonScale, persist=persist)
        self.text = self.makeButtonText(self.box, name, text, buttonColor=textColor, buttonScale = textScale, persist=persist)

    def makeButtonText(self, button, buttonID, buttonText, 
                       buttonColor = Color(255,255,255), 
                       buttonPos = Position(0, 0, 0.6), 
                       buttonRot = Rotation(0,0,0), 
                       buttonScale = Scale(0.5, 2, 1), 
                       persist=False):
        #Create Button Text Object
        buttonText = Text(
            object_id=buttonID+"_text",
            text=buttonText,
            align="center",
                
            position=buttonPos,
            rotation=buttonRot,
            scale=buttonScale,
            
            material = Material(color = buttonColor, transparent = False, opacity=1),

            parent = button,
            persist=persist
        )
        self.scene.add_object(buttonText)
        #Return created object
        return buttonText

    def makeButtonBox(self, buttonID, buttonText, buttonHandler, 
                      buttonColor = Color(128,128,128), 
                      buttonPos = Position(0,0,0), 
                      buttonRot = Rotation(0,0,0), 
                      buttonScale = Scale(0.4, 0.08, 0.04), 
                      buttonTextColor = Color(255,255,255), 
                      persist=False):        
        #Create Button Object
        button = Box(
            object_id=buttonID,

            position=buttonPos,
            rotation=buttonRot,
            #scale=Scale(0,0,0),
            scale=buttonScale,

            material = Material(color = buttonColor, transparent = True, opacity=CHOICE_BUBBLE_OPACITY),

            evt_handler=buttonHandler,
            parent = self.npc,
            clickable=True,
            persist=persist
        )
        self.scene.add_object(button)
        #Button Appearance Animation    
        animation = Animation(property="scale", start=Scale(0,0,0), end=buttonScale, easing="easeInOutQuad", dur=CHOICE_SCALE_DURATION)
        button.dispatch_animation(animation)
        self.scene.run_animations(button)
        #Return created object
        return button