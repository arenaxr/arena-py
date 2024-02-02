# teleporter.py
''' Creates a teleporter
'''

import random
from arena import *


USER_HEIGHT = 1.6
UPDATE_INTERVAL = 100
TELEPORT_THRES = 1.0


def rando():
    return float(random.randint(-100000, 100000)) / 3000


class Teleporter(Object):
    def __init__(self, scene, pos_src: Position, pos_dest: Position):
        self.scene = scene

        self.pos_src = pos_src
        self.pos_dest = pos_dest
        self.pos_src.y = USER_HEIGHT
        self.pos_dest.y = USER_HEIGHT

        # create objects
        self.teleporter_src = Cylinder(
                                object_id="teleporter1",
                                scale=(1,2.5,1),
                                material=Material(transparent=True, opacity=0.5, color=(255,255,0)),
                                position=self.pos_src
                            )
        self.teleporter_dest = Cylinder(
                                object_id="teleporter2",
                                scale=(1,2.5,1),
                                material=Material(transparent=True, opacity=0.5, color=(255,0,255)),
                                position=self.pos_dest
                            )
        self.src_text = Text(value="Teleporter source", position=(0,0.8,0), parent=self.teleporter_src)
        self.dest_text = Text(value="Teleporter destination", position=(0,0.8,0), parent=self.teleporter_dest)

        # add objects to scene
        self.scene.add_object(self.teleporter_src)
        self.scene.add_object(self.teleporter_dest)
        self.scene.add_object(self.src_text)
        self.scene.add_object(self.dest_text)


scene = Scene(host="arenaxr.org", scene="example")

teleporter = Teleporter(
                    scene=scene,
                    pos_src=Position(rando(),USER_HEIGHT,rando()),
                    pos_dest=Position(rando(),USER_HEIGHT,rando())
                )

@scene.run_forever(interval_ms=UPDATE_INTERVAL)
def teleporter_handler():
    for user in scene.get_user_list():
        if user.data.position.distance_to(teleporter.pos_src) <= TELEPORT_THRES:
            print("teleported!")
            scene.manipulate_camera(
                user,
                position=teleporter.pos_dest,
            )

scene.run_tasks()
