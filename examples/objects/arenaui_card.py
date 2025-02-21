"""ARENAUI Card Panel

A card is a rectangular panel that can contain text and/or an image. It can be used to display
information or act as a sign. Its layout will dynamic adjust according to the optional parameters
that are provided: for instance, if no image is provided, then only text will be displayed. If only
a title is provided, it will serve more as a label or sign. An optional close button may also added.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_ui_card():
    # Add a simple info card with text and image
    intro_card = ArenauiCard(
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

    hello_card = ArenauiCard(
        object_id="hello_card",
        persist=True,
        title="Hello World",
        body="Please applaud",
        bodyAlign="center",
        position=Position(-2, 2, -2.5),
        widthScale=0.25,
        look_at="#my-camera",
    )
    scene.add_object(hello_card)


scene.run_tasks()
