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
boom_loc = [ 3, 2, -10]
NUM_HITS = 10
hit_counter = NUM_HITS

# AREA for seeding location and effects
AREA_X_START = -5
AREA_X_STOP = 25
AREA_Y_START = -5
AREA_Y_STOP = 25
NUM_BOXES = 5
pinata_scale = 0.1
kill_flag = 0

GROUND_LEVEL = -2.1
TXT_HIGHT = 2.0

delete_object_queue = [""]
# To run in ARTS, these parameters are passed in as environmental variables.
# export HOST=mqtt.arenaxr.org
# export REALM=realm
# export MQTTH=arenaxr.org

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
    global boom_loc
    print("Boom!")
    boxes = [""]
    explode = arena.Object( location=(boom_loc[0],boom_loc[1],boom_loc[2]),data='{"material": { "transparent": true, "opacity": 0 },"sound":{"positional":true,"poolSize":1,"src":"store/users/wiselab/audio/explode.wav","autoplay":"true"}}')
    delete_object_queue.append(explode)
    for i in range(NUM_BOXES):
        x=arena.Object(
        objType=arena.Shape.cube,
        persist=False,
        objName="cube"+str(i),
        # messes up child-follow-parent pose
        physics=arena.Physics.dynamic,
        collision_listener=False,
        #transparency=arena.Transparency(True,0.5),
        impulse=arena.Impulse("mouseup",( 5,30,0),(30,1,1)),
#        location=(random.randrange(AREA_X_START,AREA_X_STOP), 10, random.randrange(AREA_Y_START,AREA_Y_STOP)),
        location=(boom_loc[0], boom_loc[1]+1.5, boom_loc[2] ),
        color=random_color(),
        scale=(0.2, 0.2, 0.2),
        clickable=False,
        callback=box_callback,
        )
        boxes.append(x)
    time.sleep(0.5)
    clap = arena.Object( location=(boom_loc[0],boom_loc[1],boom_loc[2]),data='{"material": { "transparent": true, "opacity": 0 },  "sound":{"positional":true,"poolSize":1,"src":"store/users/wiselab/audio/applause.wav","autoplay":"true"}}')
    delete_object_queue.append(clap)
    time.sleep(2.0)
    clap = arena.Object( location=(boom_loc[0],boom_loc[1],boom_loc[2]),data='{ "material": { "transparent": true, "opacity": 0 }, "sound":{"positional":true,"poolSize":1,"src":"store/users/wiselab/audio/applause.wav","autoplay":"true"}}')
    time.sleep(7)
    clap.delete()
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
    global delete_object_queue
    global pinata_loc

    cnt = 0
    while True:
        if kill_flag==1:
            print("Kill Flat!")
            return
        #if gravity_enabled is True:
        #    pinataParent.update(location=(pinata_loc[0],pinata_loc[1],pinata_loc[2]))
        if(fire_impulse>0):
            print("Hit!")
            t=0.1
            vi=10.0
            H = pinata_loc[1]
            fire_impulse=0
        if gravity_enabled is True:
            pinata_loc[1] = H + vi * t + 0.5*GRAVITY*(t*t)
            #if cnt%4==0 and pinata_loc[1]>6.0:
            if pinata_loc[1]>GROUND_LEVEL+0.5:
                pinata_loc[0] += random.uniform(-0.25,0.25)
                pinata_loc[2] += random.uniform(-0.25,0.25)
        t=t+0.1
#        print( "H, Vi,t,y: " + str(H) + "," + str(vi) + "," + str(t) + "," + str(pinata_loc[1]))
        if( pinata_loc[1]<=GROUND_LEVEL):
            pinata_loc[1]=GROUND_LEVEL
            vi= (-1*GRAVITY*t) / 5
            if(vi<2.0):
                vi=0.0
            else:
                boing = arena.Object( scale=(0.1,0.1,0.1), location=(pinata_loc[0],pinata_loc[1],pinata_loc[2]),data='{"material": { "transparent": true, "opacity": 0 },"sound":{"positional":true,"poolSize":1,"src":"store/users/wiselab/audio/boing.wav","autoplay":"true"}}')
                delete_object_queue.append(boing)
            t=0.1
            #H = 0.0
            H = GROUND_LEVEL


#        pinata_loc[0]=random.uniform(0,10)
#        pinata_loc[1]=random.uniform(0,10)
#        pinata_loc[2]=random.uniform(0,10)
        # Tweening Move...
        if gravity_enabled is True and vi>0:
            pinataParent.update(location=(pinata_loc[0],pinata_loc[1],pinata_loc[2]))
            pinataParent.update(data='{"animation": {"property": "position","to": "' + str(pinata_loc[0]) + ' ' + str(pinata_loc[1]) + ' ' + str(pinata_loc[2]) + '","easing": "linear","dur": 100}}')
        time.sleep(0.1)
        cnt=cnt+1
        if cnt>90:
            cnt=0
            pinataParent.update(location=(pinata_loc[0],pinata_loc[1],pinata_loc[2]))
            pinataParent.update(data='{"animation": {"property": "position","to": "' + str(pinata_loc[0]) + ' ' + str(pinata_loc[1]) + ' ' + str(pinata_loc[2]) + '","easing": "linear","dur": 100}}')


# Manually delete clicks
def object_harvester_thread():
    global delete_object_queue
    while True:
        while delete_object_queue:
            obj=delete_object_queue.pop()
            if type(obj) is not str:
                obj.delete()
        time.sleep(5)

# This function draws a line when a user clicks
def draw_ray(click_pos, position):
    global delete_object_queue
    global pinata_loc

    click = arena.Object( scale=(0.1,0.1,0.1), location=(pinata_loc[0],pinata_loc[1],pinata_loc[2]),data='{"material": { "transparent": true, "opacity": 0 },"sound":{"positional":true,"poolSize":1,"src":"store/users/wiselab/audio/glass.oga","autoplay":"true"}}')
    delete_object_queue.append(click)
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
    delete_object_queue.append(line)
animateState = False


def pinata_handler(event=None):
    global pinata1
    global text1
    global vi
    global pinataParent
    global hit_counter
    global fire_impulse
    global gravity_enabled
    global boom_loc
    global pinata_loc

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

#        hud = arena.Object(
#                persist=True,
#                objName="hudText",
#                objType=arena.Shape.text,
#                text=str(hit_counter),
#                location=(0, 0.4, -0.5),
#                parent="myCamera",
#                scale=(0.2, 0.2, 0.2),
#            )

        if hit_counter==0:
#            hud = arena.Object(
#                persist=True,
#                objName="hudText",
#                objType=arena.Shape.text,
#                text="Yay!!!",
#                location=(0, 0.4, -0.5),
#                parent="myCamera",
#                scale=(0.2, 0.2, 0.2),
#            )

            boom_loc[0]=pinata_loc[0]
            boom_loc[1]=pinata_loc[1]
            boom_loc[2]=pinata_loc[2]
            pinata_loc[0]= 5000
            pinata_loc[2]= 5000
            pinataParent.update(data='{"animation": {"property": "position","to": "0 -5000 0","easing": "linear","dur": 100}}')
            pinataParent.update( location=(5000,0,5000) )
            gravity_enabled=False
            # clickable false doesn't seem to work...
            #pinata1.update( clickable=False )
            # For now, just hide it
            magestic_ending()
            # respawn in random location
            restart = arena.Object( location=(pinata_loc[0],pinata_loc[1],pinata_loc[2]),data='{"material": { "transparent": true, "opacity": 0 },"sound":{"positional":true,"poolSize":1,"src":"store/users/wiselab/audio/witch.wav","autoplay":"true"}}')
            restart.delete()
            pinata_loc[0]=random.uniform(AREA_X_START,AREA_X_STOP)
            pinata_loc[1]=GROUND_LEVEL+1.0
            pinata_loc[2]=random.uniform(AREA_Y_START,AREA_Y_STOP)
            pinataParent.update( location=(pinata_loc[0],pinata_loc[1],pinata_loc[2]) )
            #pinata1.update( clickable=True)
            hit_counter=NUM_HITS

#            hud = arena.Object(
#                persist=True,
#                objName="hudText",
#                objType=arena.Shape.text,
#                text="Come find me!",
#                location=(0, 0.4, -0.5),
#                parent="myCamera",
#                scale=(0.2, 0.2, 0.2),
#            )



        text1 = arena.Object(
                objName="text1",
                objType=arena.Shape.text,
                scale=(1.0,1.0,1.0),
                location=( 0,TXT_HIGHT,0),
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
    print( "\nFor bash you can copy paste the following before running:")
    print( "export MQTTH=arenaxr.org")
    print( "export REALM=realm")
    print( "export SCENE=example")
    exit(-1)

# init the ARENA library
arena.init(HOST, REALM, SCENE)

print("starting sign main loop")

#
pinataParent = arena.Object(
    persist=True,
    objName="pinataParent",
    #objType=arena.Shape.cube,
    location=(0, 0, 0),
    #scale=(0.1,0.1,0.1),
    transparency=arena.Transparency(True, 0),
)


pinata1 = arena.Object(
                objName="pinata-model",
                url="store/users/wiselab/models/fortnite_llama/scene.gltf",
                objType=arena.Shape.gltf_model,
                scale=(0.002,0.002,0.002),
                location=(0,0,0),
                clickable=True,
		        persist=True,
                parent="pinataParent",
                callback=pinata_handler,
                #data='{"sound":{"positional":true,"poolSize":8,"src":"https://xr.andrew.cmu.edu/audio/boing.wav","on":"mousedown"}}'
                )

text1 = arena.Object(
                objName="text1",
                objType=arena.Shape.text,
                scale=(1.0,1.0,1.0),
                location=( 0,TXT_HIGHT,0),
                rotation=( 0,0,0,1),
                clickable=False,
                data='{"text":"Click Me!"}',
                color=(100,100,255),
		        persist=True,
                parent="pinataParent"
)

#hud = arena.Object(
#        persist=True,
#        objName="hudText",
#        objType=arena.Shape.text,
#        text="Game Started, Find and Click the Pinata!",
#        location=(0, 0.4, -0.5),
#        parent="myCamera",
#        scale=(0.2, 0.2, 0.2),
#    )

pinata_loc[0]=random.uniform(AREA_X_START,AREA_X_STOP)
#pinata_loc[1]=random.uniform(GROUND_LEVEL,1)
pinata_loc[1]=GROUND_LEVEL+1
pinata_loc[2]=random.uniform(AREA_Y_START,AREA_Y_STOP)
# move the group of objects
pinataParent.update(location=(pinata_loc[0],pinata_loc[1],pinata_loc[2]))

restart = arena.Object( location=(pinata_loc[0],pinata_loc[1],pinata_loc[2]),data='{"material": { "transparent": true, "opacity": 0 },"sound":{"positional":true,"poolSize":1,"src":"store/users/wiselab/audio/witch.wav","autoplay":"true"}}')
delete_object_queue.append(restart)

x = threading.Thread(target=game_thread)
x.start()
y = threading.Thread(target=object_harvester_thread)
y.start()
# This is the main ARENA event handler
# Everything after this should be in callbacks

arena.handle_events()
