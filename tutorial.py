from arena import *

# should actually run, but can also specify as arguments:
"""
export MQTTH=arena.andrew.cmu.edu
export REALM=realm
export SCENE=render
"""

# start ARENA client
arena = Arena("arena.andrew.cmu.edu", "render", "realm")

# create a cube. notice the argument format
cube = Cube(object_id="cube", position=Position(0,4,-2), scale=Scale(2,2,2))
arena.add_object(cube) # you MUST run this code to make objects show up in the ARENA

time.sleep(2)

# not reccomended, but you can also input a dictionary as arguments
cube1 = Cube(object_id="cube1", position={"x":-4,"y":2,"z":-2}, scale={"x":2,"y":2,"z":2})
arena.add_object(cube1)

time.sleep(2)

# lets make some noise!
cube2 = Cube(object_id="cube2", position={"x":4,"y":2,"z":-2},
                sound=Sound(positional=True, poolSize=8,
                    src="store/users/wiselab/audio/glass.oga",
                    autoplay=True
                )
            )
arena.add_object(cube2)

time.sleep(2)

# inheritance
text = Text(object_id="text", text="Welcome to the new ARENA-py", position=Position(0,1,0), parent=cube)
arena.add_object(text)

time.sleep(2)

# updating attributes
cube2.update_attributes(scale=Scale(3,2,2), position=Position(5,6,-2))
arena.update_object(cube2)
# arena.update_object(cube2, scale=Scale(3,2,2), position=Position(5,4,-2)) <- also works
text = Text(object_id="text1", text="Hi, I am up here now!", position=Position(0,1,0), parent=cube2)
arena.add_object(text)

time.sleep(2)

# deleting objects
arena.delete_object(text)

time.sleep(2)

# add events
def evt_handler(evt):
    print(evt.type)

cube1.update_attributes(click_listener=True, evt_handler=evt_handler, color="#fedcba")
arena.update_object(cube1)
text = Text(object_id="text2", text="Click me (will be active for 3 seconds)!", position=Position(0,1,0), parent=cube1)
arena.add_object(text)

time.sleep(3)

# remove events
cube1.update_attributes(click_listener=False) # click_listener=None also works
arena.update_object(cube1)
# should get a warning that we are overriding a previously made object!
text = Text(object_id="text2", text="Can't click me anymore!", position=Position(0,1,0), parent=cube1)
arena.add_object(text)

time.sleep(2)

# arena callbacks
def on_msg_callback(msg):
    print("I will get called when there is a new message in the arena!")
def new_obj_callback(msg):
    print("I will get called when there is a new object in the arena that you havent seen before!")

arena.on_msg_callback = on_msg_callback
arena.new_obj_callback = new_obj_callback

# if id is unspecified, arena will generate a random uuid4
torus = Torus(position=Position(0,3,-5), scale=Scale(2,2,3), color="#abcedf")
arena.add_object(torus)
# ^ should call callback

time.sleep(3)

text = Text(object_id="text", text="Turn flying mode on!", position=Position(0,1,0), parent=cube)
arena.add_object(text)

# line following program! A line will trace your flight!
cam = None
prev_pos = None
lines = []

def on_msg_callback1(msg):
    global cam
    global prev_pos

    if "camera" in msg["object_id"]:
        if cam is None:
            cam = Camera(**msg) # only created once, the rest of the time, it will automatically be updated by the library!
            prev_pos = cam.data.position

arena.on_msg_callback = on_msg_callback1
arena.new_obj_callback = None

# user defined event loop. MUST have this for all objects to be created!
while True:
    if cam and prev_pos:
        arena.on_msg_callback = None
        curr_pos = cam.data.position # cam.data.position is automatically updated
        if prev_pos.dist(curr_pos) >= 0.5:
            line = Line(start=prev_pos, end=curr_pos, color="#abcdef")
            lines.append(line)
            arena.add_object(line)
            if len(lines) > 50:
                arena.delete_object(lines.pop(0))
            prev_pos = cam.data.position
    time.sleep(0.05)

