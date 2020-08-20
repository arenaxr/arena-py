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
COLOR_WAIT = (0, 0, 255)
DTAG_ERROR_THRESH = 5e-6
MOVE_THRESH = .05   # 5cm
ROT_THRESH = .087   # 5deg
TIME_THRESH = 3     # 3sec
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
                         persist=True)


class SyncUser:
    def __init__(self, name):
        self.hud = SyncHUD(name)
        self.pose = None
        self.last_time = datetime.min
        self.state = 0
        self.hud.update(color=COLOR_WALK)

    def on_tag_detect(self, cam_pose, vio, time):
        global users
        self.pose = cam_pose
        self.last_vio = vio
        self.last_time = time
        if self.state == 1:
            self.state = 2
            self.hud.update(color=COLOR_WAIT)
        if all(users[user].state == 2 for user in users):
            for user in users:
                users[user].state = 0
                users[user].hud.update(color=COLOR_WALK)

    def on_vio(self, vio, time):
        if self.state == 2:
            pos_diff, rot_diff = pose.pose_diff(self.last_vio, vio)
            time_diff = time - self.last_time
            if pos_diff > MOVE_THRESH or rot_diff > ROT_THRESH or time_diff > TIME_THRESH:
                self.state = 1
                self.hud.update(color=COLOR_FINDTAG)


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
    if client_id not in users:
        return
    if hasattr(json_msg, 'detections'):
        dtag = json_msg.detections[0]
        dtag_pose, dtag_error = get_tag_pose(json_msg)
        if dtag_error > DTAG_ERROR_THRESH:
            return
        reftag_pose = pose.reftag_pose_to_matrix4(dtag.refTag.pose)
        cam_pose = reftag_pose @ np.linalg.inv(dtag_pose)
        vio_pose = pose.pose_to_matrix4(
            json_msg.vio.position, json_msg.vio.rotation)
        time = datetime.strptime(json_msg.timestamp, TIME_FMT)
        users[client_id].on_tag_detect(cam_pose, vio_pose, json_msg.timestamp)
    elif hasattr(json_msg, 'object_id') and json_msg.object_id.endswith('_local'):
        vio_pose = pose.pose_to_matrix4(
            json_msg.data.position, json_msg.data.rotation)
        time = datetime.strptime(json_msg.timestamp, TIME_FMT)
        users[client_id].on_vio(vio_pose, time)


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
