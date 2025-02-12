"""Text

Display text.

More properties at <a href='https://aframe.io/docs/1.5.0/components/text.html'>A-Frame Text</a>.

Add some red text that says "Hello World".

Change text color properties [A-Frame Text](https://aframe.io/docs/1.5.0/components/text.html#properties).
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_text():
    my_text = Text(
        object_id="my_text",
        value="Hello World!",
        align="center",
        font="mozillavr",  # https://aframe.io/docs/1.4.0/components/text.html#stock-fonts
        position=(0, 2, -3),
        scale=(1.5, 1.5, 1.5),
        color=(100, 255, 255),
    )
    scene.add_object(my_text)


scene.run_tasks()
