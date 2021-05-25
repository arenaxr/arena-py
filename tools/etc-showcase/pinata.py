# This is a demo program of a pianta that randomly respawns and after some number of clicks
# will explode and then respawn.
# It currently does not use tweened animations (todo) and does not play well with navmeshes (todo)
# The program simulates its own synchronous physics for the pinata.  The colored squares from the explosion
# use globally asynchronous client-side physics (not consistent across viewers).

from arena import *
import random
import time

scene = Scene(host="arenaxr.org", scene="ProjectHub")

# Constants used to define operations
RESPAWN_X_MIN = -67
RESPAWN_X_MAX = 25
RESPAWN_Z_MIN = -338
RESPAWN_Z_MAX = -205
RESPAWN_Y = 20          # respawn at exactly this Y position
HIT_RELOAD=10           # how many hits does it take
#G_ACCEL = -9.8
#HIT_IMPULSE = 20
G_ACCEL = -19.8
HIT_IMPULSE = 20        # Velocity added to hit
GROUND_LEVEL = -1       # Ground level for pseudo-physics

# some state defines
IDLE = 0
MOVING = 1
EXPLODE = 2
WAITING_RESTART = 3

# Assets for the program
PINATA_MODEL_PATH="https://www.dropbox.com/s/a7fm7tcvybhh5rj/pinata.glb?dl=0"
EXPLODE_SOUND_PATH="https://www.dropbox.com/s/jzk4tkho653ugbn/explode.wav?dl=0"
BOUNCE_SOUND_PATH="https://www.dropbox.com/s/3obfz1in7tj37ce/boing.wav?dl=0"
HIT_SOUND_PATH="https://www.dropbox.com/s/3gwfykslii55gp4/hit.wav?dl=0"
WITCH_SOUND_PATH="https://www.dropbox.com/s/lw7elc3krguk1mh/witch.wav?dl=0"
APPLAUSE_SOUND_PATH="https://www.dropbox.com/s/3k9fin95z6nbex9/applause.wav?dl=0"

# location of the pinata
pinata_loc = [0,0,0]
pinata_state = IDLE  # 0-still, 1-moving, 2-explode, 3-waiting to restart
hit_counter = HIT_RELOAD
# time and velocity globals for physics
t=0
vy=0
restart_counter=0

# Generate a bunch of random boxes from the pinata location.
# These boxes use local physics
def explode():
    global pinata_loc, pinata
    print("Boom!")
    pinata.update_attributes(position=(0,-1000,0))
    scene.update_object(pinata)
    for i in range(50):
        rand_offset = (random.random()-0.5)/5
        colorBox = Box(position=(pinata_loc[0]+rand_offset, pinata_loc[1]+rand_offset, pinata_loc[2]+rand_offset),scale=Scale(.5,.5,.5),ttl=15,physics=Physics(type="dynamic"))
        scene.add_object(colorBox)
    explode_sound = Sound(src=EXPLODE_SOUND_PATH,positional=True,autoplay=True,poolSize=1 )
    explode_sound_obj = Box(sound=explode_sound,position=pinata_loc,scale=Scale(.01,.01,.01),ttl=10)
    scene.add_object(explode_sound_obj)
    applause_sound = Sound(src=APPLAUSE_SOUND_PATH,positional=True,autoplay=True,poolSize=1 )
    applause_sound_obj = Box(sound=applause_sound,position=pinata_loc,scale=Scale(.01,.01,.01),ttl=10)
    scene.add_object(applause_sound_obj)


# This is a callback handler attached to the pinata that processes click events
def click(scene, evt, msg):
    global pinata_loc, vy, pinata_state, hit_counter, hit_text
    if evt.type == "mousedown":
        start = evt.data.clickPos
        end = evt.data.position
        # Minor offset in drawing the line so a user can see their own trail
        start.x-=.1
        start.y-=.1
        start.z-=.1
        # Draw a click tracer
        line = ThickLine(path=(start,end), color=(255,0,0), lineWidth=5, ttl=1)
        scene.add_object(line)
        # Velocity of hit
        vy+= HIT_IMPULSE
        pinata_state=MOVING
        hit_counter-=1
        # Update the text over the pinata
        hit_text.update_attributes(text=str(hit_counter))
        scene.update_object(hit_text)

        hit_sound = Sound(src=HIT_SOUND_PATH,positional=True,autoplay=True,poolSize=10 )
        hit_sound_obj = Box(sound=hit_sound,position=pinata_loc,scale=Scale(.01,.01,.01),ttl=1)
        scene.add_object(hit_sound_obj)

        print("Hit Counter: " + str(hit_counter))
        if hit_counter<=0:
            pinata_state = EXPLODE # This is picked up by the main game loop and hides the pinata while running the explosion animation


# Reset game state
def game_reset():
    global hit_counter,pinata_loc,pinata_state,pinata,hit_text,vy,t
    witch_sound = Sound(src=WITCH_SOUND_PATH,positional=True,autoplay=True,poolSize=1 )
    witch_sound_obj = Box(sound=witch_sound,position=pinata_loc,scale=Scale(.01,.01,.01),ttl=10)
    scene.add_object(witch_sound_obj)
    hit_counter=HIT_RELOAD
    pinata_loc=[random.randrange(RESPAWN_X_MIN,RESPAWN_X_MAX),RESPAWN_Y,random.randrange(RESPAWN_Z_MIN,RESPAWN_Z_MAX)]
    pinata.update_attributes(position=pinata_loc)
    scene.update_object(pinata)
    hit_text.update_attributes(text=str(hit_counter))
    scene.update_object(hit_text)
    scene.update_object(hit_text)
    vy=0
    t=0
    pinata_state=IDLE
    print( "Respawned at: " + str(pinata_loc))

# Generate the models at startup
# The pinata and text persist so new people entering can see them
@scene.run_once
def main():
    global pinata, pinata_loc, hit_text, hit_counter
    print("Setting up")
    pinata = GLTF(
            object_id="pinata",
            position=(pinata_loc),
            scale=(1, 1, 1),
            persist=True,
            clickable=True,
            evt_handler=click,
            url=PINATA_MODEL_PATH
            )
    scene.add_object(pinata)
    hit_text = Text(object_id="hit_text", persist=True, text=str(hit_counter), scale=Scale(3,3,3), position=Position(0.5,5,0), parent=pinata)
    scene.add_object(hit_text)
    scene.update_object(hit_text)
    game_reset()

# Main game loop called by scheduler every 100ms
@scene.run_forever(interval_ms=100)
def main_loop():
    global pinata, pinata_loc, t,pinata_state,restart_counter
    global vy

    dt=.1  # size of timestamp set at 100ms converted to seconds

    # Watchdog timer, reset without any touches after 60 seconds
    if pinata_state==IDLE:
            restart_counter+=1
            if restart_counter>=600:
                restart_counter=0
                game_reset()
                pinata_state=IDLE
    else:
        restart_counter=0

    # If exploded, play animation and wait timeout until reset
    if pinata_state==EXPLODE:
        pinata_state=WAITING_RESTART
        t=0
        explode()
    if pinata_state==WAITING_RESTART:
        t+=dt
        if t>20:
            game_reset()
            pinata_state=IDLE

    # Grab the current location of the pinata
    y=pinata_loc[1]

    # If the pinata is moving, compute physics
    if pinata_state==MOVING:
        y +=  vy * dt           # Update position based on velocity
        vy += G_ACCEL * dt      # Update velocity timestep

        # Each time the pinata hits the ground, it bounces
        # This section converts some amount of velocity at impact to be rebounce
        # This section also caps small velocities to stop infinite bouncing
        if y<=GROUND_LEVEL+.2:
            if vy>2 or  vy<-2:
                vy=-.5*vy   # This is the bounce input, where the ground returns half the velocity
                y = GROUND_LEVEL
                boing_sound = Sound(src=BOUNCE_SOUND_PATH,positional=True,autoplay=True,poolSize=10 )
                boing_sound_obj = Box(sound=boing_sound,position=pinata_loc,scale=Scale(.01,.01,.01),ttl=1)
                scene.add_object(boing_sound_obj)
            else:
                # If the velocity is low enough, lets just cap it
                vy=0
                y = GROUND_LEVEL
                pinata_state=IDLE

        pinata_loc[0]+=random.random()-0.5
        pinata_loc[2]+=random.random()-0.5
        pinata_loc[1]=y
        t+=dt # Add to the physics timestep
        pinata.update_attributes(position=pinata_loc)
        scene.update_object(pinata)


scene.run_tasks()
