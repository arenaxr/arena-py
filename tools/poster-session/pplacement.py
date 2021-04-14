from arena import *
from layout import Layout
from landmarks import Landmarks
from gstable import GoogleSheetTable
import argparse
import os
import math
import yaml
import time
import re

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

def parse_color(dict, key, default):
    '''Get a string with a color (as 'red, gree, blue') from a dictionary passed as argument
       Parse the string and return a (red, green, blue) tuple
    dict:
      the dictionary with the color string (as 'red, gree, blue')
    key:
      key where the color string is
    default:
      default color string value, if key does not exist

    Returns a (red, green, blue) tuple
    '''
    color_string = dict.get(key, default)
    return tuple(map(int, color_string.split(',')))

def make_wall(name_suffix, position, rotation, wall_data, config):
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

    return: the object id to be used for the landmark to this wall
    '''
    # default persit to False
    persist = config.get('persist', False)

    # get wall config
    wall_config         = config.get('wall', {})
    wall_width          = wall_config.get('width', 9)
    wall_height         = wall_config.get('height', 6)
    wall_depth          = wall_config.get('depth', 1)
    img_height          = wall_config.get('img_height', 2.6)
    wall_color          = parse_color(wall_config, 'color', '151, 171, 216')
    text_color          = parse_color(wall_config, 'text_color', '0, 66, 117')
    back_text_color     = parse_color(wall_config, 'back_text_color', '96, 122, 163')
    text_font           = wall_config.get('text_font', 'exo2bold')
    title_maxlen        = wall_config.get('title_maxlen', 150)

    # these will be the name of the objects in the scene
    root_name           = f'poster_root_{name_suffix}'
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

    # invisible root object; all other objects are children of this object
    root = Object(
        object_id=root_name,
        object_type='entity',
        persist=persist,
        position=position,
        rotation=rotation,
        material=Material(transparent=True)
    )
    scene.add_object(root)

    # back wall
    wall = Box(object_id=wall_name,
        parent=root_name,
        persist=persist,
        position=Position(0, 2.75, 0),
        width=wall_width,
        height=wall_height,
        depth=wall_depth,
        color=wall_color
    )
    scene.add_object(wall)

    try:
        # image on the wall
        img = Image(object_id=img_name,
            parent=root_name,
            persist=persist,
            position=Position(0, img_height, 0.510),
            scale=Scale(7.2,4.05,1),
            url=wall_data['image_url'] # raise exception if key does not exist
        )
        scene.add_object(img)
    except Exception as err:
        print(f'Could not add wall image: {err}')

    try:
        if len(wall_data['button1']) > 0:
            (bicon, btext, burl) = parse_button(wall_data['button1']) # raise exception if failed to parse

            iconpath = f'{config["icons"][bicon]}' # raise exception if key does not exist

            # button1
            videolink = Image(
                object_id=b1_name,
                parent=root_name,
                persist=persist,
                position=Position(4, img_height + .3, 0.510),
                scale=Scale(.5, .5, 1),
                url=iconpath,
                clickable=True,
                goto_url=GotoUrl(dest='popup', on='mousedown', url=burl)
            );
            scene.add_object(videolink)

            # button text
            lblb1 = Text(
                object_id=lbl_btn1,
                parent=b1_name,
                persist=persist,
                position=Position(0, -.35, 0),
                text=btext[0:10],
                color=(255, 255, 255),
                font=text_font,
                width=4
            )
            scene.add_object(lblb1)
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
                position=Position(4, img_height - .3, 0.510),
                scale=Scale(.5, .5, 1),
                url=iconpath,
                clickable=True,
                goto_url=GotoUrl(dest='popup', on='mousedown', url=burl)
            );
            scene.add_object(videolink)

            # button text
            lblb2 = Text(
                object_id=lbl_btn2,
                parent=b2_name,
                persist=persist,
                position=Position(0, -.35, 0),
                text=btext[0:10],
                color=(255, 255, 255),
                font=text_font,
                width=4
            )
            scene.add_object(lblb2)
    except Exception as err:
        print(f'Could not add button2: {err}')

    # title
    try:
        title_cut = f'{wall_data["title"][0:title_maxlen]}' # cut title; raise exception if key does not exist
        if len(wall_data["title"]) > title_maxlen: title_cut = title_cut + '...'

        lbltitle = Text(
            object_id=lbl_title_name,
            parent=root_name,
            persist=persist,
            position=Position(0, wall_height-.6, 0.510),
            text=title_cut,
            color=text_color,
            font=text_font,
            width=5
        )
        scene.add_object(lbltitle)

        # title, back
        lbltitleb = Text(
            object_id=lbl_back_title_name,
            parent=root_name,
            persist=persist,
            position=Position(0, wall_height/2, -0.55),
            rotation=Rotation(0, 180, 0),
            text=title_cut,
            color=back_text_color,
            font=text_font,
            width=8
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
            position=Position(0, wall_height-1.1, 0.510),
            text=f'{wall_data["authors"][0:100]}', # raise exception if key does not exist
            color=text_color,
            font=text_font,
            wrapCount=100,
            width=8
        )
        scene.add_object(lbl)
    except Exception as err:
        print(f'Could not add wall authors: {err}')

    # return the image name as the object the landmark should point to
    return img_name

def make_walls():
    # get data from google spreadsheet table
    print('Getting data...')
    gst = GoogleSheetTable();
    data = gst.aslist(config['input_table']['spreadsheetid'], config['input_table']['named_range'])

    # filter by scenename in config
    filtered = list(filter(lambda v: v['scene'] == config['arena']['scenename'], data))

    # get layout coordinates
    t = Layout(getattr(Layout, config[config['arena']['scenename']]['layout']), filtered).get_transforms(**(config[config['arena']['scenename']]['layout_args']))

    # create a lanmarks object; we will add a landmark for each wall
    landmarks = Landmarks();

    for i in range(len(filtered)):
        ldmrk_obj_id = make_wall(
            filtered[i]['id'], # use id as a suffix for the objects of each wall
            Position(t[i]['x'], t[i]['y'], t[i]['z']), # position as given by the layout
            Rotation(t[i]['rx'],t[i]['ry'],t[i]['rz']), # rotation as given by layout
            filtered[i],
            config,
        )
        lbl = f'{filtered[i]["title"][0:50]}' # cut title if too big and use a landmark label
        if len(filtered[i]["title"]) > 50: lbl = lbl + '...'
        landmarks.push_landmark(ldmrk_obj_id, lbl) # push landmark to the list

    # add landmark list to scene
    landmarks.add_object(config['arena']['scenename'])

    print('\nDone. Press Ctrl+C to disconnect.')

if __name__ == '__main__':
    global config

    # get args
    parser = argparse.ArgumentParser(description=(
        "Generate a poster session layout in a given scene"))
    parser.add_argument('-c', '--conf', dest='configfile', default=DFT_CONFIG_FILENAME, action='store', type=str,
            help=f'The configuration file. Default is {DFT_CONFIG_FILENAME}')
    parser.add_argument('-s', dest='scenename', default=None,
                        help='Scenename of the poster session (e.g. theme1, theme2)')
    args = parser.parse_args()

    # load config
    with open(args.configfile) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    # save scenename in config
    if args.scenename is not None:
        config['arena']['scenename'] = args.scenename

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
    scene = Scene(host=config['arena']['host'], realm=config['arena']['realm'], scene=config['arena']['scenename'])

    # add and start tasks
    scene.run_once(make_walls)
    scene.run_tasks()
