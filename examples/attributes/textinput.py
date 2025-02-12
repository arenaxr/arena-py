"""Text Input

Opens an HTML prompt when clicked. Sends text input as an event on MQTT. Requires click-listener.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

textinput = TextInput(
    on="mouseup",
    title="What is your favorite food?",
    label="Please let us know below:",
    placeholder="Favorite food here",
)


def evt_handler(scene, evt, msg):
    if evt.type == "textinput":
        display_name = scene.all_objects[evt.data.writer].displayName
        print(f"{display_name}'s favorite food is: {evt.data.text}!")


@scene.run_once
def make_tex_input_iso():
    my_iso = Icosahedron(
        object_id="my_iso",
        position=(0, 2, -5),
        material=Material(color=(100, 200, 100)),
        clickable=True,
        evt_handler=evt_handler,
        textinput=textinput,
    )
    scene.add_object(my_iso)


scene.run_tasks()
