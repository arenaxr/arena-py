# teleporter.py
''' Creates a teleporter
'''

import random
from arena import *


def rando():
    return float(random.randint(-100000, 100000)) / 1000


class Teleporter(Object):
    def __init__(self, scene, pos1: Position, pos2: Position):
        self.scene = scene
        self.pos1 = pos1
        self.pos2 = pos2
        self.pos1.y = 1.6
        self.pos2.y = 1.6
        self.teleporter1 = Cylinder(
                                object_id="teleporter1",
                                scale=(1,2.5,1),
                                material=Material(color=(255,255,0), transparent=True, opacity=0.5),
                                position=self.pos1
                            )
        self.teleporter2 = Cylinder(
                                object_id="teleporter2",
                                scale=(1,2.5,1),
                                material=Material(color=(255,0,255), transparent=True, opacity=0.5),
                                position=self.pos2
                            )
        self.tp1_text = Text(text="Teleporter source", position=(0,1,0), parent=self.teleporter1)
        self.tp2_text = Text(text="Teleporter destination", position=(0,1,0), parent=self.teleporter2)

        self.scene.add_object(self.teleporter1)
        self.scene.add_object(self.teleporter2)
        self.scene.add_object(self.tp1_text)
        self.scene.add_object(self.tp2_text)


users = []


def user_join_callback(scene, cam, msg):
    global users
    users += [cam]


scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")
scene.user_join_callback = user_join_callback

teleporter = Teleporter(scene, Position(rando(),0.1,rando()), Position(rando(),0.1,rando()))

@scene.run_forever(interval_ms=100)
def teleporter_handler():
    global users

    for user in users:
        if user.data.position.distance_to(teleporter.pos1) <= 1.0:
            print("teleport!")
            scene.manipulate_camera(
                user,
                position=teleporter.pos2,
            )

scene.run_tasks()
