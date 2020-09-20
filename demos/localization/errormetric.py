''' Evaluate error metric at different distances
'''
import getopt
import numpy as np
import pose
import sys
sys.path.append('..')
import arena


BROKER = 'oz.andrew.cmu.edu'
REALM = 'realm'


def printhelp():
    print('errormetric.py -s <scene>')
    print('   ex: python3 errormetric.py -s myScene')


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
    if scene is None or userfile is None:
        printhelp()
        sys.exit(1)

    arena.init(BROKER, REALM, scene)
    print("Go to URL: https://xr.andrew.cmu.edu/?networkedTagSolver=true&scene=" + scene + "&fixedCamera=" + user.arenaname)
    arena.handle_events()


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
