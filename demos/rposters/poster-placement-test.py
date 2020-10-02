#!/usr/bin/python
# -*- coding: utf-8 -*-

# poster placement
#

import time
import arena
import random
import os
import json

import atexit

# To run in ARTS, these parameters are passed in as environmental variables.
# export SCENE=thescene
# export REALM=realm
# export MQTTH=arena.andrew.cmu.edu

def agent_handler(event=None):
    global agent1
    global agentParent
    print('agent handler callback!')

# Pull in the SCENE, MQTT and REALM parameters from environmental variables
# TODO: Add commandline overide
# if (os.environ.get('SCENE') is not None) and (os.environ.get('REALM') is not None) and (os.environ.get('MQTTH') is not None):
#    SCENE = os.environ["SCENE"]
#    HOST = os.environ["MQTTH"]
#    REALM = os.environ["REALM"]
#    print("Loading:" + SCENE + "," + REALM + "," + HOST)
# else:
#    print( "You need to set SCENE, MQTTH and REALM as environmental variables to specify the program target")
#    exit(-1)


SCENE = 'newtest'
REALM = 'realm'
MQTTH = 'arena.andrew.cmu.edu'

# init the ARENA library

arena.init(MQTTH, REALM, SCENE)
theme = 1
pindex = 1
persist = True
wallcolor = (100, 100, 130)

# parent of the poster

prootName = 't' + str(theme) + '_poster' + str(pindex) + '_root'
pwallName = 't' + str(theme) + '_poster' + str(pindex) + '_wall'
pimgName = 't' + str(theme) + '_poster' + str(pindex) + '_img'
plightName = 't' + str(theme) + '_poster' + str(pindex) + '_light'
plblName = 't' + str(theme) + '_poster' + str(pindex) + '_lbl'

pRoot = arena.Object(
    objName=prootName,
    objType=arena.Shape.cube,
    location=(0, 0, 0),
    transparency=arena.Transparency(True, 0),
    clickable=False,
    persist=persist,
)

pwall = arena.Object(
    objName=pwallName,
    objType=arena.Shape.cube,
    location=(0, 0, 0),
    scale=(6, 9, .5),
    rotation=(0, 0.7071, 0, 0.7071),
    color=wallcolor,
    parent=prootName,
    clickable=False,
    persist=persist,
)

pimg = arena.Object(
    objName=pimgName,
    url='store/users/conixadmin/posters/poster_imgs/CONIX-dft.jpg',
    objType=arena.Shape.image,
    scale=(4, 4, 4),
    location=(-0.3, 2.2, 0),
    rotation=(0, 0.7071, 0, -0.7071),
    clickable=False,
    parent=prootName,
    persist=persist,
)

plbl = arena.Object(
    objName=plblName,
    objType=arena.Shape.text,
    scale=(0.5, 0.5, 0.5),
    location=(-0.3, 0.13, 0),
    rotation=(0, 0.7071, 0, -0.7071),
    clickable=False,
    data='{"text":"'+'Theme' + str(theme) + '"}',
    color=(252, 132, 3),
    parent=prootName,
    persist=persist)

plight = arena.Object(
    objName=plightName,
    objType=arena.Shape.light,
    location=(0, 2, 1.50),
    rotation=(0, 0, 1, 0),
    data='{"light":{"type":"point","intensity":"0.5"}}',
    clickable=False,
    parent=prootName,
    persist=persist,
)

plink = arena.Object(
    objName="scatalog",
    url='store/users/conixadmin/posters/scatalog-'+str(theme)+'.png',
    objType=arena.Shape.image,
    scale=(.5, .5, .5),
    location=(-0.3, 2.2, 2.5),
    rotation=(0, 0.7071, 0, -0.7071),
    clickable=True,
    parent=prootName,
    persist=persist,
    data='{"goto-url": { "on": "mousedown", "url": "https://conix.io/conix-2020-review-demos-posters?theme=' +
        str(theme) + '"} } '
)

demob = arena.Object(
    objName="demo_sign",
    url='store/users/wiselab/models/maria_sign_board/scene-demo.gltf',
    objType=arena.Shape.gltf_model,
    scale=(.3, .3, .3),
    location=(-2, 0.8, 6),
    rotation=(0, 0.5, 0, 0.7071),
    clickable=True,
    parent=prootName,
    persist=persist,
    data='{"goto-url": { "on": "mousedown", "url": "https://arena.andrew.cmu.edu/?scene=gabe"} } '
)

demolbl = arena.Object(
    objName="demo_lbl",
    objType=arena.Shape.text,
    scale=(1.5, 1.5, 1.5),
    location=(0, -2, -.6),
    rotation=(0, 1, 0, 0),
    clickable=False,
    data='{"text":"Smart Cities Demo"}',
    color=(250, 20, 20),
    parent="demo_sign",
    persist=persist)


# move the group of objects
# agentParent.update(location=(3, 0, -10))

# This is the main ARENA event handler
# Everything after this should be in callbacks

print('starting main loop')
arena.handle_events()

# agentParent.delete()
