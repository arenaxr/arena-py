from arena import *
from layout import Layout
from landmarks import Landmarks
from google_drive_downloader import GoogleDriveDownloader as gdd
import os
import math

theme='theme1'

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
    root_name           = f'{name_suffix}_root'
    wall_name           = f'{name_suffix}_wall'
    img_name            = f'{name_suffix}_img'
    light_name          = f'{name_suffix}_light'
    lbl_title_name      = f'{name_suffix}_lbltitle'
    lbl_authors_name    = f'{name_suffix}_lblauthors'
    lbl_back_name       = f'{name_suffix}_lblback'
    lbl_back_title_name = f'{name_suffix}_lblbacktitle'
    slides_lnk_name     = f'{name_suffix}_slideslink'
    video_lnk_name      = f'{name_suffix}_videolink'

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
    os.remove('comsenter-review-data.json')

    # download data file
    gdd.download_file_from_google_drive(file_id='1br58rf4OwvfqQAU3wooncg2kmmsx6QHd', dest_path='./comsenter-review-data.json', unzip=False)

    with open('./comsenter-review-data.json') as f:
        data = json.load(f)

    p_to_add = []
    for p in data:
        print(p)
        if p['theme'] == theme:
            p_to_add.append(p)

    t = Layout(Layout.ROWCOL, p_to_add).get_transforms(row_dist=20, col_dist=20, row_off=20, col_off=-50)
    #t = Layout(Layout.CIRCLE, p_to_add).get_transforms(radius=50)
    #t = Layout(Layout.SQUARE, p_to_add).get_transforms(length=100)
    #t = Layout(Layout.LINE, p_to_add).get_transforms(length=200)

    landmarks = Landmarks();
    for i in range(len(p_to_add)):
        make_wall(
            p_to_add[i]['lname'],
            Position(t[i]['x'],
            t[i]['y'], t[i]['z']),
            Rotation(t[i]['rx'],t[i]['ry'],t[i]['rz']),
            p_to_add[i]
        )
        lbl = f'{p_to_add[i]["lname"]}: {p_to_add[i]["title"]}'
        lbl_cut = f'{lbl[0:50]}...'
        landmarks.push_landmark(f'{p_to_add[i]["lname"]}_img', lbl_cut)

    landmarks.add_object(theme);

if __name__ == '__main__':

    # init the ARENA library
    scene = Scene(host='arenaxr.org', realm='realm', scene=theme)

    # add and start tasks
    scene.run_once(make_walls)
    scene.run_tasks()
