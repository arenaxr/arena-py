# camera.py
#
# Move (all) users' camera about a scene with cinematic slow movements
# takes an argument: scene name for which to move the camera(s) in

from arena import *
import random
import sys

HOST = "arenaxr.org"
SCENE = "test"

if len(sys.argv) > 1:
    SCENE=sys.argv[1]


arena = Scene(HOST, "realm", SCENE)

limit=12.5

def randmove(old):
    x = random.randint(-S,S)
    y = random.randint(-S,S)
    z = random.randint(-S,S)
    retx = x+old[0]
    if (retx > limit):  retx=   limit
    if (retx < -limit): retx = -limit
    rety= y+old[1]
    if (rety > limit): rety=limit
    if (rety < 0):     rety= 0
    retz = z+old[2]
    if (retz > limit):  retz=   limit
    if (retz < -limit): retz = -limit
    return(retx,rety,retz)

RR=30
Rlimit=90
def randrot(old):
    x = random.randint(-RR,RR)
    y = random.randint(-RR,RR)
    z = random.randint(-RR,RR)
    retx = x+old[0]
    if (retx >  Rlimit): retx= Rlimit
    if (retx < -Rlimit): retx=-Rlimit
    rety= y+old[1]
    if (rety >  Rlimit): rety= Rlimit
    if (rety < -Rlimit): rety=-Rlimit
    retz = z+old[2]
    if (retz >  Rlimit): retz= Rlimit
    if (retz < -Rlimit): retz=-Rlimit

    return(retx,rety,0) # pitch,yaw,roll



old=(0,0,0)

# trick: obtain an arena.py Object for an already-existing global scene object named "cameraRig"
# in order to update it's data attributes
rig = Object(object_id="myCamera")

Rold = (1,1,1)
Rjoe = (0,0,0)

# SPEED: moves every so often
S = 10*1000

@scene.run_forever(interval_ms=S)
def main():
    global old, joe, Rold, Rjoe

    joe = randmove(old)
    Rjoe = randrot(Rold)

    # add animation
    scene.update_object(rig,
        animation=Animation(
            property="position",
            start=(old[0], old[1], old[2]),
            end=(joe[0], joe[1], joe[2]),
            easing="easeInOutQuad",
            dur=str(S)
        ),
        animation__2=Animation(
            property="rotation",
            start=f"{str(Rold[0])} {str(Rold[1])} {str(Rold[2])}",
            end=f"{str(Rjoe[0])} {str(Rjoe[1])} {str(Rjoe[2])}",
            easing="easeInOutQuad",
            dur=str(S)
        )
    )
    print(rig)

    old=(joe[0],joe[1],joe[2])
    Rold=(Rjoe[0],Rjoe[1],Rjoe[2])

scene.run_tasks()
