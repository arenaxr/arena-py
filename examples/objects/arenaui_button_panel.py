"""ARENAUI Button Panel

A button panel is a horizontal or vertical panel that contains buttons. Each button can have a
text or image label. When a button is clicked, a message is sent over pubsub with
the `buttonName` and `buttonIndex`.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_ui_button_panel():
    # Add a button panel, with two sets of buttons
    first_buttonset = [Button(name="Prompt A"), Button(name="Option B"), Button("More")]
    second_buttonset = [Button("D"), Button("E"), Button("F"), Button("Back")]

    def button_handler(_scene, evt, _msg):
        global prompt
        if evt.type == "buttonClick":
            if evt.data.buttonName in ["Option B", "D", "E", "F"]:  # Compare buttonName
                print(f"{evt.data.buttonName} clicked!")
            elif evt.data.buttonName == "More":  # switch to second button set
                scene.update_object(button_panel, buttons=second_buttonset)
            elif evt.data.buttonIndex == 3:  # compare buttonIndex, switch 1st set
                scene.update_object(button_panel, buttons=first_buttonset)

    button_panel = ArenauiButtonPanel(
        object_id="button-panel",
        persist=True,
        title="Option Buttons",
        buttons=first_buttonset,
        vertical=True,
        font="Roboto-Mono",
        position=Position(2, 2, -2.5),
        evt_handler=button_handler,
    )
    scene.add_object(button_panel)


scene.run_tasks()
