''' Synchronize users for ground truth collection with apriltags
'''
from datetime import datetime
import getopt
import json
import pose
import sys
from types import SimpleNamespace
sys.path.append('..')
import arena

BROKER = 'oz.andrew.cmu.edu'
REALM = 'realm'
TOPIC_DETECT = REALM + '/g/a/#'
TOPIC_VIO = '/topic/vio/#'
TOPIC_UWB = REALM + '/g/uwb/#'
TIME_FMT = '%Y-%m-%dT%H:%M:%S.%fZ'
TIME_FMT_UWB = '%Y-%m-%dT%H:%M:%S.%f'
OUTFILE = datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + '.txt'

STATE_WALK = 0
STATE_FINDTAG = 1
STATE_WAIT = 2
COLOR_WALK = (0, 255, 0)
COLOR_FINDTAG = (255, 0, 0)
COLOR_WAIT = (0, 0, 255)
MOVE_THRESH = .05   # 5cm
ROT_THRESH = .087   # 5deg
TIME_THRESH = 3     # 3sec
DTAG_ERROR_THRESH = 5e-6    # tag detection error units?
TIME_INTERVAL = 10          # 10sec

users = {}
last_detection = datetime.min


class SyncUser:
    def __init__(self, arenaname, uwbname):
        self.hud = arena.Object(objName='circle_' + arenaname,
                                parent='camera_' + arenaname + '_' + arenaname,
                                objType=arena.Shape.circle,
                                location=(0, 0, -0.5),
                                rotation=(0, 0, 0, 1),
                                scale=(0.02, 0.02, 0.02),
                                persist=True)
        self.arenaname = arenaname
        self.uwbname = uwbname
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
            pos_diff, rot_diff = pose.pose_diff(vio, self.last_vio)
            time_diff = (time - self.last_time).total_seconds()
            if pos_diff > MOVE_THRESH or rot_diff > ROT_THRESH or time_diff > TIME_THRESH:
                self.state = STATE_FINDTAG
                self.hud.update(color=COLOR_FINDTAG)

    def on_timer(self):
        if self.state == STATE_WALK:
            self.state = STATE_FINDTAG
            self.hud.update(color=COLOR_FINDTAG)


def printhelp():
    print('gt-sync.py -s <scene> <arenaname1> <uwbname1> [arenaname2 uwbname2 ...]')
    print('   ex: python3 gt-sync.py -s myScene nuno 1 john 2')


def dict_to_sns(d):
    return SimpleNamespace(**d)


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
        cam_pose, dtag_error = pose.get_cam_pose(json_msg)
        if dtag_error > DTAG_ERROR_THRESH:
            return
        vio_pose = pose.get_vio_pose(json_msg)
        time = datetime.strptime(json_msg.timestamp, TIME_FMT)
        users[client_id].on_tag_detect(cam_pose, vio_pose, time)
        if all(users[u].state == STATE_WAIT for u in users):
            data = {'timestamp': time.strftime(TIME_FMT_UWB), 'type': 'gt', 'poses': [{'user': users[u].arenaname, 'pose': users[u].pose.tolist()} for u in users]}
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
        vio_pose = pose.get_vio_pose(json_msg)
        time = datetime.strptime(json_msg.timestamp, TIME_FMT)
        users[client_id].on_vio(vio_pose, time)
        data = {'timestamp': time.strftime(TIME_FMT_UWB), 'type': 'vio', 'user': users[client_id].arenaname, 'pose': vio_pose.tolist()}
        with open(OUTFILE, 'a') as outfile:
            outfile.write(json.dumps(data))
            outfile.write(',\n')
        if (time - last_detection).total_seconds() > TIME_INTERVAL:
            for u in users:
                users[u].on_timer()


def on_uwb(msg):
    pass
    # json_msg = json.loads(msg.payload.decode('utf-8'), object_hook=dict_to_sns)
    # time = datetime.strptime(json_msg.timestamp, TIME_FMT_UWB)
    # data = {'timestamp': time.strftime(TIME_FMT_UWB), 'type': 'uwb', 'src': , 'dst': , 'range': , 'ble_rssi', }
    # with open(OUTFILE, 'a') as outfile:
    #     outfile.write(json.dumps(data))
    #     outfile.write(',\n')


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
        else:
            printhelp()
            sys.exit(1)

    if scene is None or len(args) < 1 or len(args) % 2 > 0:
        printhelp()
        sys.exit(1)

    arena.init(BROKER, REALM, scene)
    for arenaname, uwbname in zip(args[::2], args[1::2]):
        users['camera_' + arenaname + '_' + arenaname] = SyncUser(arenaname, uwbname)
        print("Go to URL: https://xr.andrew.cmu.edu/?networkedTagSolver=true&scene=" + scene + "&fixedCamera=" + arenaname)

    arena.add_topic(TOPIC_DETECT, on_tag_detect)
    arena.add_topic(TOPIC_VIO, on_vio)
    arena.add_topic(TOPIC_UWB, on_uwb)
    arena.handle_events()


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
