from arena import *

scene = Scene(host="arenaxr.org", scene="grab")

grabbing = False

orig_position = (0,2,-3)

def box_click(scene, evt, msg):
    global orig_position
    global grabbing

    if evt.type == "mousedown":
        clicker = scene.users[evt.data.source]
        hand = clicker.hands.get('handRight', None)

        if hand is not None and not grabbing:
            grabbing = True
            grab_dist = hand.data.position.distance_to(my_box.data.position)
            my_box.update_attributes(parent='rightHand', position=(0,0,-grab_dist))
            scene.update_object(my_box)

    elif evt.type == "mouseup":
        if grabbing:
            grabbing = False
            my_box.update_attributes(parent=None, position=orig_position)
            scene.update_object(my_box)

my_box = Box(
    object_id="my_box",
    position=orig_position,
    scale=(1.5,1.5,1.5),
    color=(50,60,200),
    patent=None,
    clickable=True,
    evt_handler=box_click
)

@scene.run_once
def main():
    scene.add_object(my_box)

scene.run_tasks()
