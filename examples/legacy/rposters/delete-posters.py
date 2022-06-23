
import json
import paho.mqtt.publish as publish
import time

mqtt_host = "mqtt.arenaxr.org"
scene_path = "realm/s/theme"

def delete_obj(obj_name, topic):
    print(topic, obj_name)
    publish.single( topic, '{"object_id": "' + obj_name + '", "action": "delete"}', hostname=mqtt_host)

theme=1

for theme in range(1,7):
    paparentName = 't' + str(theme) + '_poster_area_parent'
    delete_obj(paparentName, scene_path + str(theme))
    for pindex in range(1,11):

        prootName  = 't' + str(theme) + '_poster' + str(pindex) + '_root'
        pwallName  = 't' + str(theme) + '_poster' + str(pindex) + '_wall'
        pimgName   = 't' + str(theme) + '_poster' + str(pindex) + '_img'
        plightName = 't' + str(theme) + '_poster' + str(pindex) + '_light'
        plblName   = 't' + str(theme) + '_poster' + str(pindex) + '_lbl'
        ppdflnkName = 't' + str(theme) + '_poster' + str(pindex) + '_pdflink'
        pvideolnkName = 't' + str(theme) + '_poster' + str(pindex) + '_videolink'
        pavideolnkName = 't' + str(theme) + '_poster' + str(pindex) + '_supvideolink'
        dboardName = 't' + str(theme) + '_poster' + str(pindex) + '_demo_board'
        dboardlblName = 't' + str(theme) + '_poster' + str(pindex) + '_demo_board_lbl'

        delete_obj(prootName, scene_path + str(theme))
        delete_obj(pwallName, scene_path + str(theme))
        delete_obj(pimgName, scene_path + str(theme))
        delete_obj(plightName, scene_path + str(theme))
        delete_obj(plblName, scene_path + str(theme))
        delete_obj(ppdflnkName, scene_path + str(theme))
        delete_obj(pvideolnkName, scene_path + str(theme))
        delete_obj(pavideolnkName, scene_path + str(theme))
        delete_obj(dboardName, scene_path + str(theme))
        delete_obj(dboardlblName, scene_path + str(theme))

