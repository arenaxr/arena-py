''' Synchronize users for ground truth collection with apriltags
'''
import arena
from datetime import datetime
import getopt
import numpy as np
import pose
import sys
from types import SimpleNamespace

BROKER = 'oz.andrew.cmu.edu'
REALM = 'realm'
TOPIC = REALM + '/g/a/#'
TIME_FMT = '%Y-%m-%dTH:M:S.%fZ'
COLOR_WALK = (0, 255, 0)
COLOR_FINDTAG = (255, 0, 0)
COLOR_WAIT = (255, 255, 0)
users = {}


class SyncHUD(arena.Object):
    def __init__(self, name):
        obj_str = "circle_" + name
        camera_str = "camera_" + name + "_" + name
        super().__init__(objName=obj_str,
                         objType=arena.Shape.circle,
                         parent=camera_str,
                         location=(-.5, 0, -.5),
                         rotation=(0, 0, 0, 1),
                         scale=(0.05, 0.05, 0.05),
                         color=COLOR_WALK,
                         persist=True)

    def setstate_walk(self):
        self.update(color=COLOR_WALK)

    def setstate_findtag(self):
        self.update(color=COLOR_FINDTAG)

    def setstate_wait(self):
        self.update(color=COLOR_WAIT)


class SyncUser:
    def __init__(self, name):
        self.hud = SyncHUD(name)
        self.pose = None
        self.posetime = datetime.min

    def on_tag_detect(self, campose, time):
        self.pose = campose
        self.posetime = time


def printhelp():
    print('gt-sync.py [-s <scene>] <user1> [user2 ...]')
    print('   ex: python3 gt-sync.py -s myScene name1 name2 name3')


def dict_to_sns(d):
    return SimpleNamespace(**d)


def get_tag_pose(msg):
    detected_tag = msg.detections[0]
    vio_pose = pose.pose_to_matrix4(msg.vio.position, msg.vio.rotation)
    dtag_pose1 = pose.dtag_pose_to_matrix4(detected_tag.pose)
    dtag_pose2 = pose.dtag_pose_to_matrix4(detected_tag.pose.asol)
    dtag_error1 = detected_tag.pose.e
    dtag_error2 = detected_tag.pose.asol.e
    reftag_pose = pose.reftag_pose_to_matrix4(detected_tag.refTag.pose)
    return resolve_pose_ambiguity(dtag_pose1, dtag_error1, dtag_pose2, dtag_error2, vio_pose, reftag_pose)


def on_tag_detect(msg):
    global users
    json_msg = json.loads(msg.payload.decode('utf-8'), object_hook=dict_to_sns)
    client_id = msg.topic.split('/')[-1]
    if client_id in users:
        dtag = json_msg.detections[0]
        dtag_pose = get_tag_pose(json_msg)
        reftag_pose = pose.reftag_pose_to_matrix4(dtag.refTag.pose)
        cam_pose = reftag_pose @ np.linalg.inv(dtag_pose)
        time = datetime.strptime(json_msg.timestamp, TIME_FMT)
        users[client_id].on_tag_detect(cam_pose, json_msg.timestamp)


def main():
    scene = 'cic-tags'
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hs:', ['scene='])
    except getopt.GetoptError:
        printhelp()
        sys.exit(1)

    for opt, arg in opts:
        if opt == '-h':
            printhelp()
            sys.exit(1)
        elif opt in ('-s', '--scene'):
            scene = arg

    if len(users) < 1:
        printhelp()
        sys.exit(1)

    print("Scene: " + scene)
    print("Users: " + str(args))

    arena.init(BROKER, REALM, scene)
    for user in args:
        users[user] = SyncUser(user)
        obj_str = "circle_" + user
        camera_str = "camera_" + user + "_" + user
        arena.Object(objName=obj_str,
                     objType=arena.Shape.circle,
                     parent=camera_str,
                     location=(-.5, 0, -.5),
                     rotation=(0, 0, 0, 1),
                     scale=(0.05, 0.05, 0.05),
                     color=color,
                     persist=True)

        print("Go to URL: https://xr.andrew.cmu.edu/?scene=" +
              scene + "&fixedCamera=" + user)

    arena.add_topic(TOPIC, on_tag_detect)
    arena.handle_events()


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
