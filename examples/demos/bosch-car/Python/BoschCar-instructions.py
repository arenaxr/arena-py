from arena import *

guide_state = -1
# -1 "get started"
# 0 "open the hood"
# 1 "remove the engine block"
# 2 "replace the engine block"
# 3 "close the hood"

def car_events_cb(_scene, obj, msg):
    """
    Callback to handle specific events for the Bosch Car.
    """
    obj_id = obj['object_id']
    if obj_id == "BoschCar_Hood":
        # Handle open and close rotation animations
        try:
            to_rotate = msg["data"].get("animation__rotation",{}).get("to")
            if to_rotate == "0 0 0":
                if guide_state == 3:
                    print("Hood Closing, reset")
                    render_guide(-1)
            elif to_rotate is not None:
                print("Hood Opening")
                render_guide(1)
        except:
            pass
    elif obj_id == "BoschCar_Engine_Block":
        try:
            to_pos = msg["data"].get("animation__position", {}).get("to", {}).get("y", -1)
            if to_pos == 0:
                if guide_state == 2:
                    print("Engine Block Closing")
                    render_guide(3)
            elif to_pos > 0:
                print("Engine Block Opening")
                render_guide(2)
        except:
            pass
    elif msg["action"] == "clientEvent" and msg["type"] == "buttonClick":
        if msg["data"]["buttonName"] == "Begin Repair":
            print("Begin Repair Button Clicked")
            render_guide(0)


prompt = ArenauiPrompt(
    object_id="guide_sign_panel",
    parent="BoschCar_Root",
    title="Car Repair Guide",
    description="Let's get Started!",
    buttons=[
        Button("Begin Repair"),
    ],
    position=(0.75, 0.5, -0.25),
    look_at="#my-camera",
    persist=True,
    width=1.25,
    scale=Scale(0.5, 0.5, 0.5),
)
panel = ArenauiCard(
    object_id="guide_sign_prompt",
    parent="BoschCar_Root",
    title="Car Repair Guide",
    body="Let's get Started!",
    bodyAlign="center",
    position=(0.75, 0.5, -0.25),
    look_at="#my-camera",
    persist=True,
    widthScale=0.33,
)

# We need this to anchor guideline starting point from sign
sign_ref = Box(
    depth=0.01,
    height=0.5,
    width=0.5,
    position=(0.75, 0.5, -0.25),
    material=Material(visible=False),
    object_id="guide_sign_ref",
    look_at="#my-camera",
    parent="BoschCar_Root",
    persist=True,
)
# Need this as target obj pointer
guide_line_parent = Box(
    object_id="guide_line_parent",
    parent="guide_sign_ref",
    material=Material(visible=False),
    look_at="#Boschcar_hood_ref",
    persist=True,
)

# Guide line has rotation "forward" to target object it's looking at
guide_material = Material(color=Color("#ff1117"), opacity= 0.66, visible=False)
guide_line = Cylinder(
    object_id="guide_line",
    height=0.5,
    radius=0.005,
    position=(0,0,0.4),
    material=guide_material,
    persist=True,
    parent="guide_line_parent",
    rotation=Rotation(90,0,0)
)

engline_block_ref = Box(
    object_id="Boschcar_engine_block_ref",
    material=Material(visible=False),
    persist=True,
    position=(0,0.3,0),
    parent="BoschCar_Engine_Block"
)
hood_ref = Box(
    object_id="Boschcar_hood_ref",
    material=Material(visible=False),
    persist=True,
    position=(0,-0.1,-0.2),
    parent="BoschCar_Hood"
)


def render_guide(to_state):
    """
    Render the guide for the car repair process. Steps through each state in order
    :param to_state: Guide state to render
    """
    global guide_state, guide_line_parent, guide_line_opacity, guide_line
    if to_state == -1:
        panel.update_attributes(scale=Scale(0.001,0.001,0.001))
        prompt.update_attributes(scale=Scale(0.5, 0.5, 0.5))
        guide_material.visible = False
        scene.update_objects([panel, prompt, guide_line])
        guide_state = to_state
    if guide_state != to_state - 1:
        return
    if to_state == 0:
        prompt.update_attributes(scale=Scale(0.001,0.001,0.001))
        panel.update_attributes(scale=Scale(1,1,1))
        guide_material.visible = True
        scene.update_objects([panel, prompt, guide_line])
        panel.update_attributes(
            body="Step 1: Open the hood",
        )
        scene.update_object(panel)
        # Draw arrow to the hood
    elif to_state == 1:
        panel.update_attributes(
            body="Step 2: Remove the engine block",
        )
        guide_line_parent.update_attributes(look_at="#Boschcar_engine_block_ref")
        scene.update_objects([panel, guide_line_parent])
        print(1)
        # Draw arrow to the engine block
    elif to_state == 2:
        panel.update_attributes(
            body="Step 3: Replace the engine block",
        )
        guide_line_parent.update_attributes(look_at="#Boschcar_engine_block_ref")
        scene.update_objects([panel, guide_line_parent])
    elif to_state == 3:
        panel.update_attributes(
            body="Step 4: Close the hood",
        )
        guide_line_parent.update_attributes(look_at="#Boschcar_hood_ref")
        scene.update_objects([panel, guide_line_parent])
    guide_state = to_state


scene = Scene(host="arenaxr.org", namespace="public", scene="arena", on_msg_callback=car_events_cb)

scene.add_objects([panel, prompt, sign_ref, guide_line_parent, guide_line, engline_block_ref, hood_ref])

render_guide(-1)

# our main event loop
scene.run_tasks()