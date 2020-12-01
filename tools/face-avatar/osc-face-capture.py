"""Small example OSC server

This program listens to several addresses, and prints some information about
received packets.
"""
import argparse
import math

from pythonosc import dispatcher
from pythonosc import osc_server

import arena
import random
import time
import signal
import json
from scipy.spatial import distance

HOST = "oz.andrew.cmu.edu"
SCENE = "face-agr"
OBJECT = "face-agr-model"

users = {}
SCALE_FACTOR = 100


anims2=[
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
    "tongue_out"
    ]

anims=[
    "shapes.browInnerUp",
    "shapes.browDown_L",
    "shapes.browDown_R",
    "shapes.browOuterUp_L",
    "shapes.browOuterUp_R",
    "shapes.eyeLookUp_L",
    "shapes.eyeLookUp_R",
    "shapes.eyeLookDown_L",
    "shapes.eyeLookDown_R",
    "shapes.eyeLookIn_L",
    "shapes.eyeLookIn_R",
    "shapes.eyeLookOut_L",
    "shapes.eyeLookOut_R",
    "shapes.eyeBlink_L",
    "shapes.eyeBlink_R",
    "shapes.eyeSquint_L",
    "shapes.eyeSquint_R",
    "shapes.eyeWide_L",
    "shapes.eyeWide_R",
    "shapes.cheekPuff",
    "shapes.cheekSquint_L",
    "shapes.cheekSquint_R",
    "shapes.noseSneer_L",
    "shapes.noseSneer_R",
    "shapes.jawOpen",
    "shapes.jawForward",
    "shapes.jawLeft",
    "shapes.jawRight",
    "shapes.mouthFunnel",
    "shapes.mouthPucker",
    "shapes.mouthLeft",
    "shapes.mouthRight",
    "shapes.mouthRollUpper",
    "shapes.mouthRollLower",
    "shapes.mouthShrugUpper",
    "shapes.mouthShrugLower",
    "shapes.mouthClose",
    "shapes.mouthSmile_L",
    "shapes.mouthSmile_R",
    "shapes.mouthFrown_L",
    "shapes.mouthFrown_R",
    "shapes.mouthDimple_L",
    "shapes.mouthDimple_R",
    "shapes.mouthUpperUp_L",
    "shapes.mouthUpperUp_R",
    "shapes.mouthLowerDown_L",
    "shapes.mouthLowerDown_R",
    "shapes.mouthPress_L",
    "shapes.mouthPress_R",
    "shapes.mouthStretch_L",
    "shapes.mouthStretch_R",
    "tongue_out"
    ]

anims_w = []
anims_hrq = []

def anims_init():
  i=0
  anims_hrq.append(0.0)
  anims_hrq.append(0.0)
  anims_hrq.append(0.0)
  anims_hrq.append(1.0)
  while i < len(anims):
    anims_w.append(0.0)
    i+=1

def draw_blendshape_face():

  morphStr = '{'
  i=0
  while i < (len(anims)-1):
    morphStr +='"gltf-morph__' + str(i) + '":{"morphtarget":"' + anims[i] + '","value":"' + str(anims_w[i]) + '"},'
    i+=1

  # morphStr +='"gltf-morph__' + str(i) + '":{"morphtarget":"' + str(i) + '","value":"' + str(anims_w[i]) + '"}}'
  morphStr +='"gltf-morph__' + str(i) + '":{"morphtarget":"' + anims[i] + '","value":"' + str(anims_w[i]) + '"}}'

  print("Rotation:" + str(anims_hrq[0]) + str(anims_hrq[1]) + str(anims_hrq[2]) + str(anims_hrq[3]))
  #print(morphStr)
  print("Frame Publish")
  obj = arena.Object(
   rotation=(anims_hrq[0],anims_hrq[1],anims_hrq[2],anims_hrq[3]), # quaternion value roughly between -.05 and .05
 # rotation=(0,0,0.6-openness,1), # quaternion value roughly between -.05 and .05
   objName=OBJECT,
#   url="models/Facegltf/sampledata.gltf", 
   objType=arena.Shape.gltf_model,
   scale=(15,15,15),
   location=(0,2,-5),
   data = morphStr
   )
        

frame_skip=0

def capture_w(unused_addr, args, index, w):
  global frame_skip
  val=float(w)
  anims_w[index]=val
  if index == 0:
    frame_skip+=1
    if frame_skip>4:
      draw_blendshape_face()
      frame_skip=0


def capture_hrq(unused_addr, args, x, y, z, w ):
  anims_hrq[0]=float(x)
  anims_hrq[1]=float(y)
  anims_hrq[2]=float(z)
  anims_hrq[3]=float(w)



if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip",
      default="127.0.0.1", help="The ip to listen on")
  parser.add_argument("--port",
      type=int, default=5005, help="The port to listen on")
  args = parser.parse_args()

  dispatcher = dispatcher.Dispatcher()
#  dispatcher.map("/HRQ", print)
  dispatcher.map("/HRQ", capture_hrq, "x", "y","z","w")
#  dispatcher.map("/HT", print)
#  dispatcher.map("/ELR", print)
#  dispatcher.map("/ERR", print)
#  dispatcher.map("/W",  print)
  dispatcher.map("/W", capture_w, "index", "w")
#  dispatcher.map("/filter", print)
#  dispatcher.map("/volume", print_volume_handler, "Volume")
#  dispatcher.map("/logvolume", print_compute_handler, "Log volume", math.log)

  arena.init(HOST, "realm", SCENE)
  anims_init()

  obj = arena.Object(
   rotation=(0,0,0.0,1), # quaternion value roughly between -.05 and .05
   objName=OBJECT,
   # url="models/Facegltf/sampledata.gltf", 
   objType=arena.Shape.gltf_model,
#   scale=(40,40,40),
#   location=(0,10,10),
   )
 

  draw_blendshape_face() 
  server = osc_server.ThreadingOSCUDPServer(
      (args.ip, args.port), dispatcher)
  print("Serving on {}".format(server.server_address))


  # Setup ARENA and callback
#  arena.init(HOST, "realm", SCENE, callback=callback)
#  arena.handle_events()

  # Launch OSC server 
  server.serve_forever()