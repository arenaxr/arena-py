# robot-arm.py
#

import time
import arena
import random
import os
import json 
import time
import threading
import signal 

pinata_loc = [ 3, 2, -10]
NUM_HITS = 10
hit_counter = NUM_HITS

# AREA for seeding location and effects
AREA_X_START = -100
AREA_X_STOP = 100
AREA_Y_START = -100
AREA_Y_STOP = 100 
NUM_BOXES = 50

kill_flag = 0

click_objects = [""]
# To run in ARTS, these parameters are passed in as environmental variables.
# export HOST=arena.andrew.cmu.edu
# export REALM=realm
# export MQTTH=arena.andrew.cmu.edu

gravity_enabled = False
GRAVITY = -25.0
vi = 0.0
t = 1.0
fire_impulse = 1

def box_callback(event=None): # gets a GenericEvent
    if event.event_type == arena.EventType.mousedown:
        # draw a ray from clicker to cube
        draw_ray(event.click_pos, event.position)

def random_color():
    rgbl=[random.uniform(0,255),random.uniform(0,255),random.uniform(0,255)]
    #random.shuffle(rgbl)
    return tuple(rgbl)

def magestic_ending():
    boxes = [""]
    for i in range(NUM_BOXES):
        x=arena.Object(
        objType=arena.Shape.cube,
        persist=False,
        objName="cube"+str(i),
        # messes up child-follow-parent pose
        physics=arena.Physics.dynamic,
        collision_listener=True,
        #transparency=arena.Transparency(True,0.5),
        impulse=arena.Impulse("mouseup",( 5,30,0),(30,1,1)),
#        location=(random.randrange(AREA_X_START,AREA_X_STOP), 10, random.randrange(AREA_Y_START,AREA_Y_STOP)),
        location=(pinata_loc[0], pinata_loc[1]+1.5, pinata_loc[2] ),
        color=random_color(),
        scale=(0.6, 0.6, 0.6),
        clickable=True,
        callback=box_callback,
        )
        boxes.append(x)
    time.sleep(10)
    for i in range(NUM_BOXES):
        x=boxes.pop()
        x.delete()

# Main Game Logic Loop
def game_thread():
    global vi
    global t
    global fire_impulse
    global gravity_enabled 
    global kill_flag 

    #cnt = 0
    while True:
        if kill_flag==1:
            print("Kill Flat!")
            return 
        if gravity_enabled is True:
            pinataParent.update(location=(pinata_loc[0],pinata_loc[1],pinata_loc[2]))
        if(fire_impulse>0):
            print("Hit!")
            t=0.1
            vi=20.0
            H = pinata_loc[1]
            fire_impulse=0
        if gravity_enabled is True:
	    #cnt+=1
            pinata_loc[1] = H + vi * t + 0.5*GRAVITY*(t*t)
            #if cnt%4==0 and pinata_loc[1]>6.0:
            if pinata_loc[1]>6.0:
                pinata_loc[0] += random.uniform(-1,1)
                pinata_loc[2] += random.uniform(-1,1)
        t=t+0.1
#        print( "H, Vi,t,y: " + str(H) + "," + str(vi) + "," + str(t) + "," + str(pinata_loc[1]))
        if( pinata_loc[1]<=0):
            pinata_loc[1]=0
            vi= (-1*GRAVITY*t) / 5
            if(vi<2.0):
                vi=0.0
            t=0.1
            H = 0.0
            
            
#        pinata_loc[0]=random.uniform(0,10)
#        pinata_loc[1]=random.uniform(0,10)
#        pinata_loc[2]=random.uniform(0,10)
        # Tweening Move...
        pinataParent.update(data='{"animation": {"property": "position","to": "' + str(pinata_loc[0]) + ' ' + str(pinata_loc[1]) + ' ' + str(pinata_loc[2]) + '","easing": "linear","dur": 100}}')
        time.sleep(0.1)


# Manually delete clicks
def ray_harvester_thread():
    global click_objects
    while True:
        while click_objects:
            line=click_objects.pop()
            if type(line) is not str: 
                line.delete()
        time.sleep(2)

# This function draws a line when a user clicks
def draw_ray(click_pos, position):
    global clock_objects
    random_number = random.randint(0,16777215)
    rand_color = str(hex(random_number))
    rand_color ='#'+ rand_color[2:]
    line = arena.Object(
        #ttl=1,   DON'T USE THIS FOR high traffic objects since it uses the DB!
        # Have a harvester thread above instead
        objType=arena.Shape.thickline,
        thickline=arena.Thickline( # slightly below camera so you can see line vs head-on
            {
                (click_pos[0],click_pos[1]-0.2,click_pos[2]),
                (position[0],position[1],position[2])
            },5,rand_color)
    )
    click_objects.append(line)
animateState = False


def pinata_handler(event=None):
    global pinata1 
    global text1 
    global hud 
    global vi
    global pinataParent
    global hit_counter 
    global fire_impulse
    global gravity_enabled 

#    print("pinata hit handler callback!")
#    if event.event_type == arena.EventType.mouseenter:
        # Make it transparent on hover over
#        pinata1.update(transparency=arena.Transparency(True, 0.1)  )
#    if event.event_type == arena.EventType.mouseleave:
        # Make it opaque, you can add color or other properties in the list
#        pinata1.update(transparency=arena.Transparency(True, 1.0) )
    if event.event_type == arena.EventType.mousedown:
        # On click, draw a ray
        draw_ray(event.click_pos, event.position)
        
        #pinataParent.update(location=(pinata_loc[0],pinata_loc[1],pinata_loc[2]))
        #pinata_loc[0]=random.uniform(0,10)
        #pinata_loc[1]=random.uniform(0,10)
        #pinata_loc[2]=random.uniform(0,10)
        # Tweening Move...
        #pinataParent.update(data='{"animation": {"property": "position","to": "' + str(pinata_loc[0]) + ' ' + str(pinata_loc[1]) + ' ' + str(pinata_loc[2]) + '","easing": "linear","dur": 250}}')

        
        hit_counter = hit_counter - 1
        if hit_counter == NUM_HITS-1:
            gravity_enabled=True

        fire_impulse = 1

        hud = arena.Object(
                persist=True,
                objName="hudText",
                objType=arena.Shape.text,
                text=str(hit_counter),
                location=(0, 0.4, -0.5),
                parent="myCamera",
                scale=(0.2, 0.2, 0.2),
            )

        if hit_counter==0:
            hud = arena.Object(
                persist=True,
                objName="hudText",
                objType=arena.Shape.text,
                text="Yay!!!",
                location=(0, 0.4, -0.5),
                parent="myCamera",
                scale=(0.2, 0.2, 0.2),
            )
            gravity_enabled=False
            # clickable false doesn't seem to work...
            pinata1.update( clickable=False )
            # For now, just hide it
            pinataParent.update( location=(0,-5000,0) )
            magestic_ending()
            # respawn in random location
            pinata_loc[0]=random.uniform(AREA_X_START,AREA_X_STOP)
            pinata_loc[1]=random.uniform(3,15)
            pinata_loc[2]=random.uniform(AREA_Y_START,AREA_Y_STOP)
            pinataParent.update( location=(pinata_loc[0],pinata_loc[1],pinata_loc[2]) )
            pinata1.update( clickable=True)
            hit_counter=NUM_HITS

            hud = arena.Object(
                persist=True,
                objName="hudText",
                objType=arena.Shape.text,
                text="Come find me!",
                location=(0, 0.4, -0.5),
                parent="myCamera",
                scale=(0.2, 0.2, 0.2),
            )



        text1 = arena.Object(
                objName="text1",
                objType=arena.Shape.text,
                scale=(5.0,5.0,5.0),
                location=( 0,7,0),
                rotation=( 0,0,0,1),
                #clickable=False,
                data='{"text":"' + str(hit_counter) + '"}',
                color=(random.uniform(0,255),random.uniform(0,255),random.uniform(0,255)),
		        persist=True,
                parent="pinataParent"
            )


def signal_handler(sig, frame):
    global kill_flag
    print( "Setting Kill flat")
    kill_flag=1
    time.sleep(1.0)
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Pull in the SCENE, MQTT and REALM parameters from environmental variables 
# TODO: Add commandline overide
if (os.environ.get('SCENE') is not None) and (os.environ.get('REALM') is not None) and (os.environ.get('MQTTH') is not None):
    SCENE = os.environ["SCENE"]
    HOST = os.environ["MQTTH"]
    REALM = os.environ["REALM"]
    print("Loading:" + SCENE + "," + REALM + "," + HOST)
else:
    print( "You need to set SCENE, MQTTH and REALM as environmental variables to specify the program target")
    exit(-1)

# init the ARENA library
arena.init(HOST, REALM, SCENE)

print("starting sign main loop")

# 
pinataParent = arena.Object(
    persist=True,
    objName="pinataParent",
    objType=arena.Shape.cube,
    location=(0, 0, 0),
    transparency=arena.Transparency(True, 0),
)


pinata1 = arena.Object(
                objName="pinata-model",
                url="store/users/wiselab/models/fortnite_llama/scene.gltf",
                objType=arena.Shape.gltf_model,
                scale=(0.01,0.01,0.01),
                location=(0,0,0),
                clickable=True,
		        persist=True,
                parent="pinataParent",
                callback=pinata_handler)

text1 = arena.Object(
                objName="text1",
                objType=arena.Shape.text,
                scale=(5.0,5.0,5.0),
                location=( 0,7,0),
                rotation=( 0,0,0,1),
                clickable=False,
                data='{"text":"Click Me!"}',
                color=(100,100,255),
		        persist=True,
                parent="pinataParent"
)

hud = arena.Object(
        persist=True,
        objName="hudText",
        objType=arena.Shape.text,
        text="Game Started, Find and Click the Pinata!",
        location=(0, 0.4, -0.5),
        parent="myCamera",
        scale=(0.2, 0.2, 0.2),
    )

pinata_loc[0]=random.uniform(AREA_X_START,AREA_X_STOP)
pinata_loc[1]=random.uniform(3,15)
pinata_loc[2]=random.uniform(AREA_Y_START,AREA_Y_STOP)
# move the group of objects
pinataParent.update(location=(pinata_loc[0],pinata_loc[1],pinata_loc[2]))

x = threading.Thread(target=game_thread)
x.start()
y = threading.Thread(target=ray_harvester_thread)
y.start()
# This is the main ARENA event handler
# Everything after this should be in callbacks
arena.handle_events()
