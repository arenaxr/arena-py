''' Synchronize users for ground truth collection with apriltags
'''
import arena
import getopt
import numpy as np
import paho.mqtt.client as mqtt
import sys


def printhelp():
    print('gt-sync.py [-s <scene>] <user1> [user2 ...]')
    print('   ex: python3 gt-sync.py -s myScene name1 name2 name3')


def get_tag_pose(json_msg):
    # Only take first marker for now, later iterate and avg all markers
    detected_tag = json_msg['detections'][0]
    pos = json_msg['vio']['position']
    rot = json_msg['vio']['rotation']

    # Construct pose matrix4 for camera
    vio_pose = np.identity(4)
    vio_pose[0:3, 0:3] = Rotation.from_quat(
        [rot._x, rot._y, rot._z, rot._w]
    ).as_matrix()
    vio_pose[0:3, 3] = [pos.x, pos.y, pos.z]

    # Construct pose matrix for detected tag
    dtag_pose_s1 = np.identity(4)
    # Correct for column-major format of detected tag pose
    R_correct = np.array(detected_tag.pose.R).T
    dtag_pose_s1[0:3, 0:3] = R_correct
    dtag_pose_s1[0:3, 3] = detected_tag.pose.t
    # Swap x/y axis of detected tag coordinate system
    dtag_pose_s1 = np.array(FLIP) @ dtag_pose_s1 @ np.array(FLIP)
    dtag_error_s1 = detected_tag.pose.e

    # Construct pose matrix for detected tag
    dtag_pose_s2 = np.identity(4)
    # Correct for column-major format of detected tag pose
    R_correct = np.array(detected_tag.pose.asol.R).T
    dtag_pose_s2[0:3, 0:3] = R_correct
    dtag_pose_s2[0:3, 3] = detected_tag.pose.asol.t
    # Swap x/y axis of detected tag coordinate system
    dtag_pose_s2 = np.array(FLIP) @ dtag_pose_s2 @ np.array(FLIP)
    dtag_error_s2 = detected_tag.pose.asol.e

    return resolve_pose_ambiguity(dtag_pose_s1, dtag_error_s1, dtag_pose_s2, dtag_error_s2, vio_pose, ref_tag_pose)


def on_tag_detect():
    json_msg = None
    try:
        json_msg = json.loads(msg.payload.decode('utf-8'))
    except ValueError:
        return
    client_id = msg.topic.split('/')[-1]
    if 'vio' in json_msg:
        detected_tag = json_msg['detections'][0]
        pos = json_msg['vio']['position']
        rot = json_msg['vio']['rotation']


def main():
    BROKER = 'oz.andrew.cmu.edu'
    REALM = 'realm'
    TOPIC = REALM + '/g/a/#'
    COLOR_WALK = (0, 255, 0)
    COLOR_FINDTAG = (255, 0, 0)
    COLOR_WAIT = (255, 255, 0)
    scene = 'cic-tags'

    try:
        opts, users = getopt.getopt(sys.argv[1:], 'hs:', ['scene='])
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
    print("Users: " + str(users))

    arena.init(BROKER, REALM, scene)
    for user in users:
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
