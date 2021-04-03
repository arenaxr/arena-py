from arena import *

scene = Scene(host="arena-dev1.conix.io", realm="realm", scene="test")

def evt_handler(scene, evt, msg):
    if evt.type == "textinput":
        print(f"{evt.data.writer}'s favorite food is {evt.data.text}!")

@scene.run_once
def make_tex_input_iso():
    my_iso = Icosahedron(
        object_id="my_iso",
        position=(0,2,-5),
        color=(100,200,100),
        clickable=True,
        textinput=TextInput(
            on="mouseup",
            title="What is your favorite food?",
            label="Please let us know below:",
            placeholder="Favorite food here"
        ),
        evt_handler=evt_handler,
    )

    scene.add_object(my_iso)

scene.run_tasks()
