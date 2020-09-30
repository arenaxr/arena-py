# ARENA Py - Python Examples
Draw objects in the ARENA using Python.

## Documentation
The ARENA Python library user guide and tutorials: [ARENA Documentation: Python](https://conix-center.github.io/ARENA/content/python/).

## Setup
Install package using pip:
```shell
pip3 install arena-py
```

## Hello ARENA
1. View the ARENA at [https://arena.andrew.cmu.edu?scene=hello](https://arena.andrew.cmu.edu?scene=hello)
1. Run the `hello.py` example:
```shell
cd examples
python hello.py
```

`hello.py`
```python
import arena
arena.init("arena.andrew.cmu.edu", "realm", "hello")
arena.Object(arena.Shape.cube)
arena.handle_events()
```

## arena.py Library
The above is the simplest example of an ARENA Python program. This library sits above the ARENA pub/sub MQTT
message protocol: JSON messages described in more detail at https://github.com/conix-center/ARENA-core which runs in a browser. That forms a layer, in turn, on top of [A-Frame](https://aframe.io/) and [THREE.js](http://threejs.org/) javascript libraries.

## ARENA-py Repository Files
- [arena/](arena/): The ARENA Python library
- [demos/](demos/): Demos of cool ARENA applications
- [demos/raw-prototypes/](demos/raw-prototypes/): Older ARENA non-library demos
- [digital-twins/](digital-twins/): Digital twins of physical spaces
- [examples/](examples/): Canonical examples of ARENA functions from the [documentation](https://conix-center.github.io/ARENA/content/python/))
- [system-tests/](system-tests/): Workouts for the ARENA 
- [tools/](tools/): Reusable tools for any ARENA scene
