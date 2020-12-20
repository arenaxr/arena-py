# Beginner Example - The bare minimum you need to start using ARENA-py

## Let's start by installing and importing the library
```shell
pip3 install arena-py
```

Ok, now let's get started!

### Setup environment variables (reccomended but not required)
Replace [host], [realm], and [scene] with your desired mqtt broker, realm, and scene name, respectively.
```shell
export MQTTH=[host]
export SCENE=[scene]
export REALM=[realm]
```

## Import the library
```python
from arena import *
```

## Start the client
```python
arena = Arena()
```
You can also pass host, scene, and realm as arguments, if you don't want to use enviornment variables:
```python
arena = Arena([host], [scene], [realm])
```

## Define a task
ARENA-py works by running tasks in an event loop, so we need a main task for our sample program.
```python
def main():
```

## Our first object
Inside main(), lets make a cube!
```python
cube = Cube(object_id="my_cube", position=Position(0,4,-2), scale=Scale(2,2,2))
```
Note the input arguments. The names must match what they will be in the ARENA JSON specification. We don't have to worry too much about that now, but keep this in mind, as typos will be very bad!

Cube is a type of "object". See [objects.md](objects.md).

Position and Scale are what we call "attributes". See [attributes.md](attributes.md).

## Adding our object to the ARENA
```python
arena.add_object(cube)
```

## Start the event loop
Now, outside of main, we will write:
```python
arena.run_once(main)
arena.start_tasks()
```

Now, go into the scene to see your cube!

# Appendix
```python
from arena import *

# setup library
arena = Arena("arena.andrew.cmu.edu", "example", "realm")

def main():
    # make a cube
    cube = Cube(object_id="my_cube", position=Position(0,4,-2), scale=Scale(2,2,2))
    # add the cube
    arena.add_object(cube)

# add and start tasks
arena.run_once(main)
arena.start_tasks()
```
