from arena import *

scene = Scene(host="arenaxr.org", realm="realm", scene="example")

@scene.run_once
def make_text():
    my_text = Text(
        object_id="my_text",
        text="Hello World!",
        align="center",
        font="mozillavr", # https://aframe.io/docs/1.2.0/components/text.html#stock-fonts
        position=(0,2,-3),
        scale=(1.5,1.5,1.5),
        color=(100,255,255),
    )
    scene.add_object(my_text)

scene.run_tasks()
