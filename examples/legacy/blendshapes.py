# blendshapes.py
#
# animate the bones of the 'Facegltf/sampledata.gltf' GLTF model
# bone names came from inspecting scene.gltf
# assumes the model 'izzy' already exists in ARENA scene 'cesium'

import arena
import random
import time
import signal

HOST = "oz.andrew.cmu.edu"
SCENE = "sampledata"
OBJECT = "face"

anims=[
    "blendShape1.browInnerUp",
    "blendShape1.browDown_L",
    "blendShape1.browDown_R",
    "blendShape1.browOuterUp_L",
    "blendShape1.browOuterUp_R",
    "blendShape1.eyeLookUp_L",
    "blendShape1.eyeLookUp_R",
    "blendShape1.eyeLookDown_L",
    "blendShape1.eyeLookDown_R",
    "blendShape1.eyeLookIn_L",
    "blendShape1.eyeLookIn_R",
    "blendShape1.eyeLookOut_L",
    "blendShape1.eyeLookOut_R",
    "blendShape1.eyeBlink_L",
    "blendShape1.eyeBlink_R",
    "blendShape1.eyeSquint_L",
    "blendShape1.eyeSquint_R",
    "blendShape1.eyeWide_L",
    "blendShape1.eyeWide_R",
    "blendShape1.cheekPuff",
    "blendShape1.cheekSquint_L",
    "blendShape1.cheekSquint_R",
    "blendShape1.noseSneer_L",
    "blendShape1.noseSneer_R",
    "blendShape1.jawOpen",
    "blendShape1.jawForward",
    "blendShape1.jawLeft",
    "blendShape1.jawRight",
    "blendShape1.mouthFunnel",
    "blendShape1.mouthPucker",
    "blendShape1.mouthLeft",
    "blendShape1.mouthRight",
    "blendShape1.mouthRollUpper",
    "blendShape1.mouthRollLower",
    "blendShape1.mouthShrugUpper",
    "blendShape1.mouthShrugLower",
    "blendShape1.mouthClose",
    "blendShape1.mouthSmile_L",
    "blendShape1.mouthSmile_R",
    "blendShape1.mouthFrown_L",
    "blendShape1.mouthFrown_R",
    "blendShape1.mouthDimple_L",
    "blendShape1.mouthDimple_R",
    "blendShape1.mouthUpperUp_L",
    "blendShape1.mouthUpperUp_R",
    "blendShape1.mouthLowerDown_L",
    "blendShape1.mouthLowerDown_R",
    "blendShape1.mouthPress_L",
    "blendShape1.mouthPress_R",
    "blendShape1.mouthStretch_L",
    "blendShape1.mouthStretch_R",
]

arena.init(HOST, "realm", SCENE)

def signal_handler(sig, frame):
    exit()

signal.signal(signal.SIGINT, signal_handler)

counter = 0
while True:
#    theanim = '{"animation-mixer": {"clip": "'+ anims[counter] + '"}}'
    counter = counter + 1

    rando = random.random()
    anim = anims[counter % len(anims)]
    print (anim, rando)

    obj = arena.Object(
        objName=OBJECT,
        objType=arena.Shape.gltf_model,
        scale=(40,40,40),
        location=(0,3,10),
#        bone_id = bones[random.randint(0,len(bones)-1)]
#        data=theanim
        data ='{"gltf-morph": {"morphtarget": "'+
        anim +
        '", "value": ' +
        str(rando) +
        '}}'
        )
    time.sleep(0.5)
exit()

