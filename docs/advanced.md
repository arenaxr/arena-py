# Advanced Example - EVEN more functionality!

## Generating "fake" events
```python
arena.generate_event(cube, "mouseenter")
```

## Attributes can be dictionaries too. Even ones that don't exist...
Say, there is data that doesn't exist in the arena library. For instance, the 3d avatar takes in a "morph" json.
```python
morph = {
    "gltf-morph__0": {
        "morphtarget": "shapes.jawOpen",
        "value": "0.7"
    },
    "gltf-morph__7": {
        "morphtarget": "shapes.browOuterUp_L",
        "value": "0.8"
    },
    "gltf-morph__8": {
        "morphtarget": "shapes.browOuterUp_R",
        "value": "0.1"
    },
    "gltf-morph__9": {
        "morphtarget": "shapes.mouthPucker",
        "value": "0.7"
    }
}

arena.update_object(avatar, **morph)
```

## Printing objects/looking at JSON
All objects are printed as JSON/python dicts. So to make sure your JSON is formatted correctly,
```python
print(avatar) # will print as a dict
print(arena.update_object(avatar, **morph)) # will print what was published as a dict
```
You can also enable debug when creating the Arena object
```python
arena = Arena(debug=True)
```

# Appendix
```python
from arena import *
import random

# setup library
arena = Arena("arena.andrew.cmu.edu", "example", "realm")

# create avatar/3d head
model_url = "/store/users/wiselab/models/FaceCapHeadGeneric/FaceCapHeadGeneric.gltf"
avatar = GLTF(object_id="my_avatar", url=model_url, position=Position(0,1.75,-1.5), scale=Scale(5,5,5))
arena.add_object(avatar)

def create_rand_morph():
    morph = {
        "gltf-morph__0": {
            "morphtarget": "shapes.jawOpen",
            "value": str(random.randint(0,100)/100)
        },
        "gltf-morph__5": {
            "morphtarget": "shapes.eyeBlink_L",
            "value": str(random.randint(0,100)/100)
        },
        "gltf-morph__6": {
            "morphtarget": "shapes.eyeBlink_R",
            "value": str(random.randint(0,100)/100)
        },
        "gltf-morph__7": {
            "morphtarget": "shapes.browOuterUp_L",
            "value": str(random.randint(0,100)/100)
        },
        "gltf-morph__8": {
            "morphtarget": "shapes.browOuterUp_R",
            "value": str(random.randint(0,100)/100)
        },
        "gltf-morph__9": {
            "morphtarget": "shapes.mouthPucker",
            "value": str(random.randint(0,100)/100)
        }
    }
    return morph

@arena.run_forever # default is 1000ms
def update_face():
    # attributes can be updated with any arbitrary dictionary!
    msg = arena.update_object(avatar, **create_rand_morph())
    # you can print the outputs for debugging
    print(msg)
    print()

# start tasks
arena.start_tasks()
```
