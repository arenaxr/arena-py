from arena import *
import random


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

@scene.run_once
def main():
   scene.add_object(head)

@scene.run_forever(interval_ms=10)
def update():
    global i, headlist, cnt
    for head in headlist:
        scene.update_object( head, rotation=(0, i, 0),)
    i=i+10
    cnt=cnt+1
    print("Tick: " + str(cnt))

scene.run_tasks()
