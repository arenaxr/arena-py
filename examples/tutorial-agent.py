from arena import *
import random, math

arena = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")

model_url = "/store/users/wiselab/models/FaceCapHeadGeneric/FaceCapHeadGeneric.gltf"
avatar = GLTF(
        object_id="my_avatar",
        url=model_url,
        position=(0,1.75,-1.5),
        rotation=(0,0,0),
        scale=(10,10,10)
    )
arena.add_object(avatar)

speech = Text(
        object_id="my_text",
        text="Hello!",
        parent=avatar,
        align="center",
        position=(0,0.3,0),
        scale=(0.4,0.4,0.4)
    )
arena.add_object(speech)

instructions = Text(
        object_id="instructions",
        color=(100,50,75),
        text="",
        position=(15.4,7,0),
        scale=(3,3,3)
    )

ticks = 0

code = []

box_ready = False

def talk():
    morph = {
        "gltf-morph__0": {
            "morphtarget": "shapes.jawOpen",
            "value": str(random.randint(0,70)/100)
        },
    }
    arena.update_object(avatar, **morph)

def close_mouth():
    morph = {
        "gltf-morph__0": {
            "morphtarget": "shapes.jawOpen",
            "value": str(0.1)
        },
    }
    arena.update_object(avatar, **morph)

def update_code():
    arena.update_object(instructions, text="\n\n".join(code), align="left")

@arena.run_forever(interval_ms=50)
def main():
    global ticks
    global code
    global box_ready

    if ticks < 80:
        talk()

        if ticks == 20:
            speech.data.text = "Welcome to the ARENA!"
            arena.update_object(speech)
        if ticks == 40:
            speech.data.text = "My name is Mr. Tutorial Avatar, but you can\ncall me TA. I am here to help guide you"
            arena.update_object(speech)
        if ticks == 60:
            speech.data.text = "Follow me!"
            arena.update_object(speech)

    if ticks == 80:
        close_mouth()

    if ticks == 90:
        avatar.data.rotation.y = 180
        arena.update_object(avatar)

    if 90 < ticks < 160:
        avatar.data.position.z -= 0.2
        avatar.data.position.y += 0.01
        arena.update_object(avatar)

    if 160 < ticks < 180:
        avatar.data.rotation.y = 0
        avatar.data.rotation.z = 0
        arena.update_object(avatar)

    if 175 < ticks < 500:
        talk()

        if ticks == 180:
            speech.data.text = "Let's write a\nPython program!"
            arena.update_object(speech)

            instructions.data.position.z = avatar.data.position.z
            arena.add_object(instructions)

        if ticks == 200:
            speech.data.text = "To my left is the Python\ncode I will have you write:"
            arena.update_object(speech)

            code += ["from arena import *"]
            update_code()

        if ticks == 220:
            speech.data.text = "Can you type the code I\nshow next to me?"
            arena.update_object(speech)

        if ticks == 250:
            speech.data.text = "Let's start by importing the\nARENA-py library and initializing it:"
            arena.update_object(speech)

        if ticks == 270:
            code += [f"arena = Scene(host=\"{arena.host}\", realm=\"{arena.realm}\", namespace=\"{arena.namespace}\", scene\"{arena.scene}\")"]
            update_code()

        if ticks == 300:
            speech.data.text = "Next, let's create our\nfirst Object: a box!"
            arena.update_object(speech)

        if ticks == 320:
            code += [f"box = Box(object_id=\"my_box\", position=(0,4,-2), scale=(2,2,2))"]
            update_code()

        if ticks == 340:
            speech.data.text = "Next, let's add that box\nto the ARENA:"
            arena.update_object(speech)

        if ticks == 360:
            code += ["arena.add_object(box)"]
            update_code()

        if ticks == 380:
            speech.data.text = "Finally, let's run the\nARENA-py event loop:"
            arena.update_object(speech)

        if ticks == 400:
            code += ["arena.run_tasks()"]
            update_code()

        if ticks == 420:
            speech.data.text = "Can you copy this code and\nexecute it? I'll wait!"
            arena.update_object(speech)

        if 420 < ticks < 460:
            avatar.data.position.z += 0.2
            avatar.data.position.y -= 0.01
            arena.update_object(avatar)

        if ticks == 480:
            close_mouth()

            def box_made(scene, obj, msg):
                global box_ready
                if "object_id" in obj:
                    box_ready = (obj.object_id == "my_box")

            arena.new_obj_callback = box_made

    if box_ready:
        talk()
        speech.data.text = "Congrats, you did it!"
        arena.update_object(speech)
        arena.update_object(avatar, sound=Sound(positional=True, poolSize=1, autoplay=True, src="store/users/wiselab/audio/september.mp3"))
        arena.delete_object(instructions)
        box_ready = False

    ticks += 1

arena.run_tasks()
