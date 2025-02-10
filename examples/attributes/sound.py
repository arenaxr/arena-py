"""Sound

Play toy piano sound from a URL when you click a box. Sets click-listener Component, waveform URL, and sound attribute.

{
  "object_id": "box_asharp",
  "action": "create",
  "type": "object",
  "data": {
    "object_type": "box",
    "position": { "x": 2.5, "y": 0.25, "z": -5 },
    "scale": { "x": 0.8, "y": 1, "z": 1 },
    "material": { "color": "#000000" },
    "sound": {
      "src": "url(https://arenaxr.org/audio/toypiano/Asharp1.wav)",
      "on": "mousedown"
    },
    "click-listener": ""
  }
}
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

sound = Sound(positional=True, poolSize=1, autoplay=True, src="store/users/wiselab/audio/september.mp3")

@scene.run_once
def make_music_box():
    my_box = Box(
        object_id="my_box",
        sound=sound
    )

    scene.add_object(my_box)

scene.run_tasks()
