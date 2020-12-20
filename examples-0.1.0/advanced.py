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
    # attributes can be updated with any abitrary dictionary!
    msg = arena.update_object(avatar, **create_rand_morph())
    # you can print the outputs for debugging
    print(msg)
    print()

# start tasks
arena.start_tasks()
