from arena import *

# setup library
scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")

@scene.run_async
async def func():
    # make a box
    box = Box(object_id="my_box", position=Position(0,4,-2), scale=Scale(2,2,2))
    scene.add_object(box)

    def mouse_handler(scene, evt, msg):
        if evt.type == "mousedown":
            box.data.position.x += 0.5
            scene.update_object(box)

    # add click_listener
    scene.update_object(box, click_listener=True, evt_handler=mouse_handler)

    # sleep for 10 seconds
    await scene.sleep(10000)

    # delete box
    scene.delete_object(box)

# start tasks
scene.run_tasks()
