from arena import *
import math

scene = Scene(host="arenaxr.org", realm="realm", scene="example")
taPos = Position(-10,0,-10)
text = Text(object_id ="label", text="TA BOARD", position=Position(.25,6,4), rotation=Rotation(0,270,0))
taB = Box(object_id="my_shape1", position=Position(.25,4, 4),scale=Scale(.25,2,4), persist=True)
button2 = Cylinder(object_id="m_button1", position=Position(.1,3.3,5.5),scale=Scale(.1,.05,0.1),rotation=Rotation(0,0,90), persist=True)


class DisplayBoard(Object):
    def __init__(self,scene, board, max_display):
        self.start_display = 0
        self.end_display = 0
        self.display_amt = max_display
        self.q = []
        self.size = 0
        self.board= board
        #self.board = Box(object_id="my_shape", position=pos,scale=Scale(.25,2,4), persist=True)
        pass

    def insert(self, student, question):
        self.q.append((student,Text(object_id ="my_text"+str(self.size), text=student, rotation=Rotation(0,270,0), scale=Scale(.25,.25,0.25), parent=self.board)))
        self.size += 1 
        if self.size < self.display_amt:
            self.end_display += 1
        if self.size >= self.display_amt:
            self.start_display += 1

        
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

class TABoard(DisplayBoard):
    def __init__(self,scene, board, max_display):
        super().__init__(scene,board,max_display)
        self.id_ct = 0
        self.q = []
        self.board = board
        #inherit queue from parent QB
        #id_ct
        pass
    def display(self):   
        display_list = self.get_display_list()
        for i in range(0,len(display_list)): 
            scene.update_object(display_list[i][1],position=Position(-1.5, .25 -0.1*i, 0))
            scene.update_object(display_list[i][2],position=Position(-1.2, .25 -0.1*i, .45),scale=Scale(.05,.05,.1*.25))
    def insert(self,student,question):
        #add button to associate with q
        #inc id_ct

        self.q.append((student,Text(object_id ="my_text_t"+str(self.size), text=student, rotation=Rotation(0,270,0), scale=Scale(.25,.25,0.25), parent=self.board),Cylinder(object_id="my_button"+str(self.size), rotation=Rotation(0,0,90), parent= self.board)))
        self.size += 1 
        if self.size < self.display_amt:
            self.end_display += 1

    def dequeue(self, student):
        #pop entry from q
        pass

class QBoard(DisplayBoard):
    def __init__(self,scene, board, max_display):
        super().__init__(scene,board, max_display)
        self.TABoards = []
        self.board = board
        self.button = Cylinder(object_id="my_button", position=Position(.1,3.3,-1.5),scale=Scale(.1,.05,0.1),rotation=Rotation(0,0,90), persist=True)
        #id_ct
    def insert(self, student, question):
        self.q.append((student,Text(object_id ="my_text"+str(self.size), text=student, rotation=Rotation(0,270,0), scale=Scale(.25,.25,0.25), parent=self.board)))
        self.size += 1 
        if self.size < self.display_amt:
            self.end_display += 1
        for i in range(len(self.TABoards)):
            self.TABoards[i].insert(student,question)

        #loop through TA boards and call updateinsrt
        #inc id_ct
        pass
    def addTABoard(self, ta_board):
        self.TABoards.append(ta_board)
     
    def delTABoard(self):
        #delete ta board
        pass
    def dequeue(self, student):
        #pop entry from q, update all TA lists
        pass
    def display(self):
       
        display_list = self.get_display_list()
        for i in range(0,len(display_list)): 
            scene.update_object(display_list[i][1],position=Position(-1.5, .25 -0.1*i, 0))

queue = QBoard(scene,Box(object_id="my_shape", position=Position(.25,4,-3),scale=Scale(.25,2,4), persist=True),5);
taBoard = TABoard(scene, taB,5)
queue.addTABoard(taBoard)
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
    scene.add_object(queue.button)
    scene.add_object(queue.board)
    scene.add_object(button2)
    scene.add_object(taBoard.board)
    scene.add_object(text)

@scene.run_forever(interval_ms=100)
def main():
    global queue
    global scene
    global taBoard
    def mouse_handler(scene, evt,msg):
        #
        if evt.type == "mousedown" and clickB(evt.data.clickPos, queue.button.data.position,1):
            print("adding ", msg["data"]["source"])
            queue.insert(msg["data"]["source"],"a")
            queue.display()
            taBoard.display()
    def ta_mouse_handler(scene, evt, msg):
        if evt.type == "mousedown":
            for obj in(taBoard.get_display_list()):
                #print(obj[2]['data']['position'])
                #print(evt['data']['clickPos'])
                #print(obj[2]['data']['position'].distance_to(evt['data']['clickPos']))
                if obj[2]['data']['position'].distance_to(evt['data']['clickPos']) <20:
                    teleport(taPos, msg["data"]["source"])

    scene.update_object(queue.button, click_listener=True, evt_handler=mouse_handler)
    for obj in (taBoard.get_display_list()):
        scene.update_object(obj[2], click_listener=True, evt_handler=ta_mouse_handler)


scene.run_tasks()

