from arena import *
import random
import time

scene = Scene(host="arenaxr.org", realm="realm", scene="pinata")

RESPAWN_X_AREA = 100
RESPAWN_Z_AREA = 100
RESPAWN_Y = 10
HIT_RELOAD=10
G_ACCEL = -9.8
HIT_IMPULSE = 10
GROUND_LEVEL = 0

pinata_loc = [0,0,0]
pinata_state = 0  # 0-still, 1-moving, 2-explode 
hit_counter = HIT_RELOAD 
t=0
vy=0

def explode():
    global pinata_loc, pinata
    print("Boom!")
    pinata.update_attributes(position=(0,-1000,0))
    scene.update_object(pinata)
    for i in range(50):
        rand_offset = (random.random()-0.5)/5
        colorBox = Box(position=(pinata_loc[0]+rand_offset, pinata_loc[1]+rand_offset, pinata_loc[2]+rand_offset),scale=Scale(.5,.5,.5),ttl=15,physics=Physics(type="dynamic")) 
        scene.add_object(colorBox) 
    explode_sound = Sound(src="https://www.dropbox.com/s/jzk4tkho653ugbn/explode.wav?dl=0",positional=True,autoplay=True,poolSize=1 )
    explode_sound_obj = Box(sound=explode_sound,position=pinata_loc,scale=Scale(.01,.01,.01),ttl=10) 
    scene.add_object(explode_sound_obj)



def click(scene, evt, msg):
    global pinata_loc, vy, pinata_state, hit_counter, hit_text
    if evt.type == "mousedown":
        start = evt.data.clickPos
        end = evt.data.position
        start.x-=.1
        start.y-=.1
        start.z-=.1
        line = ThickLine(path=(start,end), color=(255,0,0), lineWidth=5, ttl=1)
        scene.add_object(line)
        # Velocity of hit
        vy+= HIT_IMPULSE
        pinata_state=1
        hit_counter-=1
        hit_text.update_attributes(text=str(hit_counter))
        scene.update_object(hit_text)

        hit_sound = Sound(src="https://www.dropbox.com/s/3gwfykslii55gp4/hit.wav?dl=0",positional=True,autoplay=True,poolSize=10 )
        hit_sound_obj = Box(sound=hit_sound,position=pinata_loc,scale=Scale(.01,.01,.01),ttl=1) 
        scene.add_object(hit_sound_obj)

        print("Hit Counter: " + str(hit_counter))
        if hit_counter==0:
            pinata_state = 2 


def game_reset():
    global hit_counter,pinata_loc,pinata_state,pinata,hit_text,vy,t
    witch_sound = Sound(src="https://www.dropbox.com/s/lw7elc3krguk1mh/witch.wav?dl=0",positional=True,autoplay=True,poolSize=1 )
    witch_sound_obj = Box(sound=witch_sound,position=pinata_loc,scale=Scale(.01,.01,.01),ttl=10) 
    scene.add_object(witch_sound_obj)
    hit_counter=HIT_RELOAD
    pinata_loc=[random.randrange(-RESPAWN_X_AREA,RESPAWN_X_AREA),RESPAWN_Y,random.randrange(-RESPAWN_Z_AREA,RESPAWN_Z_AREA)]   
    pinata.update_attributes(position=pinata_loc)
    scene.update_object(pinata)
    hit_text.update_attributes(text=str(hit_counter))
    scene.update_object(hit_text)
    scene.update_object(hit_text)
    vy=0
    t=0
    pinata_state=0
    print( "Respawned at: " + str(pinata_loc))


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
            url="https://www.dropbox.com/s/a7fm7tcvybhh5rj/pinata.glb?dl=0"
        )
    scene.add_object(pinata)
    hit_text = Text(object_id="hit_text", persist=True, text=str(hit_counter), scale=Scale(3,3,3), position=Position(0.5,5,0), parent=pinata)
    scene.add_object(hit_text)
    scene.update_object(hit_text)
    game_reset()

@scene.run_forever(interval_ms=100)
def main_loop():
    global pinata, pinata_loc, t,pinata_state
    global vy

    dt=.1  # size of timestamp set at 100ms

    if pinata_state==2:
        pinata_state=3
        t=0
        explode()
    if pinata_state==3:
        t+=dt
        if t>20:
            game_reset()
            pinata_state=0


    y=pinata_loc[1]

    # If the pinata is hit, start computing gravity
    if pinata_state==1:
        y +=  vy * dt
        vy += G_ACCEL * dt 
        if y<=GROUND_LEVEL+.2: 
            if vy>2 or  vy<-2:
                vy=-.5*vy
                y = GROUND_LEVEL
                boing_sound = Sound(src="https://www.dropbox.com/s/3obfz1in7tj37ce/boing.wav?dl=0",positional=True,autoplay=True,poolSize=10 )
                boing_sound_obj = Box(sound=boing_sound,position=pinata_loc,scale=Scale(.01,.01,.01),ttl=1) 
                scene.add_object(boing_sound_obj)
            else:
                vy=0
                y = GROUND_LEVEL
                pinata_state=0

        pinata_loc[1]=y
        t+=dt
        pinata.update_attributes(position=pinata_loc)
        scene.update_object(pinata)


scene.run_tasks()
