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
We are adding protection to the ARENA MQTT broker, eventually to host an ACL list to limit access to change your scenes.
As a first step, we are requiring Python programs to supply authentication through a Google account.

### Sign-In Desktop OS
If you have a web browser available, the ARENA library `Scene(host="myhost.com")` will launch a web browser the first time
and ask you for an account to authenticate you with, before opening a client MQTT connection.

### Sign-In Server/Headless OS
For headless environments, the ARENA library `Scene(host="myhost.com")` will provide you with a url to cut and paste in a
browser anywhere, ask you for an account to authenticate you with, and show you a code you can enter on the command line,
before opening a client MQTT connection.

### Sign-Out
```bash
arena-py-signout
```
### Show Permissions
```bash
arena-py-permissions
```

## Changelog
Changelog can be found [here](CHANGELOG.md).

## ARENA-py Repository Files
- [arena/](arena/): The ARENA Python library.

- [examples/](examples/): Canonical examples of ARENA functions from the [documentation](https://arena.conix.io/content/python/).
- [examples/objects](examples/objects): Examples on how to create various ARENA-py objects.
- [examples/attributes](examples/attributes): Examples on how to declare an add various ARENA-py object attributes.

- [examples/legacy/](examples/legacy/): **Deprecated** demos for **ARENA-py < 0.1.0**.
- [examples/legacy/digital-twins/](examples/legacy/digital-twins/): **Deprecated** demo of digital twins of physical spaces for **ARENA-py < 0.1.0**.

- [system-tests/](system-tests/): Workouts and tests for ARENA-py.

- [tools/](tools/): Reusable tools for any ARENA scene.
