
from ColorPrinter import *
from config import *
import json

import sys
if(USE_DEV_ARENAPY):
    sys.path.append(ARENAPY_DEV_PATH)

from arena import *

 #---JSON IMPORTER HELPER FUNCTIONS---#
def importSound(json):
    _volume = json["volume"]
    _src = json["src"]
    return Sound(volume = _volume, autoplay=True, positional=True, src = _src)

def importAnimation(json):
    _clip = json["clip"]
    _loop = json["loop"]
    _crossFadeDuration = json["crossFadeDuration"]
    _timeScale = json["timeScale"]
    return AnimationMixer(clip = _clip, loop = _loop, timeScale = _timeScale, crossFadeDuration = _crossFadeDuration)

def importMorph(json):
    morphs = []
    for i in range(len(json)):
        _morphtarget = json[i]["morphtarget"]
        _value = json[i]["value"]
        morphs.append( Morph(_morphtarget,_value) )
    return morphs

def importTransform(json):
    px = json["position"]["x"]
    py = json["position"]["y"]
    pz = json["position"]["z"]
    rx = json["rotation"]["x"]
    ry = json["rotation"]["y"]
    rz = json["rotation"]["z"]
    return [              
        Animation(property="position", end=Position(px,py,pz), easing="easeInOutSine", dur=CFG.TRANSFORM_TIMER),  
        Animation(property="rotation", end=Rotation(rx,ry,rz), easing="linear", dur=CFG.TRANSFORM_TIMER*0.5)
    ]

def importGotoUrl(json):
    _url = json["url"]
    _dest = json["dest"]
    return GotoUrl(dest=_dest, on="mouseup", url=_url)

class IMG:
    def __init__(self, src, w, h, size):
        self.src = src
        self.w = w
        self.h = h
        self.size = size
def importImage(json):
    _src = json["src"]
    _w = json["w"]
    _h = json["h"]
    return IMG(src = _src, w = _w, h = _h, size = 1)

def importVideo(json):
    _src = json["src"]
    _w = json["w"]
    _h = json["h"]
    return Material(src = _src, transparent = True, opacity = CFG.PLANE_OPACITY, w = _w, h = _h, size = 1)

 #---MAPPINGS CLASS, CONTAINS ALL MAPPINGS FROM DIALOGUE FILE TO COMMANDS---#
class Mappings:
    def __init__(self):

        # Open config file
        f = open(MAPPINGS_FILENAME)
        jsonString = f.read()
        mappingsJson = json.loads(jsonString) 

        #---PRE-DEFINED DEFAULT ACTIONS (triggered when talking/moving/clicking/etc)---#

        #DEFAULT SOUNDS (set these to None if you don't want default sound effects, or set USE_DEFAULT_SOUNDS = False)
        self.SOUND_NEXT    = importSound(mappingsJson["DEFAULTS"]["SOUND"]["NEXT"])
        self.SOUND_CHOICE  = importSound(mappingsJson["DEFAULTS"]["SOUND"]["CHOICE"])
        self.SOUND_ENTER   = importSound(mappingsJson["DEFAULTS"]["SOUND"]["ENTER"])
        self.SOUND_EXIT    = importSound(mappingsJson["DEFAULTS"]["SOUND"]["EXIT"])
        self.SOUND_IMAGE   = importSound(mappingsJson["DEFAULTS"]["SOUND"]["IMAGE"])
        self.SOUND_TALKING = importSound(mappingsJson["DEFAULTS"]["SOUND"]["TALKING"])
        self.SOUND_WALKING = importSound(mappingsJson["DEFAULTS"]["SOUND"]["WALKING"]) #Not applied yet, TODO

        #DEFAULT ANIMATIONS (set these to None if you don't want default animations, or set USE_DEFAULT_ANIMATIONS = False)
        self.ANIM_IDLE = importAnimation(mappingsJson["DEFAULTS"]["ANIMATION"]["IDLE"])
        self.ANIM_WALK = importAnimation(mappingsJson["DEFAULTS"]["ANIMATION"]["WALK"])
        self.ANIM_TALK = importAnimation(mappingsJson["DEFAULTS"]["ANIMATION"]["TALK"])

        #DEFAULT MORPHS (set these to None if you don't want default morphs, or set USE_DEFAULT_MORPHS = False)
        self.MORPH_OPEN  =     importMorph(mappingsJson["DEFAULTS"]["MORPH"]["OPEN"])
        self.MORPH_CLOSE =     importMorph(mappingsJson["DEFAULTS"]["MORPH"]["CLOSE"])
        self.MORPH_BLINK_ON =  importMorph(mappingsJson["DEFAULTS"]["MORPH"]["BLINK_ON"])
        self.MORPH_BLINK_OFF = importMorph(mappingsJson["DEFAULTS"]["MORPH"]["BLINK_ON"])
        self.MORPH_RESET =     importMorph(mappingsJson["DEFAULTS"]["MORPH"]["RESET"])

        #DEFAULT VIDEO LOADING FRAME
        self.DEFAULT_VIDEO_FRAME_OBJECT = mappingsJson["DEFAULTS"]["VIDEO_FRAME_OBJECT"]

        #DEFAULT TRANSFORM 
        self.TRANSFORM_RESET = [ Animation(property="position", end=CFG.ROOT_POSITION, easing="easeInOutSine", dur=CFG.TRANSFORM_TIMER), 
                                 Animation(property="rotation", end=CFG.ROOT_ROTATION, easing="linear", dur=CFG.TRANSFORM_TIMER*0.5) ]

        #---PRE-DEFINED QUICK ACTION MAPPINGS (for use in Yarn, because who wants to type all this out every time?)---#

        # Shorthand sound names mapped to (Sound URL, volume, loop)
        # --Sound Schema: https://docs.arenaxr.org/content/schemas/message/sound.html
        # --Sound Example: https://github.com/arenaxr/arena-py/blob/master/examples/attributes/sound.py 
        self.soundMappings = {}
        for mapping in mappingsJson["SOUND_MAPPINGS"]:
            self.soundMappings[mapping["NAME"]] = importSound(mapping["SOUND"])

        # Shorthand animation names mapped to (animationName, crossFade, timeScale, loopMode['once', 'repeat', 'pingpong'])
        # --AnimationMixer Schema: https://docs.arenaxr.org/content/schemas/message/animation-mixer.html 
        # --AnimationMixer Example: https://github.com/arenaxr/arena-py/blob/master/examples/attributes/animation_mixer.py 
        self.animationMappings = {}
        for mapping in mappingsJson["ANIMATION_MAPPINGS"]:
            self.animationMappings[mapping["NAME"]] = importAnimation(mapping["ANIMATION"])

        # Shorthand transform names mapped to transform action over time
        # --Animation Schema: https://docs.arenaxr.org/content/schemas/message/animation.html 
        # --Animation Example: https://github.com/arenaxr/arena-py/blob/master/examples/attributes/animation.py 
        self.transformMappings = {}
        for mapping in mappingsJson["TRANSFORM_MAPPINGS"]:
            self.transformMappings[mapping["NAME"]] = importTransform(mapping["TRANSFORM"])

        # Shorthand morph names mapped to list of morph target names with weights
        # --Morph Schema: https://docs.arenaxr.org/content/python/animations.html#gltf-morphs
        # --Morph Example: https://github.com/arenaxr/arena-py/blob/master/examples/attributes/morph.py
        self.morphMappings = {}
        for mapping in mappingsJson["MORPH_MAPPINGS"]:
            self.morphMappings[mapping["NAME"]] = importMorph(mapping["MORPH"])

        # Shorthand url names mapped to (Website URL, volume, loop)
        # --Url Schema: https://docs.arenaxr.org/content/schemas/message-examples.html#goto-url 
        # --Url Example: https://github.com/arenaxr/arena-py/blob/master/examples/attributes/goto_url.py 
        self.urlMappings = {}
        for mapping in mappingsJson["URL_MAPPINGS"]:
            self.urlMappings[mapping["NAME"]] = importGotoUrl(mapping["GOTOURL"])

        # Shorthand image names mapped to (Website URL, volume, loop)
        # --Url Schema: https://github.com/arenaxr/arena-py/blob/master/examples/objects/image.py
        # --Url Example: https://docs.arenaxr.org/content/schemas/message/image.html
        self.imageMappings = {}
        for mapping in mappingsJson["IMAGE_MAPPINGS"]:
            self.imageMappings[mapping["NAME"]] = importImage(mapping["IMAGE"])

        # Shorthand image names mapped to (Website URL, volume, loop)
        # --Url Schema: https://docs.arenaxr.org/content/schemas/message/material.html#material
        # --Url Example: https://github.com/arenaxr/arena-py/blob/master/examples/attributes/material.py
        self.videoMappings = {}
        for mapping in mappingsJson["VIDEO_MAPPINGS"]:
            self.videoMappings[mapping["NAME"]] = importVideo(mapping["VIDEO"])

MAP = Mappings()