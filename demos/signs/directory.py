# robot-arm.py
#

import time
import arena
import random
import os
import json
import sys 

# export HOST=arena.andrew.cmu.edu
# export REALM=realm
# export HOST=arena.andrew.cmu.edu
# export MID=MID_1234
# Optional:
# export LINKS = "Link1,https://www.duckduckgo.com,Link 2,https:www.f1.com,Link 3,https://www.eet.com"
# export LOC = "3,0,-10"

# LINKS env will overwrite this default:
sign_links =  ['Link 1','https://www.duckduckgo.com','sametab','Link 2','https://www.f1.com','sametab','Link 3','https://www.eet.com','sametab']
# Loc env will overwrite this default:
sign_location = [3,0,-10]

def draw_ray(click_pos, position):
    line = arena.Object(
        objType=arena.Shape.thickline,
        thickline=arena.Thickline( # slightly below camera so you can see line vs head-on
            {
                (click_pos[0],click_pos[1]-0.2,click_pos[2]),
                (position[0],position[1],position[2])
            },5,"#FF00FF")
    )
    time.sleep(.25)
    line.delete()


def dir_add_element(MID,title,link,mode,entry,signCnt):
    print("Sign CNT: " + str(signCnt) + " Entry: " + str(entry))
    dataStr='{"goto-url": { "dest":"' + mode + '", "on": "mousedown", "url": "' + link + '"} } '
    target1 = arena.Object(
                objName=MID+"target_"+str(signCnt) + "_" + str(entry),
                objType=arena.Shape.cube,
                scale=(5.0,0.30,0.1),
                location=( 0,3-entry*0.4, -0.1),
                color=(255,255,255),
                clickable=True,
                data=dataStr,
               # transparency=arena.Transparency(True, 0),
		        persist=True,
                parent=MID+"signParent"+str(signCnt)
    )


    #dataStr='{"text":{ "anchor":left, "wrapCount":100, "value":"Definitely not working..." } } '
    text1 = arena.Object(
                objName=MID+"text_"+str(signCnt) + "_" + str(entry),
                objType=arena.Shape.text,
                scale=(1.0,0.5,0.3),
                location=( 0,3-entry*0.4, 0),
                clickable=False,
                text=title,
                data=dataStr,
                color=(100,100,255),
		        persist=True,
                parent=MID+"signParent"+str(signCnt)
    )









# start the fun shall we?

if (os.environ.get('SCENE') is not None) and (os.environ.get('REALM') is not None) and (os.environ.get('HOST') is not None) and (os.environ.get('MID') is not None):
    SCENE = os.environ["SCENE"]
    HOST = os.environ["HOST"]
    REALM = os.environ["REALM"]
    MID = os.environ["MID"]
    print("Loading (prgm,scene,real,host,MID): " + sys.argv[0]  + "," + SCENE + "," + REALM + "," + HOST + "," + MID)
    MID = MID + '-'
else:
    print( "You need to set SCENE, HOST, MID and REALM as environmental variables to specify the program target")
    print( "\nFor bash you can copy paste the following before running:")
    print( "export MID=dir")
    print( "export HOST=arena.andrew.cmu.edu")
    print( "export REALM=realm")
    print( "export SCENE=example")
    exit(-1)

if os.environ.get('LINKS') is not None:
    # Links is base64 encoded
    LINKS = os.environ["LINKS"]
#    LINKS = unquote(LINKS)
    # take the string and parse out CSV parameters
    print( "LINKS:" + LINKS)
    sign_links= LINKS.split(",")

if os.environ.get('LOC') is not None:
    # Links is base64 encoded
    LOC = os.environ["LOC"]
    print( "LOC:" + LOC)
    # take the string and parse out CSV parameters
    sign_location = LOC.split(",")




arena.init(HOST, REALM, SCENE)

if os.environ.get('JSONCFG') is not None:
    # Links is base64 encoded
    JFILE = os.environ["JSONCFG"]
    print( "JSONCFG:" + JFILE)
    signData=None
    with open(JFILE) as dataFile:
        signData = json.load(dataFile)
        cnt=1
        for key in signData:
            value = signData[key]
            print("Sign Title: " + key)
            signParent = arena.Object(
                persist=True,
                objName=MID+"signParent"+str(cnt),
                objType=arena.Shape.cube,
                location=(0, 0, 0),
                transparency=arena.Transparency(True, 0),
            )
            entry=0
            for key2 in value:
                if "link" in key2:
                    print("\tTitle " + value[key2][0])
                    print("\tLink " + value[key2][1])
                    print("\tMode " + value[key2][2])
                    dir_add_element(MID,value[key2][0], value[key2][1], value[key2][2],entry,cnt)
                    entry+=1
            sign_location=value["position"]
            sign_rotation=value["rotation"]
            sign_scale=value["scale"]
            signParent.update(location=(float(sign_location[0]),float(sign_location[1]),float(sign_location[2])))
            signParent.update(rotation=(float(sign_rotation[0]),float(sign_rotation[1]),float(sign_rotation[2]),float(sign_rotation[3])))
            signParent.update(scale=(float(sign_scale[0]),float(sign_scale[1]),float(sign_scale[2])))
            cnt+=1
    


print("starting sign main loop")




print( "Go to URL: https://" + HOST + "/" + SCENE)

time.sleep(1)
print("Signs Made")
#arena.handle_events()
