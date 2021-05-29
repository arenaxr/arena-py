'''
oh-boards.py
    Demonstrates queue board and TA boards for enqueuing and dequeuing students in OH
    To test, run:
        > python3.8 oh-boards.py
    
    There should be three boards (one under Main Queue; two under TA Boards)
    Main Queue Usage:
        The top left buttons on the Main Queue are for scrolling up and down the queue.
        The bottom right button on the Main Queue is for adding questions to the queue.
        Currently we're only adding the camera id but once text input is integrated this should be changed to the student's question

    TA Board Usage:
        The top left buttons on the Main Queue are for scrolling up and down the queue.
        Whenever a question is added to the Main Queue it should also appear on each TA Board linked to it with a button next to the question.
        If a button is pressed then the student who enqueued the question should teleport to the user (TA) who pressed that button and the student should be dequeued.
    
    @author Denise Yang <denisey@andrew.cmu.edu>
    @date   05/28/2021

'''
from arena import *
import math

scene = Scene(host="arenaxr.org", realm="realm", scene="example")

taPos = Position(-10,0,0)     #TA position to teleport to for testing purposes
board_size = Scale(.25,2,4)     #Size of boards
max_display_amount = 4          #Amount of questions to display on the queue
spacing  = -0.15                #Amount of spacing between queue elements

#Base identifiers to prevent overwriting objects
button_id = "button_"

#TA board label
ta_label = Text(
    object_id ="ta_boards_label", 
    text="TA Boards", 
    position=Position(.25,6,4), 
    rotation=Rotation(0,270,0),
    persist=True)

#Main Queue label
queue_label = Text(
    object_id ="queue_label", 
    text="Main Queue", 
    position=Position(.25,6,-3), 
    rotation=Rotation(0,270,0),
    persist=True)

#TA board objects to be displayed
taB = Box(
    object_id="ta_board1", 
    position=Position(.25,4, 4),
    scale=board_size, 
    persist=True)
taB2 = Box(
    object_id="ta_board2", 
    position=Position(.25,4, 8),
    scale=board_size, 
    persist=True)


"""
DisplayBoard object
   Basic queue with scrolling fuctionality and the ability to dequeue students anywhere in the queue
   @param scene: scene to display
   @param board: board object to display on
   @param max_display: max students to display at a time
   @id: a unique identifier for the board
"""
class DisplayBoard(Object):
    def __init__(self,board, max_display, id):
        self.start_display = 0                    
        self.end_display = 0
        self.display_amt = max_display + 1
        self.size = 0
        self.board= board
        #queue to hold students' questions
        self.q = []                           
        #objects to be displayed in scene
        self.display_objects = []
        #button for scrolling up
        self.up_button = Cylinder(object_id="up_button_"+id, position=Position(-.5,.4,-.4),scale=Scale(.05,.4,.025),rotation=Rotation(0,0,90), persist = True, parent = self.board)
        #button for scrolling down
        self.down_button = Cylinder(object_id="down_button_"+id, position=Position(-.5,.3,-.4),scale=Scale(.05,.4,.025),rotation=Rotation(0,0,90), persist = True, parent = self.board)

    def insert(self, item):
        self.q.append(item)
        self.size += 1 
        if self.size < self.display_amt:
            self.end_display += 1

    def get_display_list(self):
        return self.q[self.start_display:self.end_display]
   
    def scroll_up(self):
        if self.start_display == 0 and (self.end_display - self.start_display < self.display_amt):
            print("at top!")
            return
        self.start_display -= 1
        self.end_display -= 1
        display_list = self.get_display_list()
        for i in range(0,len(self.display_objects)): 
            scene.update_object(self.display_objects[i][0],text=display_list[i][1])

    def scroll_down(self):
        if self.end_display == self.size and (self.end_display - self.start_display < self.display_amt):
            print("at bottom!")
            return
        self.start_display += 1
        self.end_display += 1
        display_list = self.get_display_list()
        for i in range(0,len(self.display_objects)): 
            scene.update_object(self.display_objects[i][0],text=display_list[i][1])
    
    ###Scene Setup Functions ###
    def scroll_up_mouse_handler(self,scene, evt, msg):
        if evt.type == "mousedown" and evt['data']['position'].distance_to(evt['data']['clickPos']) < 7:
            self.scroll_up()
            
    def scroll_down_mouse_handler(self,scene, evt, msg):
        if evt.type == "mousedown" and evt['data']['position'].distance_to(evt['data']['clickPos']) < 7:
            self.scroll_down()

    #enable scrolling events
    def enable_scrolling(self, scene):
        scene.update_object(self.up_button, click_listener=True, evt_handler= self.scroll_up_mouse_handler)
        scene.update_object(self.down_button, click_listener=True, evt_handler= self.scroll_down_mouse_handler)

    #initialize board in scene
    def show_board(self,scene):
        scene.add_object(self.up_button)
        scene.add_object(self.down_button)
        scene.add_object(self.board)

    


"""
TABoard object
   Shows students' questions with button to dequeue individual questions. If the button is pressed then student teleports to the TA)
   @param scene: scene to display
   @param board: board object to display on
   @param max_display: max students to display at a time
   @qboard: the main QBoard that students can submit questions
   @board_id: a unique identifier for the board
"""
class TABoard(DisplayBoard):
    def __init__(self, board, max_display, qboard, board_id):
        super().__init__(board,max_display,board_id)
        self.queue = qboard
        self.board = board
        self.id = board_id
    
    """
    Dequeues students from the TA board
       @param student_id: student's index in the queue
    """
    def dequeue(self, scene, student_id):
        if self.size <= 0:
            print("queue empty!")
            return
        for i in range(student_id - self.start_display,len(self.display_objects)):
            if i + self.start_display < self.size - 1:
                scene.update_object(self.display_objects[i][0], text = self.q[self.start_display+i+1][1])
        student =  self.q.pop(student_id)
        self.size -= 1
        if self.size < self.display_amt-1:
            self.end_display -= 1
            scene.delete_object(self.display_objects[len(self.display_objects)-1][0])
            scene.delete_object(self.display_objects[len(self.display_objects)-1][1])
            self.display_objects.pop(len(self.display_objects)-1)
        return student[0]

    def display(self):   
        for i in range(len(self.display_objects)): 
            scene.update_object(self.display_objects[i][0],position=Position(-1.5, .25 + spacing*i, 0))
            scene.update_object(self.display_objects[i][1],position=Position(-1.2, .25 + spacing*i, .45),scale=Scale(.05,.05,.025))

    #Add student to TA Board
    def add_to_queue(self,student,question):
        #insert tuple containing (student, question, button to dequeue student)
        if len(self.display_objects) < self.display_amt-1:
            self.display_objects.append([
                Text(object_id =self.id+str(self.size), text=question, rotation=Rotation(0,270,0), scale=Scale(.25,.25,0.25), parent=self.board),
                Cylinder(object_id=self.id+button_id+str(len(self.display_objects)), rotation=Rotation(0,0,90), parent= self.board)]
            )
        self.insert([student, question+str(self.size)])
        


"""
Qboard object
   Saves object_ids of students when they put their questions on the queue
   @param scene: scene to display
   @param board: board object to display on
   @param max_display: max students to display at a time

"""
class QBoard(DisplayBoard):
    def __init__(self, board, max_display):
        super().__init__(board, max_display, "queue")
        self.TABoards = []
        self.board = board
        self.ta_id = "ta"
        #button for enqueuing students
        self.add_button = Cylinder(object_id="my_button", position=Position(.1,3.3,-1.5),scale=Scale(.1,.05,0.1),rotation=Rotation(0,0,90), persist=True)
       
    def show_board(self,scene):
        super().show_board(scene)
        scene.add_object(self.add_button)
    """
    !By storing the Text object, we run into the issue where the first or last item displayed on the queue overlaps with the new questions to be displayed 
    !The current work around is to instead store the text and update upto max_display_amount objects when scrolling. This change might cause a little lag.
    def add_to_queue(self,student,question):
        self.insert(
            (student,
            Text(object_id ="my_text"+str(self.size), text=student+str(self.size), rotation=Rotation(0,270,0), scale=Scale(.25,.25,0.25), parent=self.board)
            ))
        for board in self.TABoards:
            board.add_to_queue(student,question)
            board.display()"""

    #Stores only the text of the students' questions
    def add_to_queue(self,student,question):
        on_display = False
        if len(self.display_objects) < self.display_amt-1:
            on_display = True
            self.display_objects.append([Text(object_id ="my_text"+str(self.size), text=question, rotation=Rotation(0,270,0), scale=Scale(.25,.25,0.25), parent=self.board, persist=True)])
        self.insert([student, question+str(self.size), on_display])
        for board in self.TABoards:                     #update TABoards
            board.add_to_queue(student,question)
            board.display()

    #link multiple TABoards to the QBoard
    #@param ta_boards: list of TA Board objects to be created
    def add_ta_board(self, ta_boards, queue):
        for i in range(len(ta_boards)):
            ta_board = TABoard(ta_boards[i], max_display_amount, queue, self.ta_id + str(i))
            self.TABoards.append(ta_board)
     
    def delete_ta_board(self):
        #TODO: delete ta board
        pass
    
    #Removes specfied student from the queue and returns that student
    def dequeue(self, scene, student_id):
        if self.size <= 0:
            print("queue empty!")
            return
        for board in self.TABoards:
            board.dequeue(scene, student_id)
        if self.q[student_id][2]: #if the question is currently on display
            #Updates the text of each object following the student that got removed to the text of the student after him/her 
            for i in range(student_id - self.start_display,len(self.display_objects)):
                if i + self.start_display < self.size - 1:
                    scene.update_object(self.display_objects[i][0], text = self.q[i+1+self.start_display][1])                    
                    self.q[i+1+self.start_display][2] = True
        else:
            if student_id < self.start_display:
                self.start_display -= 1
                self.end_display -= 1
        student = self.q.pop(student_id)
        self.size -= 1
        if self.size < self.display_amt-1:
            self.end_display -= 1
            scene.delete_object(self.display_objects[len(self.display_objects)-1][0])
            self.display_objects.pop(len(self.display_objects)-1)
        return student[0]

    def display(self):       
        display_list = self.get_display_list()
        for i in range(len(self.display_objects)): 
            scene.add_object(self.display_objects[i][0])
            scene.update_object(self.display_objects[i][0],position=Position(-1.5, .25 + spacing*i, 0))

    def enable_scrolling(self, scene):
        super().enable_scrolling(scene)
        for board in self.TABoards:
            board.enable_scrolling(scene)

    def show_board(self, scene):
        super().show_board(scene)
        for board in self.TABoards:
            board.show_board(scene)


#create global main queue 
queue = QBoard(Box(object_id="my_shape", position=Position(.25,4,-3),scale=board_size, persist=True), 
               max_display_amount)
#link TA boards to main queue
queue.add_ta_board([taB, taB2], queue)

#Teleports camera id of student to Position ta_position
def teleport(ta_position, student):
    for user in scene.users.values():
        if user.object_id == student:
            scene.manipulate_camera(
                user,
                position= ta_position
            ) 

@scene.run_once
def setup():
    queue.show_board(scene)
    scene.add_object(ta_label)
    scene.add_object(queue_label)


@scene.run_forever(interval_ms=100)
def main():
    global queue
    global scene
    global taBoard

    #add student to main queue and TA boards
    def enqueue_mouse_handler(scene, evt, msg):
        if evt.type == "mousedown" and evt['data']['position'].distance_to(evt['data']['clickPos']) < 7:
            queue.add_to_queue(msg["data"]["source"], msg["data"]["source"])
            queue.display()

    #remove student from main queue and TA boards
    def dequeue_mouse_handler(scene, evt, msg):
        if evt.type == "mousedown":
            if evt['data']['position'].distance_to(evt['data']['clickPos']) < 7:
                #extracts which board was pressed, but will need to adjust if len(TABoards) > 9
                board_num = int(evt['object_id'][len(ta_id)])
                #extracts which button was pressed, but will need to adjust if max_display_amount > 9
                button_num = int(evt['object_id'][len(ta_id)+1+len(button_id)])
                student_id  = queue.TABoards[board_num].start_display + button_num
                student = queue.dequeue(scene, student_id)
                teleport(taPos, student)                    #for testing purposes
                #teleport(evt['data']['position'],student)  <-- uncomment to teleport student to TA
    
    #enable scrolling for queue and TA boards
    queue.enable_scrolling(scene)
    scene.update_object(queue.add_button, click_listener=True, evt_handler=enqueue_mouse_handler)
    
    #enable dequeuing buttons on the TA boards
    for board in queue.TABoards:
        for button in board.display_objects:
            scene.update_object(button[1], click_listener=True, evt_handler=dequeue_mouse_handler)

scene.run_tasks()

