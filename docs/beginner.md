# Beginner Example - The bare minimum you need to start using ARENA-py

## Let's start by installing and importing the library
```shell
pip3 install arena-py
```

Ok, now let's get started!

### Setup environmental variables (reccomended but not required)
Replace [host], [realm], and [scene] with your desired mqtt broker, realm, and scene name, respectively.
```shell
export MQTTH=[host]
export REALM=[realm]
export SCENE=[scene]
```

## Import the library
```python
from arena import *
```

## Start the client
```python
arena = Scene()
```
You can also pass host, realm, and scene as arguments, if you don't want to use enviornmental variables. These *must* be keyword arguments:
```python
scene = Scene(host=[host], realm=[realm], scene=[scene])
```
Note: ARENA-py will always favor environmental variables over arguments.

## Define a task
ARENA-py works by running tasks in an event loop, so we need a main task for our sample program.
```python
def main():
```

## Our first object
Inside main(), lets make a box!
```python
box = Box(object_id="my_box", position=Position(0,4,-2), scale=Scale(2,2,2))
```
Note the input arguments. The names must match what they will be in the ARENA JSON specification. We don't have to worry too much about that now, but keep this in mind, as typos will be very bad!

Box is a type of "Object". See [objects](https://arena.conix.io/content/python/objects.html).

Position and Scale are what we call "Attributes". See [attributes](https://arena.conix.io/content/python/attributes.html).

## Adding our object to the ARENA
```python
scene.add_object(box)
```

## Start the event loop
Now, outside of main, we will write:
```python
scene.run_once(main)
scene.run_tasks()
```

Now, go into the scene to see your box!

# Appendix
```python
from arena import *

# setup library
scene = Scene(host="arenaxr.org", realm="realm", scene="example")

def main():
    # make a box
    box = Box(object_id="my_box", position=Position(0,4,-2), scale=Scale(2,2,2))
    # add the box
    scene.add_object(box)

# add and start tasks
scene.run_once(main)
scene.run_tasks()
```
