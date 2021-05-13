import datetime
import random
import time

from arena import *

scene = Scene(host="arenaxr.org", realm="realm", scene="headbanger", )
# Create models

# How Many heads?
heads = 100
# Type of head.  0- box, 1- GLTF
head_type = 1

headlist = []
cnt = 0

for x in range(heads):

    if head_type == 1:
        head = GLTF(
            object_id="head"+str(cnt),
            position=(random.random()*10, 1.5, random.random()*-10),
            scale=(1, 1, 1),
            url="https://www.dropbox.com/s/e28sgj44mwy0bbg/loomis-purple.glb?dl=0"
        )
    else:
        head = Box(
            object_id="head"+str(cnt),
            position=(random.random()*10, 1.5, random.random()*-10),
            scale=(.1, .1, .1),
        )
    headlist.append(head)
    cnt = cnt+1


i = 0
cnt = 0
cycle = 0
last = datetime.datetime.now()


@scene.run_once
def main():
    print("Adding heads")
    for head in headlist:
        scene.add_object(head)


@scene.run_forever(interval_ms=100)
def update():
    global i, headlist, cnt, last, cycle
    if cnt < 100:
        print("waiting...")
        cnt = cnt+1
        return
    i = (i+15) % 360
    for head in headlist:
        if i == 0:
            head.data.position.y = cycle % 3 + 1
            if(cycle % 3 == 0):
                scene.update_object(head, rotation=(
                    0, i, 0), color=(255, 0, 0))
            if(cycle % 3 == 1):
                scene.update_object(head, rotation=(
                    0, i, 0), color=(0, 255, 0))
            if(cycle % 3 == 2):
                scene.update_object(head, rotation=(
                    0, i, 0), color=(0, 0, 255))
        else:
            scene.update_object(head, rotation=(
                0, i, 0), color=(128, 128, 128))
    if i == 0:
        if(cycle % 3 == 0):
            print("********************************** Red Low")
        if(cycle % 3 == 1):
            print("********************************** Green Middle")
        if(cycle % 3 == 2):
            print("********************************** Blue High")
        cycle = cycle+1
    cnt = cnt+1
    now = datetime.datetime.now()
    c = now-last
    last = now
    print("Heads: " + str(heads) + " Tick: " + str(cnt) +
          " Time: " + str(c.microseconds/1000) + "ms")


scene.run_tasks()
