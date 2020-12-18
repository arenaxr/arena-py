from arena import *

cam = None
prev_pos = None
lines = []

def new_obj_callback(msg):
    global cam
    global prev_pos
    if "camera" in msg["object_id"]:
        if cam is None:
            cam = Camera(**msg)
            prev_pos = cam.data.position

arena = Arena("arena.andrew.cmu.edu", "head", "realm", new_obj_callback=new_obj_callback)

while True:
    if cam and prev_pos:
        curr_pos = cam.data.position
        if prev_pos.dist(curr_pos) >= 0.5:
            line = Line(start=prev_pos, end=curr_pos, color="#abcdef")
            lines.append(line)
            arena.add_object(line)
            if len(lines) > 30:
                arena.delete_object(lines.pop(0))
            prev_pos = cam.data.position
    time.sleep(0.05)
