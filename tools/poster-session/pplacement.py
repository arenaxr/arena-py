from arena import *
from layout import Layout
from gcwrapper import GoogleClientWrapper
import argparse
import os
import math
import yaml
import time
import re
import urllib
from arena.attributes.landmark import Landmark # manually import Landmark, while arena-py does not do it

DFT_CONFIG_FILENAME='./config.yaml'

DFT_LAYOUT={"layout": "ROWCOL", "layout_args": { "row_dist": 20, "col_dist": 20, "row_off": 20, "col_off": -50}}

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

def get_mapped_kv(dict, key, raise_exception=True):
    '''Checks if there is a key mapping for given key and returns value from dict dictionary
    '''
    mkey=config.get('key_mappings', {}).get(key, key)
    value = dict.get(mkey)
    if (value == None and raise_exception): raise KeyError(f'No {key}')
    return value

    '''

    if (value == None):
        mkey = config.get('key_mappings', {}).get(key);
        if (mkey):
            value = wall_data.get(mkey)
            if (value == None and raise_exception): raise KeyError(f'No {key} or {mkey}')
        else:
            if (raise_exception): raise KeyError(f'No {key} or {mkey}')
    return value
    '''

def make_wall(name_suffix, position, rotation, wall_data):
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

    # get wall config
    wall_config         = config.get('wall', {})
    wall_width          = wall_config.get('width', 7)
    wall_height         = wall_config.get('height', 7.5)
    wall_depth          = wall_config.get('depth', 1)
    img_pos_height      = wall_config.get('img_pos_height', 2.5)
    img_scale_width     = wall_config.get('img_scale_width', 3*1.15)  # posters are 3x4
    img_scale_height    = wall_config.get('img_scale_height', 4*1.15) # posters are 3x4
    wall_color          = parse_color(wall_config, 'color', '151, 171, 216')
    img_btn_color       = parse_color(wall_config, 'img_btn_color', '255, 255, 255')
    img_btn_text_color  = parse_color(wall_config, 'img_btn_text_color', '0, 0, 0')
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

    # init landmark title
    try:
        title_cut = get_mapped_kv(wall_data, 'title') # raise expection if no title
        if len(title_cut) > title_maxlen: title_cut = f'{title[0:title_maxlen]}...'
    except Exception as err:
        print(f'Could not get wall title: {err}')

    # invisible root object; all other objects are children of this object
    root = Object(
        object_id=root_name,
        object_type='entity',
        persist=persist,
        position=position,
        rotation=rotation,
        material=Material(transparent=True),
        landmark=Landmark(label=title_cut, offsetPosition="0 0 4")
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

    # title
    lbltitle = Text(
        object_id=lbl_title_name,
        parent=root_name,
        persist=persist,
        position=Position(0, wall_height-1.4, 0.510),
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

    try:
        # authors
        lbl = Text(
            object_id=lbl_authors_name,
            parent=root_name,
            persist=persist,
            position=Position(0, wall_height-2, 0.510),
            text=f'{get_mapped_kv(wall_data, "authors")[0:100]}', # raise exception if key does not exist
            color=text_color,
            font=text_font,
            wrapCount=100,
            width=8
        )
        scene.add_object(lbl)
    except Exception as err:
        print(f'Could not add wall authors: {err}')

    try:
        img_url=get_mapped_kv(wall_data,'image_url_1') # raise exception if key does not exist

        # image on the wall
        img = Image(object_id=img_name,
            parent=root_name,
            persist=persist,
            position=Position(0, img_pos_height, 0.510),
            scale=Scale(img_scale_width,img_scale_height,1),
            url=img_url
        )

        scene.add_object(img)
    except Exception as err:
        print(f'Could not add wall image: {err}')

    # get list of additional images
    img_btns = {}
    for img_key in ['image_url_1', 'image_url_2', 'image_url_3', 'image_url_4']:
        img = get_mapped_kv(wall_data, img_key, False)
        if img:
            btn_name = f'poster_imgbtn_{name_suffix}_{img_key}'
            img_btns[btn_name] = {'img_object_id': img_name, 'img_url': img}
            #btn_list.append({ 'btn_object_id': f'poster_imgbtn_{name_suffix}_{img_key}', 'img_object_id': img_name, 'img_url': img }) # remove non-existing columns or empty cells

    if len(img_btns) > 1:
        # add buttons to scroll between additional images
        for i in range(len(img_btns)):
            btn = img_btns[i]
            img_btn = Image(object_id=btn,
                parent=root_name,
                persist=persist,
                position=Position(-(wall_width/2)+.45, img_pos_height + (len(img_btns)-1) * .8 / 2 - i * .8, 0.510),
                heigh=.5,
                width=.5,
                scale=Scale(.5, .5, 1),
                color=img_btn_color
            )
            scene.add_object(img_btn)

            # button text
            lblbtn_img = Text(object_id=f'{btn}_text',
                parent=btn,
                persist=persist,
                position=Position(0, 0, 0),
                text=str(i+1),
                color=img_btn_text_color,
                font=text_font,
                width=10
            )
            scene.add_object(lblbtn_img)

    # get list of existing buttons (to know how many exist, up to 4)
    btn_list = []
    for btn_key in ['button1', 'button2', 'button3', 'button4']:
        btn_data = get_mapped_kv(wall_data, btn_key, False)
        if btn_data: btn_list.append(btn_data)

    # add buttons
    btn_start_height = img_pos_height + .8 * (len(btn_list) / 2)
    for i in range(len(btn_list)):
        try:
            (bicon, btext, burl) = parse_button(btn_list[i]) # raise exception if failed to parse
            iconpath = f'{config["icons"][bicon]}' # raise exception if key does not exist
            btn_name = f'poster_btn{i+1}_{name_suffix}'
            btnlbl_name = f'poster_btnlbl{i+1}_{name_suffix}'

            # button
            btn = Image(
                object_id=btn_name,
                parent=root_name,
                persist=persist,
                position=Position(img_scale_width/2 + (wall_width/2 - img_scale_width/2) /2, btn_start_height - .8 * i, 0.510),
                scale=Scale(.5, .5, 1),
                url=iconpath,
                clickable=True,
                goto_url=GotoUrl(dest='popup', on='mousedown', url=burl)
            );
            scene.add_object(btn)

            # button text
            lblbtn = Text(
                object_id=btnlbl_name,
                parent=btn_name,
                persist=persist,
                position=Position(0, -0.3, 0),
                text=btext[0:15],
                color=(255, 255, 255),
                font=text_font,
                width=3.5
            )
            scene.add_object(lblbtn)
        except Exception as err:
            print(f'Could not add button {btn_key}: {err}')

    print(f'Added {title_cut} ({name_suffix})')

    # return list of img buttons added to this wall
    return img_btns

def make_walls():
    # get data from google spreadsheet table
    print('Getting data...')

    data = {}
    json_url = config['input_table'].get('json_url')
    if (json_url):
        with urllib.request.urlopen(json_url) as url:
            response = url.read()
            data = json.loads(response)
    else:
        gcw = GoogleClientWrapper();
        data = gcw.gs_aslist(config['input_table']['spreadsheet']['spreadsheetid'], config['input_table']['spreadsheet']['named_range'])

    # filter by scenename in config
    scene_key = config.get('key_mappings', {}).get('scene', 'scene') # check if we have a mapping for scene
    filtered = list(filter(lambda v: v[scene_key] == config['arena']['scenename'], data))

    # get layout coordinates
    scene_params = config.get(config['arena']['scenename'], DFT_LAYOUT)
    t = Layout(getattr(Layout, scene_params['layout']), filtered).get_transforms(**(scene_params['layout_args']))

    btns = {}
    for i in range(len(filtered)):
        wall_btns = make_wall(
            filtered[i]['id'], # use id as a suffix for the objects of each wall
            Position(t[i]['x'], t[i]['y'], t[i]['z']), # position as given by the layout
            Rotation(t[i]['rx'],t[i]['ry'],t[i]['rz']), # rotation as given by layout
            filtered[i]
        )

        btns.update(wall_btns)

    # save buttons data on gdrive
    #gcw.gd_save_json(config['links_config']['fileid'], btns, f'{config["input_table"]["spreadsheetid"]}.json');
    print(f'Added {len(filtered)} posters.')
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

    if (config['input_table'].get('json_url') == None):
        if (config['input_table'].get('spreadsheet') == None):
            print("Config missing 'input_table.json_url' or 'input_table.spreadsheet'")
            exit(1)

        if (config['input_table']['spreadsheet'].get('spreadsheetid') == None):
            print("Config missing 'input_table.spreadsheetid'.")
            exit(1)

        if (config['input_table']['spreadsheet'].get('named_range') == None):
            print("Config missing 'input_table.named_range'.")
            exit(1)

    if (config.get('icons') == None):
        print("Config missing 'icons' section")
        exit(1)

    # init the ARENA library
    #scene = Scene(host=config['arena']['host'], realm=config['arena']['realm'], namespace=config['arena']['namespace'], scene=config['arena']['scenename'])
    scene = Scene(host=config['arena']['host'], realm=config['arena']['realm'], namespace=config['arena']['namespace'], scene='room1')
    # add and start tasks
    scene.run_once(make_walls)
    scene.run_tasks()
