''' Synchronize users for ground truth collection with apriltags
'''
import arena
import getopt
import paho.mqtt.client as mqtt
import sys


def printhelp():
    print('gt-sync.py [-s <scene>] <user1> [user2 ...]')
    print('   ex: python3 gt-sync.py -s myScene name1 name2 name3')


def on_tag_detect():
    pass


def main():
    BROKER = 'oz.andrew.cmu.edu'
    PORT = 1883
    REALM = 'realm'
    CLIENT_ID = "gt-sync_" + str(random.randint(0, 100))
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

        print("Go to URL: https://xr.andrew.cmu.edu/?scene=" + scene + "&fixedCamera=" + user)

    arena.handle_events()

    mqttc = mqtt.Client(CLIENT_ID, clean_session=True, userdata=None)
    mqttc.connect(BROKER, PORT)
    print("Connected MQTT")
    mqttc.subscribe(TOPIC)
    mqttc.message_callback_add(TOPIC, on_tag_detect)
    mqttc.loop_forever()


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
