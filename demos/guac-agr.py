# guac.py
#
# plays Tic Tac Toe
# clicked boxes alternate red and blue
# boxes fall if no winner
# boxes launch upon win
# avocado "Vanna White" reacts accordingly

import time
import arena

HOST = "oz.andrew.cmu.edu"
REALM = "realm"
SCENE = "agr-kitchen"

# Globals (yes, Sharon)

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


def childObject(**kwargs):
    return arena.Object(**kwargs, parent="sceneParent")


def initCube(x, y, color):
    name = "cube_" + str(x) + "_" + str(y)
    cubes[(x, y)] = childObject(
        objType=arena.Shape.cube,
        persist=False,
        objName=name,
        # messes up child-follow-parent pose
        # physics=arena.Physics.static,
        collision_listener=True,
        transparency=arena.Transparency(True,0.5),
        impulse=arena.Impulse("mouseup",(0,10,0),(10,1,1)),
        location=(x, y, -3),
        color=color,
        scale=(0.6, 0.6, 0.6),
        clickable=True,
        callback=guac_callback,
    )


def delete_cube(x, y):
    cubes[(x, y)].delete()


def drop_cube(x, y):
    cubes[(x, y)].update(physics=arena.Physics.dynamic)


def launch_cube(x, y):
    cubes[(x, y)].update(physics=arena.Physics.dynamic)
    cubes[(x, y)].fireEvent(arena.EventType.mouseup, (0, 0, 0), "guacprogram")


def deleteAvocado():
    global avocado
    avocado.delete()


def drawAvocado():
    global avocado
    avocado = childObject(
        persist=False,
        objName="gltf-model_avocadoman",
        objType=arena.Shape.gltf_model,
        url="models/avocadoman/scene.gltf",
        location=(-1, 0.01, -4),
        scale=(0.005, 0.005, 0.005),
    )


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
    hud = arena.Object(
        persist=False,
        objName="hudText",
        objType=arena.Shape.text,
        text="red:"+str(reds)+" blue:"+str(blues)+" draw:"+str(draws),
        location=(0, 0.4, -0.5),
        parent="myCamera",
        scale=(0.2, 0.2, 0.2),
    )


def animateAvocado():
    global avocado
    deleteAvocado()
    drawAvocado()
    avocado.update(
        animation=arena.Animation(clip="Recuperate",loop="pingpong",repetitions=2,timeScale=4)
    )


def animateAvocado2():
    global avocado
    deleteAvocado()
    drawAvocado()
    avocado.update(
        animation=arena.Animation(clip="Walking",loop="pingpong",repetitions=2)
    )


def draw_board():
    global counter
    global grid
    counter = 0
    grid = [-1, -1, -1], [-1, -1, -1], [-1, -1, -1]
    drawAvocado()
    for x in Xcoords:
        for y in Ycoords:
            initCube(x, y, (127, 127, 127))


def launch_cubes():
    for x in Xcoords:
        for y in Ycoords:
            launch_cube(x, y)


def drop_cubes():
    for x in Xcoords:
        for y in Ycoords:
            drop_cube(x, y)


def delete_cubes():
    for x in Xcoords:
        for y in Ycoords:
            delete_cube(x, y)


def animate_win():
    launch_cubes()
    animateAvocado()
    time.sleep(5)
    delete_cubes()


def animate_loss():
    drop_cubes()
    animateAvocado2()
    time.sleep(5)
    delete_cubes()


def draw_ray(click_pos, position):
    line = arena.Object(
        objName="line1",
        ttl=1,
        objType=arena.Shape.line,
        line=arena.Line( # slightly below camera so you can see line vs head-on
            (click_pos[0],click_pos[1]-0.1,click_pos[2]),
            (position[0],position[1],position[2]),1,"#FFFFFF")
    )


def guac_callback(event=None): # gets a GenericEvent

    global counter

    # only mousedown messages
    if event.event_type == arena.EventType.mousedown:

        # draw a ray from clicker to cube
        draw_ray(event.click_pos, event.position)

        color = redblue[counter % 2]
        x = int(event.object_id.split("_")[1])
        y = int(event.object_id.split("_")[2])
        if grid[(x - 1)][(y - 1)] != -1:
            return
        counter = counter + 1
        grid[(x - 1)][(y - 1)] = counter % 2
        cubes[(x, y)].update(
            #physics=arena.Physics.static,
            color=color,
            impulse=arena.Impulse("mouseup",(0,10,0),(10,1,1)),
            transparency=arena.Transparency(False,1),
            clickable=True,
            location=(x, y, -3),
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


# start the fun shall we?

arena.init(HOST, REALM, SCENE)
# make a parent scene object
sceneParent = arena.Object(
    persist=False,
    objName="sceneParent",
    objType=arena.Shape.cube,
    location=(-.6,1.2,-2),
    scale=(0.1,0.1,0.1),
    transparency=arena.Transparency(True, 0)
)
print("starting main loop")
draw_board()
arena.handle_events()
