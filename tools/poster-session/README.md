# Programmatically Create a Poster Session Scene

This script creates poster walls using data from a google spreadsheet. For each line in the table (indicated by a range in the config file), it creates a poster wall. See the template [google spreadsheet template with instructions](https://docs.google.com/spreadsheets/d/1pRWUCnRwpr5cz_Tm2KFWvle_fVCwX5NVBopGcZcWLA0/edit?usp=sharing).

![image](https://user-images.githubusercontent.com/3504501/114779569-48d22280-9d44-11eb-80b6-bd1b341d195b.png)

The script operates on a scene at the time, but you can have data in the template spreadsheet for several scenes, and run the script once for each scene (indicated in the config file or passed through argument).

Run the script with:

```bash
make run
```

## Prerequisites

You need to have [Make](https://www.gnu.org/software/make/) installed. The Makefile creates a [virtual environment that deals with installing all dependencies](https://github.com/sio/Makefile.venv), including the **arena-py library** (from pyPI; it does not use the development version in this repo).

### Google Apps Script API
The script uses the google apps script API to get the spreadsheet data. Make sure to follow these google python library pre-requisites:						
1. A Google Cloud Platform project with the *Google Sheets API* enabled. See how to [create a project](https://developers.google.com/workspace/guides/create-project)
2. Authorization credentials for a desktop application (pasted into 'credentials.json'). See how to [create credentials](https://developers.google.com/workspace/guides/create-credentials).

More details [here](https://developers.google.com/apps-script/api/quickstart/python?hl=en).

## Arguments

The script accepts the following optional arguments:
```
  -h, --help            show this help message and exit
  -c CONFIGFILE, --conf CONFIGFILE
                        The configuration file. Default is ./config.yaml
  -s SCENENAME          Scenename of the poster session (e.g. theme1, theme2)
```

To pass arguments to the script, add the ARGS variable when invoking Make, e.g.:

```bash
make ARGS='-h'
make ARGS='--conf=myconfigfile.yaml'
```

## Config file

Most of the time, you will want to invoke the script with no arguments:

```bash
make run
```

And define options in the **config file** (`./config.yaml` by default). The config file looks like this:

```yaml
# persist objects (True/False)
# True: objects will be saved and appear in the scene after a reload
# False:objects will disappear after a reload (and only appear to clients already viewing the scene when they are created)
persist: False

# arena related definitions
arena:
  host: arenaxr.org # default: arenaxr.org
  realm: realm # default: realm
  scenename: ececapstone # one of the scenes defined below

# where is the input data: google spreadsheet id and cell range of the table
input_table:
  # The spreadsheetid can be found in the google spreadsheet url e.g.:
  # https://docs.google.com/spreadsheets/d/**spreadsheetid**/edit#gid=0
  #
  # For details, see: https://developers.google.com/sheets/api/guides/concepts
  spreadsheetid: 1jbFwUW_YWl6bAtsCJXcBDjPu1yojWso2uVY46dSGYW4
  # The table_named_range is the A1 or R1C1 range of the data table; Must
  # include the sheet name ('Data Table') and the header, e.g: Data Table!A1:F10
  #
  # For details, see: https://developers.google.com/sheets/api/guides/concepts
  named_range: Data Table!A1:G3

# where the icon files are
icons:
  video: /store/users/arena/poster-imgs/video.png
  catalog: /store/users/arena/poster-imgs/catalog.png
  pdf: /store/users/arena/poster-imgs/pdf.png
  link: /store/users/arena/poster-imgs/link.png

# wall settings (dimension, color, ...)
wall:
  width: 9 # width of the wall; default: 9
  height: 6 # height of the wall; default: 6
  depth: 1 # depth of the wall; default: 1
  img_height: 2.6 # heigh of the poster image; default: 2.6
  color: 151, 171, 216 # color of the wall; default: 151, 171, 216
  text_color: 0, 66, 117 # text color; default: 0, 66, 117
  back_text_color: 96, 122, 163 # back text color; default: 0, 66, 117
  text_font: 'exo2bold' # font
  title_maxlen: 150 # will add '...' after this amount of characters; default: 150

# ** Scene layout definitions (see below) **
ececapstone:
  layout: ROWCOL
  layout_args:
    row_dist: 20
    col_dist: 20
    row_off: 20
    col_off: -50
```
**Note**: The scenename command line argument overrides the config file scenename.

## Poster Wall Layouts for Each Scene

You can add a section in the config file to define how the posters are arranged in each scene. To do this, add a section (to `config.yaml`) with the scene name and define the layout parameters. For example, the section below will define a line arrangement for the poster walls of scene `test`:
```yaml
test:
  layout: LINE
  layout_args:
    length: 200 # length of the line (will try to layout the walls evenly spaced)
    rotation: 90 # rotation (degrees) of the walls
    alternating_rot: True # alternating rotation to make the walls face each other in pairs
```

The layouts supported and their options are shown below.

#### ROWCOL: arrange walls in rows and columns
##### Parameters:

- row_dist=30: distance between rows
- col_dist=30: distance between cols
- row_off=0: where rows start (offset from 0)
- col_off=0: where cols start (offset from 0)
- col_dir=1: direction of cols (1 or -1)
- row_dir=-1: direction of rows (1 or -1)
- col_axis='x': which axis is used as the col axis
- row_axis='z': which axis is used as the row axis
- fixed_axis='y': axis that defines the plane where the walls are laid out

#### CIRLE: arrange walls around a circle
##### Parameters:
- radius=50: radius of the circle (will try to layout the walls evenly spaced)
- a1_off=0: center of the circle offset from 0 in axis 1 (see axis1 param)
- a2_off=0: center of the circle offset from 0 in axis 2 (see axis2 param)
- axis1='x': which axis is used as axis1
- axis2='z': which axis is used as axis2
- fixed_axis='y': defines the plane where the walls are layed out

#### SQUARE: arrange walls in a square shape
##### Parameters:
- length=50: length of the square (will try to layout the walls evenly spaced)
- a1_off=0: offset of the corner of the square from 0 in axis 1 (see axis1 param)
- a2_off=0: offset of the corner of the square from 0 in axis 2 (see axis2 param)
- axis1='x': which axis is used as axis1
- axis2='z': which axis is used as axis2
- fixed_axis='y': defines the plane where the walls are layed out

#### LINE: arrange walls in a line
##### Parameters:
- length=200: length of the line (will try to layout the walls evenly spaced)
- rotation=90: rotation (degrees) of the wall
- alternating_rot=True: alternating rotation to make the walls face each other in pairs (True/False)
- a1_off=0: offset of the line start from 0 in axis 1 (see axis1 param)
- a2_off=0: offset of the line start from 0 in axis 2 (see axis2 param)
- axis1='x': which axis is used as axis1
- axis2='z': which axis is used as axis2
- fixed_axis='y': defines the plane where the walls are layed out

## Permissions

This tool will use the permissions of the ARENA user logged in. Can write to scenes the user has access to. If the user is not logged in, a login prompt (in a browser) will be presented.

To force sign out:
```
make signout
```
