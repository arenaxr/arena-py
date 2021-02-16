import time
import os
import json
from arena import *



# defaults
persist=True # False=objects will disappear after a reload (and only appear to clients already viewing the scene when they are created)
sign_frame_color = Color(150, 150, 150) # color of the wall
sign_panel_color = Color(255, 255, 255) # color of the wall
#title_text_color = Color(225, 75, 40)
title_text_color = Color(0, 55, 95)
link_text_color = Color(0, 0, 0)
title_text_font = 'exo2bold'
link_text_font = 'exo2semibold'
title_text_font_width = 5
link_text_font_width = 4


arena = Arena(host="arena.andrew.cmu.edu",realm="realm",scene="example")

print( "Starting up")

@arena.run_once
def draw_signs():
    if os.environ.get('JSONCFG') is not None:
        JFILE = os.environ["JSONCFG"]
        print( "JSONCFG:" + JFILE)
        signData=None
        with open(JFILE) as dataFile:
            signData = json.load(dataFile)
            cnt=1
            for key in signData:
                value = signData[key]
                print("Sign Title: " + key)
                print( "Directory Title: " + value["title"])
                title_text = value["title"]

                root_name = "sign_" + str(cnt)
                print( "Root Name: " + root_name)
                # invisible root object; all other objects children of this object
                root = Object(
                    object_id=root_name,
                    object_type='entity',
                    material=Material(transparent=True),
                    persist=persist
                )
                arena.add_object(root)

                titleText = Text(
                    object_id=root_name+"_title",
                    position=Position(0.1, 3.3, 0),
                    text=title_text,
                    material=Material(color=title_text_color),
                    font=title_text_font,
                    width=title_text_font_width,
                    persist=persist,
                    parent=root_name
                )
                arena.add_object(titleText)

                entry=0
                for key2 in value:
                    if "link" in key2:
                        print("\tTitle " + value[key2][0])
                        print("\tLink " + value[key2][1])
                        print("\tMode " + value[key2][2])
                        link_text = value[key2][0]
                        link_url = value[key2][1]
                        link_mode = value[key2][2]

                        linkBox = Box(
                            object_id=root_name+"_panel_" + str(entry),
                            position=Position(0, 3-(entry*0.4), -0.1),
                            width=5.0,
                            height=0.30,
                            depth=0.1,
                            material=Material(color=sign_panel_color),
                            clickable=True,
                            goto_url=GotoUrl(dest=link_mode,on="mousedown", url=link_url),
                            persist=persist,
                            parent=root_name
                        )
                        arena.add_object(linkBox)

                        linkText = Text(
                            object_id=root_name+"_text_" + str(entry),
                            position=Position(0.1, 3-(entry*0.4), 0),
                            text=link_text,
                            material=Material(color=link_text_color),
                            font=link_text_font,
                            width=link_text_font_width,
                            wrapCount=60,
                            parent=root_name,
                            persist=persist
                        )
                        arena.add_object(linkText)

                        entry+=1

                signFrame = Box(
                    object_id=root_name+"_frame",
                    position=Position(0, 3.55-entry*0.25, -0.2),
                    width=4.5,
                    height=entry*0.5,
                    depth=0.2,
                    material=Material(color=sign_frame_color),
                    clickable=True,
                    goto_url=GotoUrl(dest=link_mode,on="mousedown", url=link_url),
                    persist=persist,
                    parent=root_name
                    )
                arena.add_object(signFrame)

                sign_position=value["position"]
                sign_rotation=value["rotation"]
                sign_scale=value["scale"]
                print( "Moving to location:" + str(sign_position))
                print( "Setting Rotation to:" + str(sign_rotation))
                print( "Setting Scale to:" + str(sign_scale))
                root.update_attributes(position=sign_position)
                root.update_attributes(rotation=sign_rotation)
                root.update_attributes(scale=sign_scale)

                arena.update_object(root)
                cnt+=1
    else:
        print( "Need to add environmental variable to point to jason file")
        print( "export JSONCFG=directory_cfg.json")

    print("\n\nProgram done, press ctrl-c to exit")
    arena.stop_tasks()

arena.run_tasks()
