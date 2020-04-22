import getpass
import sys
import telnetlib
import time
import json
import arena
import re

HOST = "oz.andrew.cmu.edu"
SCENE = "agr-kitchen"

pantry_state=0
pendant_state=0

# This function opens a telnet connection to the lutron caseta system
# Default username and password
def lutron_connect():
     HOST = "192.168.159.183"
     # user = raw_input("Enter your remote account: ")
     # password = getpass.getpass()
     user = "lutron"
     password = "integration"

     global tn
     tn = telnetlib.Telnet(HOST)
     tn.read_until(b"login: ")
     tn.write(b"lutron\n")
     if password:
         tn.read_until(b"password: ")
         tn.write(b"integration\n")
     return 1


# This toggles the lutron light, updates the object color and returns the new state
# The tn.write functions are sending an esoteric lutron command over the telnet session
def light_toggle(light_obj,light_state,light_id):
     if light_state==0:
          b= bytes("#output,"+light_id+",1,100\n", encoding='utf-8')
          tn.write(b)
          light_obj.update(color=(0, 255, 0))
          light_state=1
     else:
          b= bytes("#output,"+light_id+",1,0\n", encoding='utf-8')
          tn.write(b)
          light_state=0
          light_obj.update(color=(255, 0, 0))
     return light_state

# This function is called to help with changing the brightness on mouse hover events
# 255 is bright and 150 (see below is dark)
def light_select(light_obj,light_state):
     if light_state==1:
          light_obj.update(color=(0, 255, 0))
     else:
          light_obj.update(color=(255, 0, 0))

# This function is called to help with changing the brightness on mouse hover events
def light_unselect(light_obj,light_state):
     if light_state==1:
          light_obj.update(color=(0, 150, 0))
     else:
          light_obj.update(color=(150, 0, 0))


# This is the MQTT message callback function for the scene
# You can hijack the mouse events here and then map them to lighting functions
def scene_callback(msg):
     global pantry_state 
     global pantry_obj
     global pendant_state 
     global pendant_obj

     print(msg)
     jsonMsg = json.loads(msg)
     if jsonMsg["action"] != "clientEvent":
          return
     # Check for mouseenter events
     # the obj vars are arena objects
     # the state vars are just ints that hold if the light is on/off
     if jsonMsg["type"] == "mouseenter":
          name = jsonMsg["object_id"]
          if name=="pendant":
               light_select(pendant_obj,pendant_state)
          if name=="pantry":
               light_select(pantry_obj,pantry_state)

     # Check for mouseleve events
     if jsonMsg["type"] == "mouseleave":
          name = jsonMsg["object_id"]
          if name=="pendant":
               light_unselect(pendant_obj,pendant_state)
          if name=="pantry":
               light_unselect(pantry_obj,pantry_state)

     if jsonMsg["type"] == "mousedown":
          name = jsonMsg["object_id"]
          if name=="pendant":
               # The "3" is the lutron id for that light
               pendant_state=light_toggle(pendant_obj,pendant_state,"3")
          if name=="pantry":
               # The "4" is the lutron id for that light
               pantry_state=light_toggle(pantry_obj,pantry_state,"4")

# open a telnet (sigh) connection to to lutron caseta system
lutron_connect()

arena.init(HOST, "realm", SCENE,scene_callback)
print("setting up objects")

arena.Object(objType=arena.Shape.cube, objName="origin", location=(0,0,0), color=(0,0,255),scale=(0.1,0.1,0.1), persist=True);
# Create the clickable object for the pantry light.  Added in transparency using json bypass
# Object locations are hardcoded based on April Tag on the floor in Anthony's house
pantry_obj=arena.Object(objType=arena.Shape.sphere, objName="pantry", location=(2.5,2.3,-0.6), color=(150,0,0),scale=(0.1,0.1,0.1), data='{"material": {"transparent":true,"opacity": 0.5}}', clickable=True, persist=True);
# Create the clickable object for the pendant light.  Added in transparency using json bypass
pendant_obj=arena.Object(objType=arena.Shape.sphere, objName="pendant", location=(3.1,2.0,-3.2), color=(150,0,0),scale=(0.1,0.1,0.1), data='{"material": {"transparent":true,"opacity": 0.5}}', clickable=True, persist=True);


print("starting main loop")
arena.handle_events()



#pantry_on()
#time.sleep(2)
#pantry_off()

