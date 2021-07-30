# ARENA-Py
Draw objects and run programs in the ARENA using Python!

## Documentation
The ARENA Python library user guide and tutorials:
[ARENA Documentation: Python](https://arena.conix.io/content/python/).

## Setup
Install package using pip:
```shell
pip3 install arena-py
```

## Hello ARENA
Run the `hello.py` example:
```shell
cd examples
python hello.py
```

`hello.py`
```python
from arena import *

scene = Scene(host="arenaxr.org", scene="example")

@scene.run_once
def make_box():
    scene.add_object(Box())

scene.run_tasks()
```

## ARENA-py Library
The above is the simplest example of an ARENA Python program. This library sits above the ARENA pub/sub MQTT
message protocol: JSON messages described in more detail at https://github.com/conix-center/ARENA-core which runs in a browser.
That forms a layer, in turn, on top of [A-Frame](https://aframe.io/) and [THREE.js](http://threejs.org/) javascript libraries.

## Authentication
We have added protection to the ARENA MQTT broker to limit access to change your scenes, which requires Python programs to supply authentication through a Google account.

### Sign-In Desktop OS
If you have a web browser available, the ARENA-py library `Scene(host="myhost.com")` will launch a web browser the first time and ask you for an account to authenticate you with, before opening a client MQTT connection.

### Sign-In Server/Headless OS
For headless environments, the ARENA-py library `Scene(host="myhost.com")` will provide you with a url to cut and paste in a browser anywhere, ask you for an account to authenticate you with, and show you a code you can enter on the command line, before opening a client MQTT connection.

## Scripts
Some helper script aliases have been added in this library to help you manage authentication and quick command-line (CLI) publish and subscribe to the ARENA.

### Sign-Out
```bash
arena-py-signout
```
### Show Permissions
```bash
arena-py-permissions
```
### CLI Subscribe to Scene Messages
```bash
arena-py-sub -mh arenaxr.org -s example
```
### CLI Subscribe to Custom Topic
```bash
arena-py-sub -mh arenaxr.org -t realm/g/a
```
### CLI Publish a Scene Object Message
```bash
arena-py-pub -mh arenaxr.org -s example -m '{"object_id": "gltf-model_Earth", "action": "create", "type": "object", "data": {"object_type": "gltf-model", "position": {"x":0, "y": 0.1, "z": 0}, "url": "store/models/Earth.glb", "scale": {"x": 5, "y": 5, "z": 5}}}'
```
### CLI Help
```bash
arena-py-pub --help
arena-py-sub --help
```

## Changelog
Changelog can be found [here](https://github.com/conix-center/ARENA-py/tree/master/CHANGELOG.md).

## ARENA-py Repository Files
- [arena/](https://github.com/conix-center/ARENA-py/tree/master/arena/): The ARENA Python library.

- [examples/](https://github.com/conix-center/ARENA-py/tree/master/examples/): Canonical examples of ARENA functions from the [documentation](https://arena.conix.io/content/python/).
- [examples/objects](https://github.com/conix-center/ARENA-py/tree/master/examples/objects): Examples on how to create various ARENA-py objects.
- [examples/attributes](https://github.com/conix-center/ARENA-py/tree/master/examples/attributes): Examples on how to declare an add various ARENA-py object attributes.

- [examples/legacy/](https://github.com/conix-center/ARENA-py/tree/master/examples/legacy/): **Deprecated** demos for **ARENA-py < 0.1.0**.
- [examples/legacy/digital-twins/](https://github.com/conix-center/ARENA-py/tree/master/examples/legacy/digital-twins/): **Deprecated** demo of digital twins of physical spaces for **ARENA-py < 0.1.0**.

- [system-tests/](https://github.com/conix-center/ARENA-py/tree/master/system-tests/): Workouts and tests for ARENA-py.

- [tools/](https://github.com/conix-center/ARENA-py/tree/master/tools/): Reusable tools for any ARENA scene.
