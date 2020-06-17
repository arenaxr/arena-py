# ARENA Py - Python Examples
Draw objects in the ARENA using python.

Install required packages:
```
pip3 install -r requirements.txt
```
(on my linux box only had to run `sudo apt-get install python3-paho-mqtt`)

## Hello ARENA
```
cd examples
python hello.py
```
(view results at https://xr.andrew.cmu.edu?scene=hello) 

hello.py
```
import arena
arena.init("oz.andrew.cmu.edu", "realm", "hello")
arena.Object(arena.Shape.cube)
arena.handle_events()
```
## arena.py library
The above is the simplest example of an ARENA Python program. This library sits above the ARENA pub/sub MQTT
message protocol: JSON messages described in more detail at https://github.com/conix-center/ARENA-core which runs in a browser. That forms a layer, in turn, on top of [A-Frame](https://aframe.io/) and [THREE.js](http://threejs.org/) javascript libraries.

Here is a breakdown of the currently available arena.py functions
### init
The **init** function takes 3 string positional arguments, and 2 optional arguments in order:
 * the DNS name of a pub/sub MQTT broker (currently Mosquitto v1.6.3, which runs the v3.1.1 protocol)
 * realm, currently the fixed string "realm" to indicate hierarchy level
 * scene name, a string
 * **callback** - a callback function to be called when ARENA network events are received. The function is passed a string argument, the network message, a JSON encoded string. (See below for more callback information)
 * **port** - a numerical port to connect if MQTT is running on a nonstandard port e.g. 3003
These are composed together to form an MQTT topic, in the example, "realm/s/hello".  
A successful *init* results in a connection with the MQTT server, ready to send and receive messages.
### Object (create method)
`Object` takes multiple optional arguments and on success creates in the scene and returns a Python ARENA object.
Accepted arguments are:  
  * **objName** - Object name, a string. Object names should be unique within a scene
  * **objType** - an arena.objType enum from the set
    - *cube*
    - *sphere*
    - *circle*
    - *cone*
    - *cylinder*
    - *dodecahedron*
    - *icosahedron*
    - *tetrahedron*
    - *octahedron*
    - *plane*
    - *ring*
    - *torus*
    - *torusKnot*
    - *triangle*
    - *gltf-model* (see https://github.com/conix-center/ARENA-core#models for more details on GLTF format 3D models)
    - *line*
    - *thickline*
    - *text*
    - *image*
    - *particle*
    - *light*
  * **location** - a triple (x, y, z) coordinate in meters
  * **rotation** - a quad (x, y, z, w) rotation in quaternions
  * **scale** - a triple scaling factor in 3 dimensions
  * **color** - a triple RGB color where each component is in the range 0-255
  * **persist** - a boolean indicating whether to persist the created ARENA object to a database, such that it is visible when revisiting a scene. If `False`, the object will still be visible to everyone currently viewing the scene, but go away upon reload.
  * **ttl** - an integer for time to live, in seconds. objects will self-delete after this many seconds, and will not be persisted
  * **parent** - a string object name; sets this object to be one of possibly several children of the parent object with this objId
  * **physics** - an `arena.Physics` enum from
    - *none* - object remains fixed in place and does not interact with other physical objects
    - *static* - object remains fixed in place but DOES interact with other physical objects (collision, bounce off, etc.) Updates to the object's position can change it's location
    - *dynamic* - object roughly follows rough laws of gravity, and interacts with other physical objects. Updates to the object's position will not change it's location; it is under the control of physics engines, which are not consistent across multiple browsers viewing the scene
  * **clickable** - a boolean indicating whether the object has a `click-listener` component, allowing it to receive events from the `arena.Event` enum:
    - *mousedown*
    - *mouseup*
    - *mouseenter*
    - *mouseleave*
  * **url** - some objects use this parameter to refer to, e.g. a bitmap image, GLTF model, or web URL. See:
    - https://github.com/conix-center/ARENA-core#images
    - https://github.com/conix-center/ARENA-core#models
    - https://github.com/conix-center/ARENA-core#load-scene
  * **data** - accepts arbitrary JSON data to specify additional attribute-value pairs not specified above to be added to the object's A-Frame entity; see A-Frame and ARENA-core documentation for more detail. An example of a somewhat fancy data message would look like
```
    data='{"impulse": {"on": "mouseup","force":"0 40 0","position":"10 1 1"},"material": {"color":"(0, 255, 0)", "transparent": false, "opacity": 1}}'
```
(this example adds an impulse component which fires on mouseup event, with a force of 40 in the Y direction, and sets the object color to green, and sets the object to be non-transparent)
### Methods on Object
  * **fireEvent** takes 3 optional arguments
    - **event** - arena.Enum event to be sent to the object, e.g. *mouseup*, *mousedown* (default), *mouseenter*, *mouseleave*
    - **position** - a triple (x, y, z) where the event was fired in World coordinates (meters) default: (0, 0, 0)
    - **source** - an `objName` string indicating the object from which the event originated, default 'arenaLibrary'
  * **update** - takes multiple optional arguments to update values originally specified at object create time
    - **location**
    - **rotation**
    - **scale**
    - **color**
    - **physics**
    - **data**
    - **clickable**
  * **delete** - deletes the object from the scene
### updateRig
takes 3 positional arguments
  * **camera id** for example "camera_er1k_er1k" if visiting ARENA URL with &fixedCamera=er1k
  * **location** - a triple (x, y, z) coordinate in meters
  * **rotation** - a quad (x, y, z, w) rotation in quaternions
### handle_events
After synchronously drawing objects to the scene, it is necessary to start a loop to listen to and handle network events and call the callback function (specified at `init()` time) 
### flush_events
Empty out the buffer of sent/received network events; call this from main thread rather than sleep() or during loops.
### callback
The data passed to the ARENA callback function is a JSON string best interpreted with `json.loads()` which turns it into a dictionary. These messages are the full contents of all MQTT messages pertaining to the scene, as specified in https://github.com/conix-center/ARENA-core. Most of them may not be of interest, and should be filtered to just events, with code like:
```
def callback(msg)
    jsonMsg = json.loads(msg)
    # filter non-event messages
    if jsonMsg["action"] != "clientEvent":
        return

    # look for only mousedown messages
    if jsonMsg["type"] != "mousedown":
        return
        
    # handle mousedown message, breaking out message data from the dict, e.g
    # jsonMsg["object_id"], jsonMsg[
