"""Images

Display an image on a plane.

See guidance to store paths under <a href='https://docs.arenaxr.org/content/interface/filestore.html'>ARENA File Store, CDN, or DropBox</a>.

Create an image on the floor.

{
  "object_id": "image_floor",
  "action": "create",
  "type": "object",
  "data": {
    "object_type": "image",
    "position": { "x": 0, "y": 0, "z": 0.4 },
    "rotation": { "x": -0.7, "y": 0, "z": 0, "w": 0.7 },
    "url": "images/floor.png",
    "scale": { "x": 12, "y": 12, "z": 2 },
    "material": { "repeat": { "x": 4, "y": 4 } }
  }
}

URLs work in the URL parameter slot. Instead of `images/2.png` it would be e.g. `url(http://arenaxr.org/images/foo.jpg)`.
To update the image of a named image already in the scene, use this syntax.

{
  "object_id": "image_2",
  "action": "update",
  "type": "object",
  "data": { "material": { "src": "https://arenaxr.org/abstract/downtown.png" } }
}
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_im():
    im = Image(
        object_id="im",
        position=(0, 2, -3),
        scale=(1.2, 1.5, 1.2),
        url="store/users/wiselab/images/conix-face-white.jpg",
    )
    scene.add_object(im)


scene.run_tasks()
