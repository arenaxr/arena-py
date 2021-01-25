from arena import *

# setup library
arena = Arena(host="arena.andrew.cmu.edu", realm="realm", scene="example")

@arena.run_async
async def func():
    # make a box
    box = Box(object_id="my_box", position=Position(0,4,-2), scale=Scale(2,2,2))
    arena.add_object(box)

    def mouse_handler(evt):
        if evt.type == "mousedown":
            box.data.position.x += 0.5
            arena.update_object(box)

    # add click_listener
    arena.update_object(box, click_listener=True, evt_handler=mouse_handler)

    # sleep for 10 seconds
    await arena.sleep(10000)

    # delete box
    arena.delete_object(box)

# start tasks
arena.run_tasks()
