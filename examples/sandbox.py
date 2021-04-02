from arena import *
import math

scene = Scene(host="arenaxr.org", realm="realm", scene="example")
shape = Box(object_id="my_shape", position=Position(.25,4,-3),scale=Scale(.25,2,4), persist=True)
button = Cylinder(object_id="my_button", position=Position(.1,3.3,-1.5),scale=Scale(.1,.05,0.1),rotation=Rotation(0,0,90), persist=True)
taPos = Position(-10,0,-10)

taB = Box(object_id="my_shape1", position=Position(4.25,4,-3),scale=Scale(.25,2,4), persist=True)
button2 = Cylinder(object_id="my_button1", position=Position(4.1,3.3,-1.5),scale=Scale(.1,.05,0.1),rotation=Rotation(0,0,90), persist=True)


class QuestionBoard(Object):
    def __init__(self,scene, max_display):
        self.start_display = 0
        self.end_display = 0
        self.display_amt = max_display
        self.q = []
        self.size = 0
    def insert(self, student, question):
        self.q.append((student,Text(object_id ="my_text"+str(self.size), text=student, rotation=Rotation(0,270,0), scale=Scale(.25,.25,0.25), parent=shape)))
        self.size += 1 
        if self.size < self.display_amt:
            self.end_display += 1
    def dequeue(self, student):
        if self.size <= 0:
            print("queue empty!")
            return
        (student,question) = self.q.pop()
        self.size -= 1
        if self.size < self.display_amt:
            self.end_display -= 1
        return (student,question)
    def scroll_up(self):
        if self.start_display == 0 and (self.end_display - self.start_display < display_amt):
            print("at top!")
            return
        self.start_display -= 1
        self.end_diaply -= 1

    def scroll_down(self):
        if self.end_display == self.size and (self.end_display - self.start_display < display_amt):
            print("at bottom!")
            return
        self.start_display += 1
        self.end_diaply += 1


    def get_display_list(self):
        return self.q[self.start_display:self.start_display + self.end_display]

class TABoard(Object):
    def __init__(self,QBoard, position, max_display):
        self.start_display = 0
        self.end_display = 0
        self.display_amt = max_display
        self.q = []
        self.size = 0
    def getSize(self):
        return self.size
    def insert(self, student, question):
        self.q.append((student,question))
        self.size += 1 
        if self.size < self.display_amt:
            self.end_display += 1
    def dequeue(self, student):
        if self.size <= 0:
            print("queue empty!")
            return
        (student,question) = self.q.pop()
        self.size -= 1
        if self.size < self.display_amt:
            self.end_display -= 1
        return (student,question)


queue = QuestionBoard(scene,5)

"""
create Qboard object
   saves object_ids of students when they put their questions on the queue
   displays top 10 questions on queue

   shows their question and place in line
"""


"""
create Taboard object
   shows questions and button next to each question
   if button pressed then student (obj_id associated with question teleports to u   TA)

"""
def clickB(pos1,pos2,bound):
    xInBound = (pos1.z >= pos2.z - bound) and (pos1.z <= pos2.z + bound)
    yInBound = (pos1.y >= pos2.y - bound) and (pos1.y <= pos2.y + bound)
    return xInBound and yInBound 
def teleport(ta, student):
    for user in scene.users.values():
        if user.object_id == student:
            print("teleported!")
            scene.manipulate_camera(
                user,
                position= ta
            ) 

@scene.run_once
def setup():
    scene.add_object(button)
    scene.add_object(shape)
    scene.add_object(button2)
    scene.add_object(taB)

@scene.run_forever(interval_ms=100)
def main():
    global queue
    global scene
    global taPos
    def mouse_handler(scene, evt,msg):
        #
        if evt.type == "mousedown" and clickB(evt.data.clickPos, button.data.position,1):
            print("adding ", msg["data"]["source"])
            queue.insert(msg["data"]["source"],"a")
            #teleport(taPos, msg["data"]["source"])
    def ta_mouse_handler(scene, evt, msg):
        if evt.type == "mousedown" and clickB(evt.data.clickPos, button.data.position,1):
            print("adding ", msg["data"]["source"])
            teleport(taPos, msg["data"]["source"])
    display_list = queue.get_display_list()
    for i in range(0,len(display_list)): 
        #scene.add_object(display_list[i][1])
        scene.update_object(display_list[i][1],position=Position(-1.5, .25 -0.1*i, 0))
    scene.update_object(shape, click_listener=True, evt_handler=mouse_handler)
    scene.update_object(taB, click_listener=True, evt_handler=ta_mouse_handler)


scene.run_tasks()

