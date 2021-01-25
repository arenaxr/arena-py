# ARENA-Py
Draw objects and run programs in the ARENA using Python!

## Documentation
The ARENA Python library user guide and tutorials: [ARENA Documentation: Python](https://conix-center.github.io/ARENA/content/python/). For version 0.1.0, see [docs](./docs).

## Setup
Install package using pip:
```shell
pip3 install arena-py
```

## Hello ARENA
1. Run the `hello.py` example:
```shell
cd examples
python hello.py
```

`hello.py`
```python
from arena import *

arena = Arena(host="arena.andrew.cmu.edu", realm="realm", scene="example")

@arena.run_once
def make_box():
    arena.add_object(Box())

arena.run_tasks()
```

## ARENA-py Library
The above is the simplest example of an ARENA Python program. This library sits above the ARENA pub/sub MQTT
message protocol: JSON messages described in more detail at https://github.com/conix-center/ARENA-core which runs in a browser.
That forms a layer, in turn, on top of [A-Frame](https://aframe.io/) and [THREE.js](http://threejs.org/) javascript libraries.

## Authentication
We are adding protection to the ARENA MQTT broker, eventually to host an ACL list to limit access to change your scenes. As a first step, we are requiring Python programs to supply authentication through a Google account.
### Sign-In Desktop OS
If you have a web browser available, the ARENA library `Arena(host="myhost.com")` will launch a web browser the first time and ask you for an account to authenticate you with, before opening a client MQTT connection.
### Sign-In Server/Headless OS
For headless environments, the ARENA library `Arena(host="myhost.com")` will provide you with a url to cut and paste in a browser anywhere, ask you for an account to authenticate you with, and show you a code you can enter on the command line, before opening a client MQTT connection.
### Sign-Out
```bash
python3 -c "from arena import auth; auth.signout()"
```
### Show Permissions
```bash
python3 -c "from arena import auth; auth.permissions()"
```

## ARENA-py Repository Files
- [arena/](arena/): The ARENA Python library
- [examples/](examples/): Canonical examples of ARENA functions from the [documentation](https://conix-center.github.io/ARENA/content/python/)
- [examples/legacy/](examples/legacy/): Deprecated demos for ARENA-py < 0.1.0
- [examples/legacy/digital-twins/](examples/legacy/digital-twins/): Digital twins of physical spaces for ARENA-py < 0.1.0
- [system-tests/](system-tests/): Workouts for the ARENA
- [tools/](tools/): Reusable tools for any ARENA scene
