from arena import *
from layout import Layout
from landmarks import Landmarks
from google_drive_downloader import GoogleDriveDownloader as gdd
import argparse
import os
import math
import yaml

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
    '''
    # some defaults
    persist=True # False=objects will disappear after a reload (and only appear to clients already viewing the scene when they are created)
    wall_color = Color(151, 171, 216) # color of the wall
    text_color = Color(0, 66, 117)
    back_text_color = Color(96, 122, 163)
    text_font = 'exo2bold'

    # these will be the name of the objects in the scene
    root_name           = f'poster_root_{name_suffix}'
    wall_name           = f'poster_wall_{name_suffix}'
    img_name            = f'poster_img_{name_suffix}'
    light_name          = f'poster_light_{name_suffix}'
    lbl_title_name      = f'poster_lbltitle_{name_suffix}'
    lbl_authors_name    = f'poster_lblauthors_{name_suffix}'
    lbl_back_name       = f'poster_lblback_{name_suffix}'
    lbl_back_title_name = f'poster_lblbacktitle_{name_suffix}'
    slides_lnk_name     = f'poster_slideslink_{name_suffix}'
    video_lnk_name      = f'poster_videolink_{name_suffix}'

    # invisible root object; all other objects children of this object
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
        width=9,
        height=5.5,
        depth=1,
        color=wall_color
    )
    scene.add_object(wall)

    # image on the wall
    img = Image(object_id=img_name,
        parent=root_name,
        persist=persist,
        position=Position(0, 2.2, 0.510),
        scale=Scale(7.2,4.05,1),
        url=wall_data['imgURL']
    )
    scene.add_object(img)

    # button to video
    videolink = Image(
        object_id=video_lnk_name,
        parent=root_name,
        persist=persist,
        position=Position(4, 3, 0.510),
        scale=Scale(.5, .5, 1),
        url='https://arenaxr.org/store/users/comsenter/images/button-video.jpg',
        clickable=True,
        goto_url=GotoUrl(dest='popup', on='mousedown', url=wall_data['videoURL'])
    );
    scene.add_object(videolink)

    # button to presentation slides
    slideslink = Image(
        object_id=slides_lnk_name,
        parent=root_name,
        persist=persist,
        position=Position(4, 2, 0.510),
        scale=Scale(.5, .5, 1),
        url='https://arenaxr.org/store/users/comsenter/images/button-slides.jpg',
        clickable=True,
        goto_url=GotoUrl(dest='popup', on='mousedown', url=wall_data['presentationURL'])
    );
    scene.add_object(slideslink)

    # title
    lbltitle = Text(
        object_id=lbl_title_name,
        parent=root_name,
        persist=persist,
        position=Position(0, 5, 0.510),
        text=wall_data['title'],
        color=text_color,
        font=text_font,
        width=5
    )
    scene.add_object(lbltitle)

    # authors
    lbl = Text(
        object_id=lbl_authors_name,
        parent=root_name,
        persist=persist,
        position=Position(0, 4.5, 0.510),
        text=f'{wall_data["fname"]} {wall_data["lname"]}',
        color=text_color,
        font=text_font,
        width=4
    )
    scene.add_object(lbl)

    # title, back
    lbltitleb = Text(
        object_id=lbl_back_title_name,
        parent=root_name,
        persist=persist,
        position=Position(0, 3, -0.55),
        rotation=Rotation(0, 180, 0),
        text=wall_data['title'],
        color=back_text_color,
        font=text_font,
        width=8
    )
    scene.add_object(lbltitleb)

def make_walls():
    # remove old file
    try:
        os.remove(config['datafile']['local_filename'])
    except:
        print("No previous data file.")

    # download data file
    print('Downloading data file...')
    gdd.download_file_from_google_drive(file_id=config['datafile']['gdriveid'], dest_path=f'./{config["datafile"]["local_filename"]}', unzip=False)
    print('Done.')

    with open(f'./{config["datafile"]["local_filename"]}') as f:
        data = json.load(f)

    p_to_add = []
    for p in data:
        if p['theme'] == config['arena']['scenename']:
            p_to_add.append(p)

    # get layout coordinates
    t = Layout(getattr(Layout, config[config['arena']['scenename']]['layout']), p_to_add).get_transforms(**(config[config['arena']['scenename']]['layout_args']))
    print(t)
    landmarks = Landmarks();
    for i in range(len(p_to_add)):
        psuffix=f'{i}_{p_to_add[i]["lname"]}'
        make_wall(
            psuffix,
            Position(t[i]['x'],
            t[i]['y'], t[i]['z']),
            Rotation(t[i]['rx'],t[i]['ry'],t[i]['rz']),
            p_to_add[i]
        )
        lbl = f'{p_to_add[i]["lname"]}: {p_to_add[i]["title"]}'
        lbl_cut = f'{lbl[0:50]}...'
        landmarks.push_landmark(f'poster_img_{psuffix}', lbl_cut)

    landmarks.add_object(config['arena']['scenename']);

if __name__ == '__main__':
    global config

    # load config
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    # get scenename
    parser = argparse.ArgumentParser(description=(
        "Generate a poster session layout in a given scene"))
    parser.add_argument('-s', dest='scenename', default=None,
                        help='Scenename of the poster session (e.g. theme1, theme2)')
    args = parser.parse_args()
    # save scenename in config
    if args.scenename is not None:
        config['arena']['scenename'] = args.scenename

    # init the ARENA library
    arena = Scene(host=config['arena']['host'], realm=config['arena']['realm'], scene=config['arena']['scenename'])

    # add and start tasks
    scene.run_once(make_walls)
    scene.run_tasks()
