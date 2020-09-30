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

# poster placement settings

theme = 6  # we are generating for this theme
dist = 40  # distance between posters
persist = True  # persist flag for generate objects
originx = -30  # start coordinate in x
originz = 2  # start coordinate in z
wallcolor = (100, 100, 130)  # color of the poster wall
dirx = 1  # 1 or -1 to define direction of the grid
dirz = -1  # 1 or -1 to define direction of the grid


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

SCENE = "theme" + str(theme)
REALM = 'realm'
MQTTH = 'arena.andrew.cmu.edu'

# init the ARENA library

arena.init(MQTTH, REALM, SCENE)

posterData = None
with open('poster-data.json') as dataFile:
    posterData = json.load(dataFile)

pcount = 0
for poster in posterData:
    print(poster['name'], poster['theme'])
    if poster['theme'] == theme:
        pcount += 1

if pcount <= 4:
    gridSize = 3
elif pcount <= 9:
    gridSize = 3
elif pcount <= 16:
    gridSize = 4
elif pcount <= 25:
    gridSize = 5
elif pcount <= 36:
    gridSize = 6

print (
    'theme=',
    theme,
    'pcount=',
    pcount,
    'gridSize=',
    gridSize,
    )

# parent of the entire area

paparentName = 't' + str(theme) + '_poster_area_parent'
postersParent = arena.Object(
    objName=paparentName,
    objType=arena.Shape.cube,
    location=(originx, 0, originz),
    transparency=arena.Transparency(True, 0),
    clickable=False,
    persist=persist,
    )

pindex = 0
for poster in posterData:
    if poster['theme'] == theme:
        print(poster['name'], poster['theme'])

        l = pindex % gridSize
        c = pindex // gridSize

        pindex += 1

        print(l, c)

        prootName  = 't' + str(theme) + '_poster' + str(pindex) + '_root'
        pwallName  = 't' + str(theme) + '_poster' + str(pindex) + '_wall'
        pimgName   = 't' + str(theme) + '_poster' + str(pindex) + '_img'
        plightName = 't' + str(theme) + '_poster' + str(pindex) + '_light'
        plblName   = 't' + str(theme) + '_poster' + str(pindex) + '_lbl'
        psclnkName = 't' + str(theme) + '_poster' + str(pindex) + '_sclink'

        # parent of the poster

        pRoot = arena.Object(
            objName=prootName,
            objType=arena.Shape.cube,
            location=(l * dist * dirx, 0, c * dist * dirz),
            transparency=arena.Transparency(True, 0),
            parent=paparentName,
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
            url='store/users/conixadmin/posters/poster_imgs/'
                + poster['posterfile'],
            objType=arena.Shape.image,
            scale=(4, 4, 4),
            location=(-0.3, 2.2, 0),
            rotation=(0, 0.7071, 0, -0.7071),
            clickable=False,
            parent=prootName,
            persist=persist,
            )

        plight = arena.Object(
            objName=plightName,
            objType=arena.Shape.light,
            location=(0, 2, 1.50),
            rotation=(0, 0, 1, 0),
            data='{"light":{"type":"point","intensity":"0.5"}}',
            clickable=False,
            parent=prootName,
            persist=persist)

        plbl = arena.Object(
            objName=plblName,
            objType=arena.Shape.text,
            scale=(0.5,0.5,0.5),
            location=(-0.35, 4.3, 0),
            rotation=(0, 0.7071, 0, -0.7071),
            clickable=False,
            data='{"text":"' + poster['authors'] + '"}',
            color=(252, 132, 3),
            parent=prootName,
		    persist=persist)   
        
        psclink = arena.Object(
            objName=psclnkName,
            url='store/users/conixadmin/posters/scatalog-'+str(theme)+'.png',
            objType=arena.Shape.image,
            scale=(.5, .5, .5),
            location=(-0.3, 2.2, 2.5),
            rotation=(0, 0.7071, 0, -0.7071),
            clickable=True,
            parent=prootName,
            persist=persist,
            data='{"goto-url": { "on": "mousedown", "url": "https://conix.io/conix-2020-review-demos-posters?theme=' + str(theme) + '"} } '
            )
        

# move the group of objects
# agentParent.update(location=(3, 0, -10))

# This is the main ARENA event handler
# Everything after this should be in callbacks

print('starting main loop')
arena.handle_events()

# agentParent.delete()
