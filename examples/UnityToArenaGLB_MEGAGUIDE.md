# arena-py NPC Readme
<img src="https://img.shields.io/badge/language-Python>=3.10-blue"/> <img src="https://img.shields.io/badge/platform-arenaxr.org-green"/> <img src="https://img.shields.io/badge/license-BSD 3 License-red"/> 

This demo repository contains scripts, tools, and examples for adding animated, interactive NPCs (Non-Player Characters) into ARENA scenes. NPC avatars can be linked to play iterating text speech like in an interactive visual novel, complete with triggers for animations, blendshapes, sound effects, image/videos, point-to-point movement and more.

<img src="Documentation/NPC_Splash.gif" width="800"> 
*A quick demo of a human operator interacting with a robot NPC avatar learning about the ARENA platform in mixed reality.*

NPCs utilize conversational dialogue trees parsed from JSON files that can be easily created with *YarnClassic*, a visual node-based editor for crafting dialogue trees. 

- YarnClassic's official repository on Github (MIT license):
https://github.com/blurymind/YarnClassic
- Download the YarnClassic editor for your platform here: (supports Mac/Windows/Linux)
https://github.com/blurymind/YarnClassic/releases
- Alternatively, you can use the web app here to create dialogue files:
https://blurymind.github.io/YarnClassic/

## Setup
Install package using pip ([https://pypi.org/project/arena-py/](https://pypi.org/project/arena-py/)):
```shell
pip3 install arena-py
pip3 install colorama
```

## How to run an NPC
Run the terminal command:

```shell
py NPC.py [FOLDER NAME]

```
Replace [FOLDER NAME] with the name/path of the folder that contains the config, dialogue, and mappings JSON files for the NPC you want to run. Note that this folder MUST have one of each file, named exactly config.json, dialogue.json, and mappings.json.


## NPC "Brain" Config JSON files
 
Each NPC "brain" is stored in a folder with three files, with the following names:
- **config.json**: contains all the configuration options for the NPC, with settings for the scene, start position, names, colors and more.
- **dialogue.json**: contains a dialogue tree file, which all conversational pathways and actions this NPC can take.
- **mappings.json**: contains all the trigger action command mappings for this NPC, which define transforms, animations, videos and more.

## NPC config.json file
The `config.json` file contains all basic settings for the NPC you want to run. Here is a full list of what each configuration option does:

### ARENA
These are connection settings that specify which server, account and room the NPC should live and run in.

|SETTING|DESCRIPTION|SYNTAX|
|-|-|-|
|HOST|Which ARENA server we want to connect to. Should be "arenaxr.org" for most users.|STRING|
|NAMESPACE|What user's domain we want to connect to. If scene is on user [USERNAME]'s account, change to [USERNAME]. Default is "public" for publically hosted scenes.|STRING|
|SCENE|Which scene we want to connect to within the specified domain namespace. Default is "arena". |STRING|

### NODE
This specifies which dialogue nodes the NPC should start and end at. There must be matching node names in `dialogue.json`.

|SETTING|DESCRIPTION|SYNTAX|
|-|-|-|
|ENTER| Defines which node we start at in 'dialogue.json' file. Enter node name must match node name in 'dialogue.json'. |STRING|
|EXIT| Defines which node to go to if out of bounds of 'dialogue.json' file. Exit node name must match node name in 'dialogue.json'. NPC dialogue will jump to this node when out of range. *(Note: range-based dialogue exit not implemented.)* |STRING|

### NPC
This defines basic visual settings of the NPC, in particular, the NPC's name, the NPC's 3D model, and the NPC's 2D icon.

|SETTING|DESCRIPTION|SYNTAX|
|-|-|-|
|NAME|Defines the name of the NPC. This is a prefix that is appended to all objects under this NPC to make it more easily searchable in the ArenaXR web editor. For example, if `NAME` is set to "MyNPC", all of its child objects will be prefixed with "MyNPC_".|STRING|
|GLTF_URL|This is a URL to a 3D GLTF/GLB model in the ARENA filestore to represent the NPC. The model should have blendshapes and animations preconfigured to match the animation/blendshape names in `mappings.json` for more expressive behaviours.|STRING|
|ICON_URL|This is a URL to a 2D image icon in the ARENA filestore to represent the NPC in its chat bubble. While not required, it is recommended to have an image with a square aspect ratio.|STRING|
  
### USE_DEFAULTS
The NPC will automatically play default animations, blendshape morphs, and sounds for initializing, interacting, talking, idling, moving and blinking without requiring designated commands in every node in `dialogue.json` if these settings are enabled and the defaults are configured correctly in `mappings.json`.

|SETTING|DESCRIPTION|SYNTAX|
|-|-|-|
|ANIMATIONS|If the model has default animations specified in `mappings.json`, set this to true, and false otherwise.|BOOLEAN|
|MORPHS|If the model has default blendshape morphs specified in `mappings.json`, set this to true, and false otherwise.|BOOLEAN|
|SOUNDS|If the model has default sound effects specified in `mappings.json`, set this to true, and false otherwise.|BOOLEAN|

### TIMERS
The NPC will check the status of various timers at specified intervals before triggering resets, transforms, and speech. Note that we do not check the status of these timers every frame, as we do not want to spam/overload ArenaXR's servers with redundant messages.

|SETTING|DESCRIPTION|SYNTAX|
|-|-|-|
|RESET| `INTERVAL` Number of milliseconds to elapse before checking this timer again. <br/> `TIME` Number of milliseconds with no activity to elapse before resetting this NPC. <br/> |{"INTERVAL": INT, "TIME": INT}|
|TRANSFORM| `INTERVAL` Number of milliseconds to elapse before checking this timer again. <br/> `TIMER` The amount of time it takes to complete a transform command. <br/> |{"INTERVAL": INT, "TIMER": INT}|
|SPEECH| `INTERVAL` Number of milliseconds to elapse before checking this timer again. <br/> `SPEED` The rate at which the NPC "speaks" by incrementally filling in chat text. <br/> |{"INTERVAL": INT, "SPEED": INT}|

### UI
These are quick visual appearance settings for the NPC's speech and choice bubbles, which use [ArenaXR's Card UI templates.](https://docs.arenaxr.org/content/python-api/objects/arenaui_card.html)

|SETTING|DESCRIPTION|SYNTAX|
|-|-|-|
|USE_NAME_AS_TITLE|Sets the NPC's speech bubble label as [NPC_NAME] if set to true, and removes speech bubble label if false.|BOOLEAN|
|THEME|Set to "light" for light mode, and "dark" for dark mode.|STRING|
|VERTICAL_BUTTONS|Sets user dialogue response choice bubbles vertically if true, and horizontally if false.|BOOLEAN|
|FONT_SIZE|Sets the master font size of the NPC's speech and choice bubbles.|FLOAT|
|TEXT_WIDTH|Sets the width of the text section of the NPC's speech bubble.|FLOAT|
|ICON_WIDTH|Sets the width of the image icon section of the NPC's speech bubble.|FLOAT|
|ICON_FILL|Sets the image icon's fill type of the NPC's speech bubble. Is either "cover", "contain", or "stretch". |STRING|

### ROOT
The ROOT node is an invisible parent cube object that all NPC objects are children of. Move/rotate/scale the root, and all children NPC objects will follow accordingly.

|SETTING|DESCRIPTION|SYNTAX|
|-|-|-|
|PARENT|Set [PARENT] to another object's name if you want the NPC's ROOT cube object to follow another object. Set this to "" if otherwise.|STRING|
|SCALE|Sets the scale of NPC root cube object. By default, this should be {"x": 1,"y": 1,"z": 1}. *Note: It is highly recommended to keep all dimensions uniform to prevent weird scaling bugs.*|{"x": FLOAT,"y": FLOAT,"z": FLOAT}|
|SIZE|This is the default width/height/depth dimension of the NPC ROOT debugging cube. Default is 0.2.|FLOAT|
|POSITION|This is the default starting position of the NPC character. If you do not want the NPC to "hug" the center of the scene (making it hard to calibrate for AR), move this to something other than {"x": 0,"y": 0,"z": 0}.|{"x": FLOAT,"y": FLOAT,"z": FLOAT}|
|ROTATION|This is the starting rotation of the NPC character, which is by default at a zero rotation: {"x": 0,"y": 0,"z": 0}.|{"x": FLOAT,"y": FLOAT,"z": FLOAT}|
|COLOR|This is the color of the invisible NPC ROOT cube. Used for debugging purposes only. Each value goes from 0-255. Default {"r": 0, "g": 255, "b": 0}.|{"r": INT, "g": INT, "b": INT}|
|OPACITY|This is opacity of the NPC ROOT cube, ranging from 0-1. Used for debugging purposes only. Set it to 0 to hide the cube. Set it to 1 to fully show it. Set it to 0.5 to make it half transparent.|FLOAT|

### GLTF
This sets the position, rotation and scale offsets of the GLTF/GLB 3D object representation of the NPC. *Note: Not to be confused with the NPC ROOT position, rotation, and scale. Change ROOT if you want to "move/rotate/scale" the NPC. Change GLTF if you want to merely add offsets to the 3D model.*

|SETTING|DESCRIPTION|SYNTAX|
|-|-|-|
|SCALE|This is the scale offset of the GLTF/GLB model, relative to the NPC ROOT cube object. By default, this should be {"x": 1,"y": 1,"z": 1}. |{"x": FLOAT,"y": FLOAT,"z": FLOAT}|
|POSITION|This is the position offset of the GLTF/GLB model, relative to the NPC ROOT cube object. By default, this should be {"x": 0,"y": 0,"z": 0}. |{"x": FLOAT,"y": FLOAT,"z": FLOAT}|
|ROTATION|This is the rotation offset of the GLTF/GLB model, relative to the NPC ROOT cube object. By default, this should be {"x": 0,"y": 0,"z": 0}. |{"x": FLOAT,"y": FLOAT,"z": FLOAT}|

### PLANE
|SETTING|DESCRIPTION|SYNTAX|
|-|-|-|
|SIZE|Description...|FLOAT|
|SIZE_DURATION|Description...|STRING|
|POSITION|Description...|{"x": FLOAT,"y": FLOAT,"z": FLOAT}|
|ROTATION|Description...|{"x": FLOAT,"y": FLOAT,"z": FLOAT}|
|OPACITY|Description...|FLOAT|

### SPEECH
|SETTING|DESCRIPTION|SYNTAX|
|-|-|-|
|TEXT| `COLOR` Color of the text. <br> `POSITION` <br> `SCALE` <br> | {"r": INT, "g": INT, "b": INT} <br> {"x": FLOAT,"y": FLOAT,"z": FLOAT} <br> {"x": FLOAT,"y": FLOAT,"z": FLOAT} <br> |
|BUBBLE | `POSITION` <br> `ROTATION` <br> `SCALE` <br> | {"x": FLOAT,"y": FLOAT,"z": FLOAT} <br> {"x": FLOAT,"y": FLOAT,"z": FLOAT} <br> {"x": FLOAT,"y": FLOAT,"z": FLOAT} <br> |

### CHOICE
|SETTING|DESCRIPTION|SYNTAX|
|-|-|-|
|TEXT| `COLOR` <br> `SCALE` <br> | {"r": INT, "g": INT, "b": INT} <br> {"x": FLOAT,"y": FLOAT,"z": FLOAT} <br> |
|BUBBLE | `COLOR` <br> `OPACITY` <br> `POSITION` <br> `ROTATION` <br> `OFFSET_Y` <br> `SCALE` <br> |  {"r": INT, "g": INT, "b": INT} <br> FLOAT <br> {"x": FLOAT,"y": FLOAT,"z": FLOAT} <br> {"x": FLOAT,"y": FLOAT,"z": FLOAT} <br> FLOAT <br> {"x": FLOAT,"y": FLOAT,"z": FLOAT} <br> |

### LINK
|SETTING|DESCRIPTION|SYNTAX|
|-|-|-|
|TEXT| `COLOR` <br> `SCALE` <br> | {"r": INT, "g": INT, "b": INT} <br> {"x": FLOAT,"y": FLOAT,"z": FLOAT} <br> {"x": FLOAT,"y": FLOAT,"z": FLOAT} <br> |
|BUBBLE | `POSITION` <br> `ROTATION` <br> `SCALE` <br> | {"x": FLOAT,"y": FLOAT,"z": FLOAT} <br> {"x": FLOAT,"y": FLOAT,"z": FLOAT} <br> {"x": FLOAT,"y": FLOAT,"z": FLOAT} <br> |


## NPC mappings.json file
The mappings.json file contains a list of trigger action mappings that the dialogue.json file references.

The majority of these mappings are full path names and more detailed 


### DEFAULTS

#### SOUND
#### ANIMATION
#### MORPH
#### MISCELLANEOUS
VIDEO FRAME OBJECT

### MAPPINGS

#### SOUND_MAPPINGS
#### ANIMATION_MAPPINGS
#### TRANSFORM_MAPPINGS
#### MORPH_MAPPINGS
#### URL_MAPPINGS
#### IMAGE_MAPPINGS
#### VIDEO_MAPPINGS


## NPC dialogue.json file
Here is an example `dialogue.json` file in the ArenaRobot folder, which creates dialogue for a cute robot character that talks about Wiselab and the ARENA, and shows off the basic example capabilities of NPC avatars. 
<img src="Documentation/ArenaRobotDialogue.png" width="800"> 
*Note: coloring Node headers is optional, and is only useful for organizing `dialogue.json` in the Yarn editor.*

- **Orange section:** Enter/Exit nodes are clearly labeled. Shows off basic line-by-line conversational speech by talking about itself, ARENA, and the Wiselab.
- **Blue section:** A list of older videos showcasing the capabilities of the ARENA platform. When any node here is selected, it will play a video on a plane next to the robot like a PowerPoint presentation.
- **Green section:** A list of transform destinations towards various points of interest around the ARENA main public demo scene. Each transform contains a position and a rotation for the NPC robot avatar to move and rotate to.
- **Black section:** This is largely a repetition of the Orange section, but allows the NPC to loop its conversation to the other sections.

### NPC Yarn Dialogue Format/Syntax
Here is a closer view of the nodes and color highlights:
<img src="Documentation/Nodes.png" width="800"> 
- **Line:** To create a line of NPC speech, write regular text. New lines represent different blocks of speech text, where NPC characters will sequentially speak every block of speech text, line by line, and the user will have to click "Next" to advance the conversation. 

- **Choice:** Add the end of the speech, add user selection Choices with `[[]]`, with the name of the new Node to jump to if the node choice is selected. If you want the Choice bubble to display different text than the name of the Node, then add `|` in between the `[[]]`, with the desired bubble text on the left and the title of the Node to jump to on the right (For example, `[[Go to this node|Node123]]` will show the user "Go to this node" as the selection option and will jump to the Node with name "Node123" if selected). Node Choices are highlighted in blue in the Yarn editor. If a node is connected to another node with a Choice, it will be shown with a directional arrow in the Yarn editor. Be sure to add all user selection choices within the same line.

- **Command:** Add trigger action commands with `<<>>`, on the same line as the speech where you want the trigger action to be activated. You can add multiple trigger action commands on the same line. See trigger action syntax and usage in the "Triggers and Actions" section below. Note: most trigger actions must have corresponding mappings preset in `mappings.json` to be activated; trigger action commands with missing mappings will be ignored. Node trigger actions are highlights in pink in the Yarn editor.


###Trigger Action Commands
Here is a layout list of all example triggers in same the `dialogue.json` file in the ArenaRobot folder. 
<img src="Documentation/Triggers.png" width="800">
*Note: These nodes shown above are not reachable in the ArenaRobot `dialogue.json` without changing the `NODE ENTER` name in the config.json file in same folder.*


Here is a list of all the possible Trigger Action Commands. Custom trigger action commands can be added by manually editing `ArenaDialogueBubbleGroup.py`, `mappings.py`, and `mapping.json`.

|Trigger Type|Description|Syntax|
|-|-|-|
|Sound|Plays the sound property mapped to [SOUND MAPPING] in `mappings.json`.|`<<sound [SOUND MAPPING]>>`|
|Morph|Plays the blendshape morph property mapped to [MORPH MAPPING] in `mappings.json`.|`<<morph [MORPH MAPPING]>>`|
|Animation|Plays the animation mixer property mapped to [ANIMATION MAPPING] in `mappings.json`.|`<<animation [ANIMATION MAPPING]>>`|
|Transform|Plays the transform property mapped to [TRANSFORM MAPPING] in `mappings.json`. Note that this can contain any combination of position, rotation and scale.|`<<transform [TRANSFORM MAPPING]>>`|
|URL|Displays a clickable web URL link defined in [URL MAPPING] in `mappings.json`.|`<<url [URL MAPPING]>>`|
|Image|Displays an image on floating billboard plane defined in [IMAGE MAPPING] in `mappings.json`.|`<<image [IMAGE MAPPING]>>`|
|Video|Displays a video on floating billboard plane defined in [VIDEO MAPPING] in `mappings.json`.|`<<video [VIDEO MAPPING]>>`|
|Print|Debugging function that logs a console message [TEXT STRING].|`<<print ("[TEXT STRING]")>>`|
|Show|Sets the visibility of an object with the name [OBJECT ID] to true.|`<<show [OBJECT ID]>>`|
|Hide|Sets the visibility of an object with the name [OBJECT ID] to false.|`<<hide [OBJECT ID]>>`|
