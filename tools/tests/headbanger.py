from arena import *
import random
import datetime 

scene = Scene(host="arenaxr.org", realm="realm", scene="headbanger", )
# Create models


headlist = []

for x in range(100):
    head = GLTF(
    position=(random.random()*10, 1.5, random.random()*-10),
    scale=(1, 1, 1),
    url="https://www.dropbox.com/s/e28sgj44mwy0bbg/loomis-purple.glb?dl=0"
    )
    headlist.append(head)


i=0
cnt=0
last = datetime.datetime.now()

@scene.run_once
def main():
   scene.add_object(head)

@scene.run_forever(interval_ms=75)
def update():
    global i, headlist, cnt, last
    for head in headlist:
        scene.update_object( head, rotation=(0, i, 0),)
    i=i+15
    cnt=cnt+1
    now = datetime.datetime.now()
    c = now-last
    last=now
    print("Tick: " + str(cnt) + " Time: " + str(c.microseconds/1000))

scene.run_tasks()
