import random
import time
from datetime import datetime

from arena import *

scene = Scene(host="arenaxr.org", scene="headbanger", )
# Create models

# How Many heads?
heads = 100
# Type of head.  0- box, 1- GLTF
head_type = 1
# Rotation type.  0- network MQTT ticks, 1- animation ticks
rotation_type = 0

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
    if rotation_type == 1:
        animation = Animation(
            property="rotation",
            start=(0, 0, 0),
            end=(0, 360, 0),
            loop=True,
            easing="linear",
            # dur=20000
        )
        head.dispatch_animation(animation)

    headlist.append(head)
    cnt = cnt+1

i = 0
cnt = 0
cycle = 0
last = datetime.now()


@scene.run_once
def main():
    print("Adding heads")
    for head in headlist:
        scene.add_object(head)
        if rotation_type == 1:
            scene.run_animations(head)


@scene.run_forever(interval_ms=100)
def update():
    global i, headlist, cnt, last, cycle
    if rotation_type == 1:
        return  # do not re-publish for animantion case
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
    now = datetime.now()
    c = now-last
    last = now
    print("Heads: " + str(heads) + " Tick: " + str(cnt) +
          " Time: " + str(c.microseconds/1000) + "ms")


scene.run_tasks()
