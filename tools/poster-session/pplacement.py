import argparse
import math
import os
import re
import time

import yaml
from gcwrapper import GoogleClientWrapper
from layout import Layout

from arena import *
from arena.attributes.landmark import (
    Landmark,  # manually import Landmark, while arena-py does not do it
)

DFT_CONFIG_FILENAME='./config.yaml'

def parse_button(button_markup):
    '''Parse a button markup in the form:
       [icon:text](link)
    '''
    pattern = re.compile('^\[(video|link|catalog|pdf)\:(.*)\]\((.*)\)')
    result = pattern.match(button_markup)
    if bool(result) == False:
        raise Exception('Failed parsing button markup!')

    if not len(result.groups()) == 3:
        raise Exception('Failed parsing button markup!')

    return result.groups()

def parse_int(dict, key, default):
    '''Get a string with a color (as 'red, green, blue') from a dictionary passed as argument
       Parse the string and return a (red, green, blue) tuple
    dict:
      the dictionary with the color string (as 'red, green, blue')
    key:
      key where the color string is
    default:
      default color string value, if key does not exist

    Returns a (red, green, blue) tuple
    '''
    str = dict.get(key, default)
    return tuple(map(int, str.split(',')))

def parse_float(dict, key, default):
    '''Get a string with a position (as '0, 0, 0') from a dictionary passed as argument
       Parse the string and return a (0, 0, 0) tuple
    dict:
      the dictionary with the position string (as '0, 0, 0')
    key:
      key where the position string is
    default:
      default position string value, if key does not exist

    Returns a (0, 0, 0) tuple
    '''
    str = dict.get(key, default)
    return tuple(map(float, str.split(',')))

def make_wall(name_suffix, position, rotation, wall_data, config, args):
    '''Create a demo wall
    args:
    name_suffix
      name suffix used for objects created in the scene
    location
      x, y, z position of wall
    rotation
      rotation of the wall
    wall_data
      data about the wall
    config
      the config

    return: a list of img buttons added to this wall
    '''
    # default persit to False
    persist = config.get('persist', False)

    # to save file to gdrive
    gcw = GoogleClientWrapper()

    # get wall config
    wall_config         = config.get('wall', {})
    wall_width          = wall_config.get('width', 9)
    wall_height         = wall_config.get('height', 6)
    wall_depth          = wall_config.get('depth', 1)
    img_height          = wall_config.get('img_height', 2.6)
    wall_color          = parse_int(wall_config, 'color', '151, 171, 216')
    img_btn_color       = parse_int(wall_config, 'img_btn_color', '255, 255, 255')
    img_btn_text_color  = parse_int(wall_config, 'img_btn_text_color', '0, 0, 0')
    text_color          = parse_int(wall_config, 'text_color', '0, 66, 117')
    back_text_color     = parse_int(wall_config, 'back_text_color', '96, 122, 163')
    text_font           = wall_config.get('text_font', 'exo2bold')
    title_maxlen        = wall_config.get('title_maxlen', 150)
    landmark_offset_dist= wall_config.get('landmark_offset_dist', 4)
    wall_offset         = parse_float(wall_config, 'wall_offset', '0, 0, 0')
    btn_scale           = Scale(wall_width/15, wall_width/15, 1)

    # these will be the name of the objects in the scene
    root_name           = f'{name_suffix}'
    wall_name           = f'poster_wall_{name_suffix}'
    img_name            = f'poster_img_{name_suffix}'
    light_name          = f'poster_light_{name_suffix}'
    lbl_title_name      = f'poster_lbltitle_{name_suffix}'
    lbl_authors_name    = f'poster_lblauthors_{name_suffix}'
    lbl_back_name       = f'poster_lblback_{name_suffix}'
    lbl_back_title_name = f'poster_lblbacktitle_{name_suffix}'
    lbl_btn1            = f'poster_lblbutton1_{name_suffix}'
    lbl_btn2            = f'poster_lblbutton2_{name_suffix}'
    b1_name             = f'poster_button1_{name_suffix}'
    b2_name             = f'poster_button2_{name_suffix}'

    # title
    title_cut = f'Poster_{name_suffix}' # init to a default value; used as landmark title if getting title from dictionary fails
    try:
        title_cut = f'{wall_data["title"][0:title_maxlen]}' # cut title; raise exception if key does not exist
        if len(wall_data["title"]) > title_maxlen: title_cut = title_cut + '...'
    except Exception as err:
        print(f'Could not get wall title: {err}')

    # TODO: (mwfarb) move this offsetPosition calc to landmark.js perhaps?
    # calc offsetPosition in world coordinates to match rotation
    if len(title_cut) == 0:
        landmark=None
    else:
        radius = landmark_offset_dist
        angle = (rotation.y+90) * (math.pi/180)
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        landmark = Landmark(
            label=title_cut,
            offsetPosition={"x": round(-x, 3), "y": 0, "z": round(z, 3)},
            randomRadiusMin=.5,
            randomRadiusMax=1,
            constrainToNavMesh="coplanar",
            lookAtLandmark=True)

    # invisible root object; all other objects are children of this object
    root = Object(
        object_id=root_name,
        object_type='entity',
        persist=persist,
        position=position,
        rotation=rotation,
        material=Material(transparent=True),
        landmark=landmark
    )
    scene.add_object(root)

    # back wall
    if args.no_wall:
        delete(wall_name)
    else:
        wall = Box(
            object_id=wall_name,
            parent=root_name,
            persist=persist,
            position=Position(wall_offset[0], (wall_height/2)+wall_offset[1], wall_offset[2]),
            width=wall_width,
            height=wall_height,
            depth=wall_depth,
            color=wall_color
        )
        scene.add_object(wall)

    # title
    if args.no_text:
        delete(lbl_title_name)
        delete(lbl_back_title_name)
        delete(lbl_authors_name)
    else:
        try:
            lbltitle = Text(
                object_id=lbl_title_name,
                parent=root_name,
                persist=persist,
                position=Position(wall_offset[0], wall_offset[1]+(wall_height*1.1), wall_offset[2]+(wall_depth/2)+.010),
                value=title_cut,
                color=text_color,
                font=text_font,
                width=wall_width*.9,
            )
            scene.add_object(lbltitle)

            # title, back
            lbltitleb = Text(
                object_id=lbl_back_title_name,
                parent=root_name,
                persist=persist,
                position=Position(wall_offset[0], wall_offset[1]+(wall_height*.75), wall_offset[2]-(wall_depth/2)-.05),
                rotation=Rotation(0, 180, 0),
                value=title_cut,
                color=back_text_color,
                font=text_font,
                width=wall_width*.9,
            )
            scene.add_object(lbltitleb)

        except Exception as err:
            print(f'Could not add wall title: {err}')

        try:
            # authors
            lbl = Text(
                object_id=lbl_authors_name,
                parent=root_name,
                persist=persist,
                position=Position(wall_offset[0], wall_offset[1]+wall_height, wall_offset[2]+(wall_depth/2)+.010),
                value=f'{wall_data["authors"][0:100]}', # raise exception if key does not exist
                color=text_color,
                font=text_font,
                #wrapCount=100,
                width=wall_width*.8,
            )
            scene.add_object(lbl)
        except Exception as err:
            print(f'Could not add wall authors: {err}')

    try:
        img_url = wall_data.get('image_url') # deal with previous versions of the spreadsheet
        if not img_url:
            img_url=wall_data['image_url_1'] # raise exception if key does not exist

        # image on the wall
        img = Image(
            object_id=img_name,
            parent=root_name,
            persist=persist,
            position=Position(wall_offset[0], wall_offset[1]+img_height, wall_offset[2]+(wall_depth/2)+.010),
            scale=Scale(wall_width*.80,wall_height*.675,1),
            url=img_url,
            material=Material(shader="flat"),
            clickable=(len(title_cut) is not 0),
        )

        scene.add_object(img)
    except Exception as err:
        print(f'Could not add wall image: {err}')



    # get list of additional images
    img_btns = {}
    for img_key in ['image_url_1', 'image_url_2', 'image_url_3', 'image_url_4']:
        img = wall_data.get(img_key)
        if img:
            btn_name = f'poster_imgbtn_{name_suffix}_{img_key}'
            img_btns[btn_name] = {'img_object_id': img_name, 'img_url': img}
            #btn_list.append({ 'btn_object_id': f'poster_imgbtn_{name_suffix}_{img_key}', 'img_object_id': img_name, 'img_url': img }) # remove non-existing columns or empty cells

    if len(img_btns) > 1:
        # add buttons to scroll between additional images
        i=0
        for btn in img_btns:
            img_btn = Image(
                object_id=btn,
                parent=root_name,
                persist=persist,
                position=Position(wall_offset[0]-(wall_width/2)+(btn_scale.x/2.1), wall_offset[1]+img_height + (len(img_btns)-1) * .8 / 2 - i * .8, wall_offset[2]+(wall_depth/2)+.010),
                heigh=.5,
                width=.5,
                scale=btn_scale,
                clickable=True,
                material=Material(shader="flat", color=img_btn_color),
            )
            scene.add_object(img_btn)

            # button text
            lblbtn_img = Text(
                object_id=f'{btn}_text',
                parent=btn,
                persist=persist,
                position=Position(0, 0, 0),
                value=str(i+1),
                color=img_btn_text_color,
                font=text_font,
                width=10
            )
            scene.add_object(lblbtn_img)
            i = i + 1

    try:
        if len(wall_data['button1']) > 0:
            (bicon, btext, burl) = parse_button(wall_data['button1']) # raise exception if failed to parse

            iconpath = f'{config["icons"][bicon]}' # raise exception if key does not exist

            # button1
            videolink = Image(
                object_id=b1_name,
                parent=root_name,
                persist=persist,
                position=Position(wall_offset[0]+(wall_width/2)-(btn_scale.x/2.1),wall_offset[1]+img_height + .3, wall_offset[2]+(wall_depth/2)+.010),
                scale=btn_scale,
                url=iconpath,
                clickable=True,
                goto_url=GotoUrl(dest='popup', on='mousedown', url=burl),
                material=Material(shader="flat", color=img_btn_color),
            )
            scene.add_object(videolink)

            # button text
            lblb1 = Text(
                object_id=lbl_btn1,
                parent=b1_name,
                persist=persist,
                position=Position(0, -.35, 0),
                value=btext[0:10],
                color=img_btn_text_color,
                font=text_font,
                width=4
            )
            scene.add_object(lblb1)
        else:
            delete(lbl_btn1)
            delete(b1_name)
    except Exception as err:
        print(f'Could not add button1: {err}')

    try:
        if len(wall_data['button2']) > 0:
            (bicon, btext, burl) = parse_button(wall_data['button2']) # raise exception if failed to parse

            iconpath = f'{config["icons"][bicon]}' # raise exception if key does not exist

            # button2
            videolink = Image(
                object_id=b2_name,
                parent=root_name,
                persist=persist,
                position=Position(wall_offset[0]+(wall_width/2)-(btn_scale.x/2.1), wall_offset[1]+img_height - .3, wall_offset[2]+(wall_depth/2)+.010),
                scale=btn_scale,
                url=iconpath,
                clickable=True,
                goto_url=GotoUrl(dest='popup', on='mousedown', url=burl),
                material=Material(shader="flat", color=img_btn_color),
            )
            scene.add_object(videolink)

            # button text
            lblb2 = Text(
                object_id=lbl_btn2,
                parent=b2_name,
                persist=persist,
                position=Position(0, -.35, 0),
                value=btext[0:10],
                color=img_btn_text_color,
                font=text_font,
                width=4
            )
            scene.add_object(lblb2)
        else:
            delete(lbl_btn2)
            delete(b2_name)
    except Exception as err:
        print(f'Could not add button2: {err}')


    # return list of img buttons added to this wall
    return img_btns

def delete(object_id):
    if object_id in scene.all_objects:
        scene.delete_object(scene.all_objects[object_id])


def make_walls(args):
    # get data from google spreadsheet table
    print('Getting data...')
    gcw = GoogleClientWrapper()
    data = gcw.gs_aslist(config['input_table']['spreadsheetid'], config['input_table']['named_range'])

    # filter by scenename in config
    filtered = list(filter(lambda v: v['scene'] == config['arena']['scenename'], data))

    # get layout coordinates
    t = Layout(getattr(Layout, config[config['arena']['scenename']]['layout']), filtered).get_transforms(**(config[config['arena']['scenename']]['layout_args']))

    scene.get_persisted_objs() # force update
    btns = {}
    for i in range(len(filtered)):
        # if args.fit:
        #     root_name = f"{filtered[i]['id']}"
        # else:
        root_name = f"{filtered[i]['id']}"
        if (args.keep_pose and root_name in scene.all_objects):
            persist_obj = scene.all_objects[root_name]
            position = persist_obj.data.position # keep last position from persist
            rotation = persist_obj.data.rotation # keep last rotation from persist
            if args.flip_y:
                rotation.y += 180
        else:
            position = Position(t[i]['x'], t[i]['y'], t[i]['z']) # position as given by the layout
            rotation = Rotation(t[i]['rx'],t[i]['ry'],t[i]['rz']) # rotation as given by layout

        wall_btns = make_wall(
            filtered[i]['id'], # use id as a suffix for the objects of each wall
            position,
            rotation,
            filtered[i],
            config,
            args,
        )

        btns.update(wall_btns)

    # save buttons data on gdrive
    gcw.gd_save_json(config['links_config']['fileid'], btns, f'{config["input_table"]["spreadsheetid"]}.json')

    print('\nDone. Press Ctrl+C to disconnect.')

if __name__ == '__main__':
    global config

    # get args
    parser = argparse.ArgumentParser(description=(
        "Generate a poster session layout in a given scene"))
    parser.add_argument('-c', '--conf', dest='configfile', default=DFT_CONFIG_FILENAME, action='store', type=str,
            help=f'The configuration file. Default is {DFT_CONFIG_FILENAME}')
    parser.add_argument('-n', dest='namespace', default=None,
                        help='Namespace of the poster session (e.g. wiselab, conix)')
    parser.add_argument('-s', dest='scenename', default=None,
                        help='Scenename of the poster session (e.g. theme1, theme2)')

    parser.add_argument('--keep-pose', action='store_true',
                        help='Keep position and rotation from other layout')
    parser.add_argument('--no-wall', action='store_true',
                        help='Remove backing wall behind the poster')
    parser.add_argument('--no-text', action='store_true',
                        help='Remove front and back title/author text')
    parser.add_argument('--flip-y', action='store_true',
                        help='Rotate the poster 180, requires --keep-pose')

    args = parser.parse_args()

    # load config
    with open(args.configfile) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    # save scenename in config
    if args.scenename is not None:
        config['arena']['scenename'] = args.scenename
    if args.namespace is not None:
        config['arena']['namespace'] = args.namespace

    # check config
    if (config.get('arena') == None):
        print("Config missing 'arena' section")
        exit(1)

    if (config['arena'].get('scenename') == None):
        print("Config missing 'arena.scenename'.")
        exit(1)

    if (config.get('input_table') == None):
        print("Config missing 'input_table' section")
        exit(1)

    if (config['input_table'].get('spreadsheetid') == None):
        print("Config missing 'input_table.spreadsheetid'.")
        exit(1)

    if (config['input_table'].get('named_range') == None):
        print("Config missing 'input_table.named_range'.")
        exit(1)

    if (config.get('icons') == None):
        print("Config missing 'icons' section")
        exit(1)

    # init the ARENA library
    kwargs = {}
    if config['arena']['namespace']: kwargs["namespace"] = config['arena']['namespace']
    scene = Scene(
        host=config['arena']['host'],
        realm=config['arena']['realm'],
        scene=config['arena']['scenename'],
        **kwargs)

    # add and start tasks
    scene.run_once(make_walls(args))
    scene.run_tasks()
