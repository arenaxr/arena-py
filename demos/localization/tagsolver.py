''' Publish rig transforms using apriltags for global localization
'''
import getopt
import json
import pose
import sys
from types import SimpleNamespace
sys.path.append('..')
import arena


BROKER = 'oz.andrew.cmu.edu'
REALM = 'realm'
TOPIC = REALM + '/g/a/#'

DTAG_ERROR_THRESH = 5e-6    # tag detection error units?
MOVE_THRESH = .05           # 5cm
ROT_THRESH = .087           # 5deg
DEBUG = True

vio_state = {}


def log(*s):
    if DEBUG:
        print(*s)


def printhelp():
    print('tagsolver.py -s <scene>')
    print('   ex: python3 tagsolver.py -s myScene')


def dict_to_sns(d):
    return SimpleNamespace(**d)


def vio_filter(vio, client_id):
    global vio_state
    vio_pose_last = vio_state.get(client_id)
    if vio_pose_last is None:
        vio_state[client_id] = vio
        return False
    pos_diff, rot_diff = pose.pose_diff(vio, vio_pose_last)
    vio_state[client_id] = vio
    if pos_diff > MOVE_THRESH or rot_diff > ROT_THRESH:
        return False
    return True


def on_tag_detect(msg):
    json_msg = json.loads(msg.payload.decode('utf-8'), object_hook=dict_to_sns)
    client_id = msg.topic.split('/')[-1]
    dtag = json_msg.detections[0]
    if not hasattr(dtag, 'refTag'):
        print('tag not in atlas:', dtag.id)
        return
    vio_pose = pose.get_vio_pose(json_msg)
    if not vio_filter(vio_pose, client_id):
        log('too much movement')
        return
    rig_pose, dtag_error = pose.get_rig_pose(json_msg)
    if dtag_error > 5e-6:
        log('too much detection error')
        return
    rig_pos, rig_rotq = pose.matrix4_to_pose(rig_pose)
    log('Localizing', client_id, 'on', str(dtag.id))
    mqtt_response = {
        'object_id': client_id,
        'action': 'update',
        'type': 'rig',
        'data': {
            'position': {
                'x': rig_pos[0],
                'y': rig_pos[1],
                'z': rig_pos[2]
            },
            'rotation': {
                'x': rig_rotq[0],
                'y': rig_rotq[1],
                'z': rig_rotq[2],
                'w': rig_rotq[3]
            }
        }
    }
    arena.arena_publish('realm/s/' + json_msg.scene, mqtt_response)


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

    if scene is None:
        printhelp()
        sys.exit(1)

    print('Scene:', scene)
    arena.init(BROKER, REALM, scene)
    print('Go to URL: https://xr.andrew.cmu.edu/?networkedTagSolver=true&scene=' + scene + '&fixedCamera=<username>')
    arena.add_topic(TOPIC, on_tag_detect)
    arena.handle_events()


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
