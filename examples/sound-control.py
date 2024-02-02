# sound-control.py
''' Demonstrate controlling the sound file play/pause/stop events of an object (earth model, playing Earth, Wind, & Fire).
'''

from arena import *

scene = Scene(cli_args=True, debug=True)


def click_handler(scene, evt, msg):
    global earth, button_play, button_pause, button_stop
    if evt.type == "mousedown":
        if evt.object_id == button_play.object_id:
            evt_type = "soundplay"
        elif evt.object_id == button_pause.object_id:
            evt_type = "soundpause"
        elif evt.object_id == button_stop.object_id:
            evt_type = "soundstop"
        evt = Event(
            object_id=earth.object_id,
            type=evt_type,
            position=earth.data.position,
            source=scene.mqttc_id,
        )
        # send additional events to play, pause, or stop playing sound attached to the object
        scene.generate_custom_event(evt, action="clientEvent")

@scene.run_once
def main():
    global earth, button_play, button_pause, button_stop
    # Create models
    earth = GLTF(
        object_id="gltf-model_Earth",
        position=(0, 2, -3),
        scale=(5, 5, 5),
        url="/store/models/Earth.glb",
        clickable=True,
        # define default 'on' sound behavior
        sound={
            "positional": True,
            "src": "/store/audio/earth.mp3",
            "on": "mousedown"
        },
    )
    scene.add_object(earth)

    # define buttons
    button_play = Box(
        object_id="button_play",
        position=(-1, 1, -3),
        clickable=True,
        evt_handler=click_handler,
        material=Material(color=(0, 255, 0)),
    )
    scene.add_object(button_play)
    button_play_text = Text(
        object_id="button_play_text",
        parent=button_play.object_id,
        position=(0, 0, 0.5),
        value="Play",
        color=(0, 0, 0),
    )
    scene.add_object(button_play_text)

    button_pause = Box(
        object_id="button_pause",
        position=(0, 1, -3),
        clickable=True,
        evt_handler=click_handler,
        material=Material(color=(255, 255, 0)),
    )
    scene.add_object(button_pause)
    button_pause_text = Text(
        object_id="button_pause_text",
        parent=button_pause.object_id,
        position=(0, 0, 0.5),
        value="Pause",
        color=(0, 0, 0),
    )
    scene.add_object(button_pause_text)

    button_stop = Box(
        object_id="button_stop",
        position=(1, 1, -3),
        clickable=True,
        evt_handler=click_handler,
        material=Material(color=(255, 0, 0)),
    )
    scene.add_object(button_stop)
    button_stop_text = Text(
        object_id="button_stop_text",
        parent=button_stop.object_id,
        position=(0, 0, 0.5),
        value="Stop",
        color=(0, 0, 0),
    )
    scene.add_object(button_stop_text)


scene.run_tasks()
