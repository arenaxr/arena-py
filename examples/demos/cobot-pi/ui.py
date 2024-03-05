from arena import *

scene = Scene(host="arenaxr.org", namespace = "johnchoi", scene="MyCobotPi320")

prompt = None


@scene.run_once
def setup_scene():
    # Add a simple info card with text and image
    intro_card = Card(
        object_id="intro-card",
        persist=True,
        title="Welcome to ARENA",
        body="ARENA is a framework designed to both simplify and host collaborative "
        "multi-user XR applications. It makes it easy to combine virtual and "
        "physical components like sensors, actuators, and digital interfaces in "
        "an immersive 3D environment.",
        bodyAlign="left",
        imgDirection="left",
        img="/static/landing/images/xr-logo-v8.png",
        imgSize="contain",
        position=Position(0, 2, -2.5),
    )
    scene.add_object(intro_card)

    hello_card = Card(
        object_id="hello_card",
        persist=True,
        title="Hello World",
        body="Please applaud",
        bodyAlign="center",
        position=Position(-2, 2, -2.5),
        widthScale=0.25,
        look_at="#my-camera"
    )
    scene.add_object(hello_card)

    # Add a popup prompt with single button

    def prompt_handler(_scene, evt, _msg):
        if evt.type == "buttonClick":
            if evt.data.buttonName == "OK":
                print("OK clicked!")
                scene.delete_object(prompt)

    # Add a button panel, with two sets of buttons

    first_buttonset = [Button(name="Prompt A"), Button(name="Option B"), Button("More")]
    second_buttonset = [Button("D"), Button("E"), Button("F"), Button("Back")]

    def button_handler(_scene, evt, _msg):
        global prompt
        if evt.type == "buttonClick":
            if evt.data.buttonName in ["Option B", "D", "E", "F"]: # Compare buttonName
                print(f"{evt.data.buttonName} clicked!")
            elif evt.data.buttonName == "Prompt A":  # Show prompt
                prompt = Prompt(
                    object_id="promptA",
                    title="Prompt A",
                    description="This is a prompt with a description.",
                    buttons=["OK"],
                    position=Position(2, 2, -2),
                    evt_handler=prompt_handler,
                )
                scene.add_object(prompt)
            elif evt.data.buttonName == "More":  # switch to second button set
                scene.update_object(button_panel, buttons=second_buttonset)
            elif evt.data.buttonIndex == 3:      # compare buttonIndex, switch 1st set
                scene.update_object(button_panel, buttons=first_buttonset)

    button_panel = ButtonPanel(
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
