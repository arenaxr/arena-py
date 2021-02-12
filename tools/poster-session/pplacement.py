from arena import *
from layout import Layout
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
    text_font = 'exo2bold'

    # these will be the name of the objects in the scene
    root_name       = name_suffix + '_root'
    wall_name       = name_suffix + '_wall'
    img_name        = name_suffix + '_img'
    light_name      = name_suffix + '_light'
    lblTitle_name   = name_suffix + '_lbltitle'
    lblAuthors_name = name_suffix + '_lblauthors'
    slidesLnk_name  = name_suffix + '_slideslink'
    videoLnk_name   = name_suffix + '_videolink'

    # invisible root object; all other objects children of this object
    root = Object(
        object_id=root_name,
        object_type='entity',
        persist=persist,
        position=position,
        rotation=rotation,
        material=Material(transparent=True)
    )
    arena.add_object(root)

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
    arena.add_object(wall)

    # image on the wall
    img = Image(object_id=img_name,
        parent=root_name,
        persist=persist,
        position=Position(0, 2.2, 0.510),
        scale=Scale(7.2,4.05,1),
        url=wall_data['imgURL'] #'https://arena.andrew.cmu.edu/store/users/comsenter/images/template_hero_image.jpg'
    )
    arena.add_object(img)

    # button to video
    videolink = Image(
        object_id=videoLnk_name,
        parent=root_name,
        persist=persist,
        position=Position(4, 3, 0.510),
        scale=Scale(.5, .5, 1),
        url='https://arena.andrew.cmu.edu/store/users/comsenter/images/button-video.jpg',
        clickable=True,
        goto_url=GotoUrl(dest='popup', on='mousedown', url=wall_data['videoURL'])
    );
    arena.add_object(videolink)

    # button to presentation slides
    slideslink = Image(
        object_id=slidesLnk_name,
        parent=root_name,
        persist=persist,
        position=Position(4, 2, 0.510),
        scale=Scale(.5, .5, 1),
        url='https://arena.andrew.cmu.edu/store/users/comsenter/images/button-slides.jpg',
        clickable=True,
        goto_url=GotoUrl(dest='popup', on='mousedown', url=wall_data['presentationURL'])
    );
    arena.add_object(slideslink)

    # title
    lbltitle = Text(
        object_id=lblTitle_name,
        parent=root_name,
        persist=persist,
        position=Position(0, 5, 0.510),
        text=wall_data['title'],
        color=text_color,
        font=text_font,
        width=5
    )
    arena.add_object(lbltitle)

    # authors
    lbl = Text(
        object_id=lblAuthors_name,
        parent=root_name,
        persist=persist,
        position=Position(0, 4.5, 0.510),
        text=wall_data['fname'] + ' ' + wall_data['lname'],
        color=text_color,
        font=text_font,
        width=4
    )
    arena.add_object(lbl)
"""
    # a light for the wall
    plight = Light(
        object_id=light_name,
        parent=root_name,
        persist=persist,
        position=Position(0, 5, 3),
        rotation=Rotation(-30,0,0),
        type='spot',
        color='#ffffff',
        intensity=0.1
    )
    arena.add_object(plight)
"""

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

    #t = Layout(Layout.ROWCOL, p_to_add).get_transforms(row_dist=20, col_dist=20, row_off=20, col_off=-50)
    #t = Layout(Layout.CIRCLE, p_to_add).get_transforms(radius=50)
    #t = Layout(Layout.SQUARE, p_to_add).get_transforms(length=100)
    t = Layout(Layout.LINE, p_to_add).get_transforms(length=200)
    #print(t)

    for i in range(len(p_to_add)):
        make_wall(p_to_add[i]['lname'], Position(t[i]['x'], t[i]['y'], t[i]['z']), Rotation(t[i]['rx'],t[i]['ry'],t[i]['rz']), p_to_add[i])

if __name__ == '__main__':

    #print(get_positions(n=10, cols=3, row_dist=40, col_dist=40, row_off=-20, col_off=2))

    #exit()

    # init the ARENA library
    arena = Arena(host='arena.andrew.cmu.edu', realm='realm', scene=theme+'1')

    # add and start tasks
    arena.run_once(make_walls)
    arena.run_tasks()
