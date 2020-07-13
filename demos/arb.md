# ARENA AR Builder
An AR/VR capable editing tool to create/manipulate/delete ARENA objects. See top-level python documentation for [requirements](../README.md). This tool uses the [ARENA Persistence Database](https://github.com/conix-center/arena-persist), so all changes are persisted.

## Quick Start
Usage: `arb` takes at minimum one argument, the first one, a scene name (`hello` in this example).
```
python arb.py hello
```
(interact with the tool at https://xr.andrew.cmu.edu?scene=hello) 

## Control Panel
![AR Builder Panel](arb-panel.png)

- **VR Mode**: Click and hold your mouse to move your camera relative to the panel. 
- **AR Mode**: Move your AR device to move your camera relative to the panel.
- **All Modes**: Use the **lock** button to reposition the panel relative to your camera's rotation. *(in development)*

|Button|Type|Description|
|--|--|--|
|**color**|*action*|Allows color select; tap object to color it *(default=#ffffff)*.|
|**create**|*action*|Allows shape select; tap clipboard object to create it in place *(default=sphere)*.|
|**delete**|*action*|Tap object to delete it.|
|**lamp**|*toggle*|Turns a headlamp on/off.|
|**lock**|*toggle*|Off=panel maintains relative world position; On=panel follows camera rotation. *(in development)*|
|**model**|*action*|Allows GLTF model select; tap clipboard object to create it in place *(default=duck.glb)*. Models may be imported via the **-m** argument *(see below)*.|
|**move**|*action*|Tap an object to show it in the clipboard, tap clipboard object to move it to that place.|
|**nudge**|*action*|Allows mm, cm, dm, m granularity; tap an object to show yellow nudge-lines; tap a positive (red) or negative (blue) ball to nudge the object in that direction according to selected granularity *(default=mm)*. A yellow circle will also show x,z position on the floor (y=0). Nudge-lines expire after 30 seconds of inactivity.|
|**occlude**|*action*|Allows occlusion on/off select; tap object to occlude it *(default=on)*.|
|**parent**|*action*|Allows setting of parent object; first tap the parent object, then, then tap the child object.|
|**redpill**|*toggle*|Reveals useful debug data: ***gridlines*** on the floor (y=0) can be seen from above and below, ***occlusion mask*** will show all occluded objects, ***object data*** mouse hover on an object will shows its position, rotation, and scale.|
|**rename**|*action*|Allows typing a new name; start typing or just tap an object load the old name into the editor, then tap object to apply the new name.|
|**rotate**|*action*|Allows 1°, 5°, 10°, 45°, 90° Euler angle granularity; tap an object to show orange rotate-lines; tap a positive (red) or negative (blue) ball to change object rotation according to selected granularity *(default=1°)*. Additional 6Dof lines will show degree of rotation. Rotate-lines expire after 30 seconds of inactivity.|
|**scale**|*action*|Allows mm, cm, dm, m granularity; tap an object to show blue scale-lines; tap a positive (red) or negative (blue) ball to increase or decrease object scale according to selected granularity *(default=mm)*. Scale-lines expire after 30 seconds of inactivity.|
|**stretch**|*action*|Allows altering scale in one of 6Dof. *(in development)*|
|**wall**|*action*|Allows creation of a basic wall 0.1m thick; tap clipboard brick once with your AR device flush with one corner of the wall, and tap the second time at the opposing corner. Three alignment markers will appear for 2 minutes. *(in development)*|

## Clipboard

The clipboard is a temporary see-through object floating in front of the user used to show the relative position of placing a future object. It's also used in AR to have something to fire an event at where no object currently exists. 

## Construction Cone

There is a small temporary object resting on position 0,0,0 in the shape of a construction cone to mark the origin of the scene. It will be removed when `arb` stops running.

## Run Options

### Importing Models
You can import a json-formatted manifest of GLTF models using the command argument **-m** to use on the **model** control panel option. You can write your own, or use the example, [arb-manifest.json](arb-manifest.json).
```
python arb.py hello -m arb-manifest.json
```

### MQTT Host and Realm
By default all `arb` MQTT messages are published to the default message broker and topic (realm and scene you specify) using this scheme: 

- *default broker*: `oz.andrew.cmu.edu`
- *default topic*: `realm/s/hello`

To use your own MQTT message broker (**-b**) and/or realm (**-r**):

- *custom broker*: `arena-west1.conix.io`
- *custom topic*: `foo/s/hello`
```
python arb.py hello -b arena-west1.conix.io -r foo
```
