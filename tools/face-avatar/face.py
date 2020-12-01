# bendy.py
#
# animate the bones of the 'face' GLTF model from Sketchfab
# fond in models/face/scene.gltf
# bone names came from inspecting scene.gltf
# assumes the model 'face' already exists in ARENA scene 'face'

import arena
import random
import time
import signal

HOST = "oz.andrew.cmu.edu"
SCENE = "face"

bones=[
      # "Nck_01", # head rotations (similar)
      # "Hd_02",
      # "L_03", # eyes
      # "R_04",
      # "LUP_05", # eyelids
      # "RUP_06",
      # "H1_07",  # hair
      # "H2_08",
      "SM1_09", # smile
      "SM2_010",
]

arena.init(HOST, "realm", SCENE)

def randrot():
    r = round((random.random()/10 - 0.05), 3)
    #print(r)
    return r

def signal_handler(sig, frame):
    exit()

signal.signal(signal.SIGINT, signal_handler)
messages = []
counter = 0
while True:
    boneId = bones[random.randint(0,len(bones)-1)]
    print(boneId)
    obj = arena.updateBone(
        object_id="face",
        rotation=(randrot(),randrot(),randrot(),1),
        bone_id = boneId
        )
    time.sleep(0.1)
exit()
