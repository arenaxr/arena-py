''' Synchronize users for ground truth collection with apriltags
'''
from datetime import datetime
import json
import getopt
import numpy as np
import pose
import sys
from types import SimpleNamespace
sys.path.append('..')
import arena

BROKER = 'oz.andrew.cmu.edu'
REALM = 'realm'
TOPIC_DETECT = REALM + '/g/a/#'
TOPIC_VIO = '/topic/vio/#'
TIME_FMT = '%Y-%m-%dT%H:%M:%S.%fZ'
OUTFILE = datetime.now().strftime(TIME_FMT) + '.txt'
STATE_WALK = 0
STATE_FINDTAG = 1
STATE_WAIT = 2
COLOR_WALK = (0, 255, 0)
COLOR_FINDTAG = (255, 0, 0)
COLOR_WAIT = (0, 0, 255)
DTAG_ERROR_THRESH = 5e-6
MOVE_THRESH = .05   # 5cm
ROT_THRESH = .087   # 5deg
TIME_THRESH = 3     # 3sec
TIME_INTERVAL = 10  # 10sec

users = {}
last_detection = datetime.min


class SyncUser:
    def __init__(self, client_id):
        self.hud = arena.Object(objName='circle_' + client_id,
                                parent=client_id,
                                objType=arena.Shape.circle,
                                location=(0, 0, -0.5),
                                rotation=(0, 0, 0, 1),
                                scale=(0.02, 0.02, 0.02),
                                persist=True)
        self.reset()

    def reset(self):
        self.pose = None
        self.last_time = datetime.min
        self.state = STATE_WALK
        self.hud.update(color=COLOR_WALK)

    def on_tag_detect(self, cam_pose, vio, time):
        self.pose = cam_pose
        self.last_vio = vio
        self.last_time = time
        if self.state == STATE_FINDTAG:
            self.state = STATE_WAIT
            self.hud.update(color=COLOR_WAIT)

    def on_vio(self, vio, time):
        if self.state == 2:
            pos_diff, rot_diff = pose.pose_diff(self.last_vio, vio)
            time_diff = (time - self.last_time).total_seconds()
            if pos_diff > MOVE_THRESH or rot_diff > ROT_THRESH or time_diff > TIME_THRESH:
                self.state = STATE_FINDTAG
                self.hud.update(color=COLOR_FINDTAG)

    def on_timer(self):
        if self.state == STATE_WALK:
            self.state = STATE_FINDTAG
            self.hud.update(color=COLOR_FINDTAG)


def printhelp():
    print('gt-sync.py -s <scene> <user1> [user2 ...]')
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
    return pose.resolve_pose_ambiguity(dtag_pose1, dtag_error1, dtag_pose2, dtag_error2, vio_pose, reftag_pose)


def on_tag_detect(msg):
    global users
    global last_detection
    json_msg = json.loads(msg.payload.decode('utf-8'), object_hook=dict_to_sns)
    client_id = msg.topic.split('/')[-1]
    if client_id not in users:
        return
    if hasattr(json_msg, 'detections'):
        dtag = json_msg.detections[0]
        if not hasattr(dtag, 'refTag'):
            print('tag not in atlas: ' + dtag.id)
            return
        dtag_pose, dtag_error = get_tag_pose(json_msg)
        if dtag_error > DTAG_ERROR_THRESH:
            return
        reftag_pose = pose.reftag_pose_to_matrix4(dtag.refTag.pose)
        cam_pose = reftag_pose @ np.linalg.inv(dtag_pose)
        vio_pose = pose.pose_to_matrix4(json_msg.vio.position, json_msg.vio.rotation)
        time = datetime.strptime(json_msg.timestamp, TIME_FMT)
        users[client_id].on_tag_detect(cam_pose, vio_pose, time)
        if all(users[u].state == STATE_WAIT for u in users):
            data = {'timestamp': time.strftime(TIME_FMT), 'type': 'gt', 'poses': [{'user': u, 'pose': users[u].pose.tolist()} for u in users]}
            print(data)
            with open(OUTFILE, 'a') as outfile:
                outfile.write(json.dumps(data))
                outfile.write(',\n')
            last_detection = time
            for u in users:
                users[u].reset()


def on_vio(msg):
    global users
    global last_detection
    json_msg = json.loads(msg.payload.decode('utf-8'), object_hook=dict_to_sns)
    client_id = msg.topic.split('/')[-1]
    if client_id not in users:
        return
    if hasattr(json_msg, 'object_id') and json_msg.object_id.endswith('_local'):
        vio_pose = pose.pose_to_matrix4(json_msg.data.position, json_msg.data.rotation)
        time = datetime.strptime(json_msg.timestamp, TIME_FMT)
        data = {'timestamp': time.strftime(TIME_FMT), 'type': 'vio', 'user': client_id, 'pose': vio_pose.tolist()}
        with open(OUTFILE, 'a') as outfile:
            outfile.write(json.dumps(data))
            outfile.write(',\n')
        users[client_id].on_vio(vio_pose, time)
        if (time - last_detection).total_seconds() > TIME_INTERVAL:
            for u in users:
                users[u].on_timer()


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hs:', ['scene='])
    except getopt.GetoptError:
        printhelp()
        sys.exit(1)

    scene = None
    for opt, arg in opts:
        if opt == '-h':
            printhelp()
            sys.exit(1)
        elif opt in ('-s', '--scene'):
            scene = arg

    if scene is None or len(args) < 1:
        printhelp()
        sys.exit(1)

    print("Scene: " + scene)
    print("Users: " + str(args))

    arena.init(BROKER, REALM, scene)
    for username in args:
        client_id = 'camera_' + username + '_' + username
        users[client_id] = SyncUser(client_id)
        print("Go to URL: https://xr.andrew.cmu.edu/?networkedTagSolver=true&scene=" + scene + "&fixedCamera=" + username)

    arena.add_topic(TOPIC_DETECT, on_tag_detect)
    arena.add_topic(TOPIC_VIO, on_vio)
    arena.handle_events()


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
