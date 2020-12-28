from arena import *

# setup library
arena = Arena("arena.andrew.cmu.edu", "realm", "example")

@arena.run_async
async def func():
    # make a cube
    cube = Cube(object_id="my_cube", position=Position(0,4,-2), scale=Scale(2,2,2))
    arena.add_object(cube)

    def mouse_handler(evt):
        if evt.type == "mousedown":
            cube.data.position.x += 0.5
            arena.update_object(cube)

    # add click_listener
    arena.update_object(cube, click_listener=True, evt_handler=mouse_handler)

    # sleep for 10 seconds
    await arena.sleep(10000)

    # delete cube
    arena.delete_object(cube)

# start tasks
arena.run_tasks()
