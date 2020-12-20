from arena import *

# setup library
arena = Arena("arena.andrew.cmu.edu", "example", "realm")

x = 0

@arena.run_async
async def func():
    # make a cube
    cube = Cube(object_id="my_cube", position=Position(x,4,-2), scale=Scale(2,2,2))
    arena.add_object(cube)

    def mouse_handler(evt):
        global x
        if evt.type == "mousedown":
            arena.update_object(cube, position=Position(x,4,-2))
            x += 0.5

    # add click_listener
    arena.update_object(cube, click_listener=True, evt_handler=mouse_handler)

    # sleep for 10 seconds
    await arena.sleep(10000)

    # delete cube
    arena.delete_object(cube)

# start tasks
arena.start_tasks()
