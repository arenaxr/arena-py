# camera.py
#
# Move (all) users' camera about a scene with cinematic slow movements
# takes an argument: scene name for which to move the camera(s) in
# [TODO] update this to 0.1.0!

import arena
import random
import time
import signal
import sys

HOST = "arena.andrew.cmu.edu"
SCENE = "render"

if len(sys.argv) > 1:
    SCENE=sys.argv[1]


arena.init(HOST, "realm", SCENE)
#arena.debug()


def signal_handler(sig, frame):
    exit()


signal.signal(signal.SIGINT, signal_handler)

limit=12.5
# SPEED: moves every so often
S=10

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
rig=arena.Object(objName="myCamera")
spinner=arena.Object(objName="myCamera")

Rold = (1,1,1)
Rjoe = (0,0,0)

while True:
    joe = randmove(old)
    Rjoe = randrot(Rold)
    print (joe,Rjoe)
    #print (Rold,"->",Rjoe)

    rig.update    (data='{"animation": {"property": "position","from": "'+
               str(old[0])+' '+str(old[1])+' '+str(old[2])+'","to": "'+
               str(joe[0])+' '+str(joe[1])+' '+str(joe[2])+
                   '","easing": "easeInOutQuad","dur": '+str(S)+'000}}')
    spinner.update(data='{"animation__2": {"property": "rotation","from": "'+
               str(Rold[0])+' '+str(Rold[1])+' '+str(Rold[2])+'","to": "'+
               str(Rjoe[0])+' '+str(Rjoe[1])+' '+str(Rjoe[2])+
                   '","easing": "easeInOutQuad","dur": '+str(S)+'000}}')

    old=(joe[0],joe[1],joe[2])
    Rold=(Rjoe[0],Rjoe[1],Rjoe[2])
    time.sleep(S)

arena.handle_events()
