"""Images

Display an image on a plane geometry.

See guidance to store paths under <a href='https://docs.arenaxr.org/content/interface/filestore.html'>ARENA File Store, CDN, or DropBox</a>.

Create an image on the floor.

URLs work in the URL parameter slot. Instead of `images/2.png` it would be e.g. `url(http://arenaxr.org/images/foo.jpg)`.
To update the image of a named image already in the scene, use this syntax.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_image():
    image_floor = Image(
        object_id="image_floor",
        position=(0, 0, 0.4),
        rotation=(-0.7, 0, 0, 0.7),
        scale=(12, 12, 2),
        material=Material(repeat={"x": 4, "y": 4}),
        url="store/users/wiselab/images/floor.png",
    )
    scene.add_object(image_floor)
    scene.update_object(
        image_floor,
        material=Material(src="store/users/wiselab/images/abstract/downtown.png"),
    )


scene.run_tasks()
