# guac.py
#
# plays Tic Tac Toe
# clicked boxes alternate red and blue
# boxes fall if no winner
# boxes launch upon win
# avocado "Vanna White" reacts accordingly

import time

from arena import *


def end_program_callback(scene: Scene):
    global sceneParent
    scene.delete_object(sceneParent)


# command line options
arena = Scene(cli_args=True, end_program_callback=end_program_callback)
app_position = arena.args["position"]
app_rotation = arena.args["rotation"]

# variables
cubes = {}  # dict of cube objects to be indexed by tuple (x,y)
# grid elements can be:
# -1: unassigned
#  0: blue
#  1: red
grid = [-1, -1, -1], [-1, -1, -1], [-1, -1, -1]
Xcoords = [1, 2, 3]
Ycoords = [1, 2, 3]
redblue = [(255, 0, 0), (0, 0, 255)]
messages = []
counter = 0
reds = 0
blues = 0
draws = 0


def solved():
    global grid

    # rows
    for row in [0, 1, 2]:
        for color in [0, 1]:
            if (
                grid[row][0] == color
                and grid[row][1] == color
                and grid[row][2] == color
            ):
                return color

    # columns
    for col in [0, 1, 2]:
        for color in [0, 1]:
            if (
                grid[0][col] == color
                and grid[1][col] == color
                and grid[2][col] == color
            ):
                return color

    # diagonals
    if grid[0][0] == 0 and grid[1][1] == 0 and grid[2][2] == 0:
        return 0
    if grid[0][0] == 1 and grid[1][1] == 1 and grid[2][2] == 1:
        return 1
    if grid[0][2] == 0 and grid[1][1] == 0 and grid[2][0] == 0:
        return 0
    if grid[0][2] == 1 and grid[1][1] == 1 and grid[2][0] == 1:
        return 1

    return -1


def stalemate():
    global grid
    for x in Xcoords:
        for y in Ycoords:
            if grid[x - 1][y - 1] == -1:
                return False
    return True


def initCube(x, y, color):
    global sceneParent
    name = "guac-cube_" + str(x) + "_" + str(y)
    cubes[(x, y)] = Box(
        persist=True,
        object_id=name,
        # messes up child-follow-parent pose
        # physics=Physics(type="static"),
        collision_listener=True,
        material=Material(transparent=True, opacity=0.5),
        impulse=Impulse(
            on="mouseup",
            force=(0, 40, 0),
            position=(10, 1, 1)),
        position=(x, y, -3),
        color=color,
        scale=(0.6, 0.6, 0.6),
        clickable=True,
        evt_handler=guac_callback,
        parent=sceneParent.object_id,
    )
    arena.add_object(cubes[(x, y)])


def delete_cube(x, y):
    arena.delete_object(cubes[(x, y)])


# def drop_cube(x, y):
#     arena.update_object(cubes[(x, y)], physics=Physics(type="dynamic"))


# def launch_cube(x, y):
#     arena.update_object(cubes[(x, y)], physics=Physics(type="dynamic"))
#     arena.generate_click_event(cubes[(x, y)], type="mouseup")
#     # old: cubes[(x, y)].fireEvent(arena.EventType.mouseup, (0, 0, 0), "guacprogram")


def deleteAvocado():
    global avocado
    arena.delete_object(avocado)


def drawAvocado():
    global sceneParent
    global avocado
    avocado = GLTF(
        persist=True,
        object_id="guac-gltf-model_avocadoman",
        url="store/models/avocadoman/scene.gltf",
        position=(-1, 0.01, -4),
        scale=(0.005, 0.005, 0.005),
        parent=sceneParent.object_id,
    )
    arena.add_object(avocado)


def draw_hud(score):
    global reds
    global blues
    global draws
    if score == -1:
        draws = draws + 1
    if score == 1:
        reds = reds + 1
    if score == 0:
        blues = blues + 1
    hud = Text(
        persist=True,
        object_id="guac-hudText",
        text="red:"+str(reds)+" blue:"+str(blues)+" draw:"+str(draws),
        position=(2, 4, -3),
        scale=(1, 1, 1),
        color="#555555",
        parent=sceneParent.object_id,
    )
    arena.add_object(hud)


def animateAvocado():
    global avocado
    # deleteAvocado()
    # drawAvocado()
    avocado.dispatch_animation(AnimationMixer(
        clip="Recuperate", loop="pingpong", repetitions=2, timeScale=4)
    )
    arena.run_animations(avocado)


def animateAvocado2():
    global avocado
    # deleteAvocado()
    # drawAvocado()
    avocado.dispatch_animation(AnimationMixer(
        clip="Walking", loop="pingpong", repetitions=2)
    )
    arena.run_animations(avocado)


def draw_board():
    global counter
    global grid
    counter = 0
    grid = [-1, -1, -1], [-1, -1, -1], [-1, -1, -1]
    drawAvocado()
    for x in Xcoords:
        for y in Ycoords:
            initCube(x, y, (127, 127, 127))


# def launch_cubes():
#     for x in Xcoords:
#         for y in Ycoords:
#             launch_cube(x, y)


# def drop_cubes():
#     for x in Xcoords:
#         for y in Ycoords:
#             drop_cube(x, y)


def delete_cubes():
    for x in Xcoords:
        for y in Ycoords:
            delete_cube(x, y)


def animate_win():
    # launch_cubes()
    animateAvocado()
    time.sleep(5)
    delete_cubes()


def animate_loss():
    # drop_cubes()
    animateAvocado2()
    time.sleep(5)
    delete_cubes()


def draw_ray(clickPos, position):
    line = ThickLine(
        ttl=1,
        lineWidth=5,
        # slightly below camera so you can see line vs head-on
        path=((clickPos.x, clickPos.y-0.2, clickPos.z),
              (position.x, position.y, position.z)),
        color="#FF00FF",
    )
    arena.add_object(line)


def guac_callback(scene, evt, msg):
    global counter
    # only mousedown messages
    if evt.type == "mousedown":
        # draw a ray from clicker to cube
        draw_ray(evt.data.clickPos, evt.data.position)

        color = redblue[counter % 2]
        x = int(evt.object_id.split("_")[1])
        y = int(evt.object_id.split("_")[2])
        if grid[(x - 1)][(y - 1)] != -1:
            return
        counter = counter + 1
        grid[(x - 1)][(y - 1)] = counter % 2
        arena.update_object(
            cubes[(x, y)],
            # physics=Physics(type="static"),
            color=color,
            impulse=Impulse(
                on="mouseup",
                force=(0, 40, 0),
                position=(10, 1, 1)),
            material=Material(transparent=False, opacity=1),
            clickable=True,
            position=(x, y, -3),
            scale=(0.6, 0.6, 0.6),
        )

        winColor = solved()
        if winColor != -1:
            draw_hud(winColor)
            print("solved")
            animate_win()
            draw_board()
        if stalemate():
            draw_hud(-1)
            print("stalemate")
            animate_loss()
            draw_board()

    else:
        return


@arena.run_once
def main():
    global sceneParent
    # make a parent scene object
    sceneParent = Box(
        persist=True,
        object_id="guac-sceneParent",
        position=app_position,
        rotation=app_rotation,
        material=Material(transparent=True, opacity=0),
    )
    arena.add_object(sceneParent)
    print("starting main loop")
    draw_board()

    title_txt = Text(
        object_id="guac-title_txt",
        position=(2, 4.3, -3),
        text="Tic Tac Guac",
        color="#555555",
        persist=True,
        parent=sceneParent.object_id,
    )
    arena.add_object(title_txt)


arena.run_tasks()
