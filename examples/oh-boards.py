from arena import *
import math

scene = Scene(host="arenaxr.org", realm="realm", scene="example")

taPos = Position(-10,0,-10)     #TA position to teleport to for testing purposes
board_size = Scale(.25,2,4)     #Size of boards
max_display_amount = 4          #Amount of questions to display on the queue

#Base identifiers to prevent overwriting objects
ta_id = "ta"
button_id = "button_"

#TA board label
text = Text(
    object_id ="label", 
    text="TA BOARDS", 
    position=Position(.25,6,4), 
    rotation=Rotation(0,270,0))

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
   @qboard: the main QBoard that students can submit questions
   @board_id: a unique identifier for the board

"""
class DisplayBoard(Object):
    def __init__(self,scene, board, max_display):
        self.start_display = 0                    
        self.end_display = 0
        self.display_amt = max_display + 1
        self.q = []                           #queue to hold students' questions
        self.size = 0
        self.board= board

    def insert(self, item):
        self.q.append(item)
        self.size += 1 
        if self.size < self.display_amt:
            self.end_display += 1
    """
    Dequeues students from the displayboard
       @param student_id: offset of student's index in the queue from start_display
    """
    def dequeue(self, student_id):
        if self.size <= 0:
            print("queue empty!")
            return
        student =  self.q.pop(self.start_display + student_id)
        self.size -= 1
        if self.size < self.display_amt:
            self.end_display -= 1
        return student

    def scroll_up(self):
        if self.start_display == 0 and (self.end_display - self.start_display < self.display_amt):
            print("at top!")
            return
        self.start_display -= 1
        self.end_display -= 1

    def scroll_down(self):
        if self.end_display == self.size and (self.end_display - self.start_display < self.display_amt):
            print("at bottom!")
            return
        self.start_display += 1
        self.end_display += 1

    def get_display_list(self):
        return self.q[self.start_display:self.end_display]


"""
TABoard object
   Shows students' questions with button to dequeue individual questions
   if the button is pressed then student teleports to the TA)
   @param scene: scene to display
   @param board: board object to display on
   @param max_display: max students to display at a time
   @qboard: the main QBoard that students can submit questions
   @board_id: a unique identifier for the board

   TODO: Add scrolling to TA Boards

"""
class TABoard(DisplayBoard):
    def __init__(self,scene, board, max_display, qboard, board_id):
        super().__init__(scene,board,max_display)
        self.queue = qboard
        self.board = board
        self.id = board_id
        
    #Removes student from the TABoard, and returns that student
    def dequeue(self, scene, student_id):
        if self.size <= 0:
            print("queue empty!")
            return
        for i in range(self.start_display + student_id,self.size-1):
            scene.update_object(self.q[i][1], text = self.q[i+1][1]['data']['text'])

        student =  self.q.pop(self.size-1)
        scene.delete_object(student[1])
        scene.delete_object(student[2])
        self.size -= 1
        if self.size < self.display_amt:
            self.end_display -= 1
        return student[0]

    def display(self):   
        display_list = self.get_display_list()
        for i in range(len(display_list)): 
            scene.update_object(display_list[i][1],position=Position(-1.5, .25 -0.2*i, 0))
            scene.update_object(display_list[i][2],position=Position(-1.2, .25 -0.2*i, .45),scale=Scale(.05,.05,.1*.25))
    
    
    #Add student to TA Board
    def add_to_queue(self,student,question):
        #insert tuple containing (student, student id (later change to question), button to dequeue student)
        self.insert(
                     (student,
                     Text(object_id =self.id+str(self.size), text=question+str(self.size), rotation=Rotation(0,270,0), scale=Scale(.25,.25,0.25), parent=self.board),
                     Cylinder(object_id=self.id+button_id+str(self.size), rotation=Rotation(0,0,90), parent= self.board), self.size)
                     )


"""
Qboard object
   - Saves object_ids of students when they put their questions on the queue
   - Top left buttons are for scrolling
   - Bottom right button adds object_ids
   @param scene: scene to display
   @param board: board object to display on
   @param max_display: max students to display at a time

"""
class QBoard(DisplayBoard):
    def __init__(self,scene, board, max_display):
        super().__init__(scene,board, max_display)
        self.TABoards = []
        self.display_objects = []
        self.board = board
        #button for enqueuing students
        self.add_button = Cylinder(object_id="my_button", position=Position(.1,3.3,-1.5),scale=Scale(.1,.05,0.1),rotation=Rotation(0,0,90), persist=True)
        #button for scrolling up
        self.up_button = Cylinder(object_id="up_button", position=Position(.1,4.7,-4.7),scale=Scale(.1,.05,0.1),rotation=Rotation(0,0,90), persist=True)
        #button for scrolling down
        self.down_button = Cylinder(object_id="down_button", position=Position(.1,4.5,-4.7),scale=Scale(.1,.05,0.1),rotation=Rotation(0,0,90), persist=True)


    #!By storing the Text object, we run into the issue where the first or last item displayed on the queue overlaps with the new questions to be displayed 
    #!The current work around is to instead store the text and update upto max_display_amount objects when scrolling
    #!This change might be causing a little lag though
    """
    def add_to_queue(self,student,question):
        self.insert(
            (student,
            Text(object_id ="my_text"+str(self.size), text=student+str(self.size), rotation=Rotation(0,270,0), scale=Scale(.25,.25,0.25), parent=self.board)
            ))
        for board in self.TABoards:
            board.add_to_queue(student,question)
            board.display()"""
    def add_to_queue(self,student,question):
        if len(self.display_objects) < self.display_amt-1:
            self.display_objects.append(Text(object_id ="my_text"+str(self.size), text=question+str(self.size), rotation=Rotation(0,270,0), scale=Scale(.25,.25,0.25), parent=self.board))
        self.insert((student, question+str(self.size))) #second arguement will eventually be the question
        for board in self.TABoards:                     #update TABoards
            board.add_to_queue(student,question)
            board.display()

    #link multiple TABoards to the QBoard
    def add_ta_board(self, ta_board):
        self.TABoards.append(ta_board)
     
    def delete_ta_board(self):
        #TODO: delete ta board
        pass
    
    #Removes specfied student from the queue and returns that student
    def dequeue(self, scene, student_id):
        if self.size <= 0:
            print("queue empty!")
            return
        #Updates the text of each object following the student that got removed to the text of the student after him/her 
        for i in range(student_id,len(self.display_objects)-1):
            scene.update_object(self.display_objects[i], text = self.q[i+1][1])
        student =  self.q.pop(self.size-1)
        self.size -= 1
        if self.size < self.display_amt-1:
            self.end_display -= 1
            scene.delete_object(self.display_objects[len(self.display_objects)-1])
        return student[0]
    
    def display(self):       
        display_list = self.get_display_list()
        for i in range(0,len(self.display_objects)): 
            scene.update_object(self.display_objects[i],position=Position(-1.5, .25 -0.1*i, 0))

    def scroll_up(self):
        super().scroll_up()
        display_list = self.get_display_list()
        for i in range(0,len(self.display_objects)): 
            scene.update_object(self.display_objects[i],text=display_list[i][1])

    def scroll_down(self):
        super().scroll_down()
        display_list = self.get_display_list()
        for i in range(0,len(self.display_objects)): 
            scene.update_object(self.display_objects[i],text=display_list[i][1])


#create global main queue 
queue = QBoard(scene,
               Box(object_id="my_shape", position=Position(.25,4,-3),scale=board_size, persist=True), 
               max_display_amount)
#create two TA boards
taBoard = TABoard(scene, taB, max_display_amount, queue, ta_id + "0")
taBoard2 = TABoard(scene, taB2, max_display_amount, queue, ta_id + "1")

#link TA boards to main queue
queue.add_ta_board(taBoard)
queue.add_ta_board(taBoard2)

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
    scene.add_object(queue.add_button)
    scene.add_object(queue.up_button)
    scene.add_object(queue.down_button)
    scene.add_object(queue.board)
    scene.add_object(taBoard.board)
    scene.add_object(taBoard2.board)
    scene.add_object(text)

@scene.run_forever(interval_ms=100)
def main():
    global queue
    global scene
    global taBoard

    #add student to main queue and TA boards
    def enqueue_mouse_handler(scene, evt, msg):
        if evt.type == "mousedown" and evt['data']['position'].distance_to(evt['data']['clickPos']) < 7:
            print("adding ", msg["data"]["source"])
            queue.add_to_queue(msg["data"]["source"], msg["data"]["source"])
            queue.display()

    #remove student from main queue and TA boards
    def dequeue_mouse_handler(scene, evt, msg):
        if evt.type == "mousedown":
            if evt['data']['position'].distance_to(evt['data']['clickPos']) < 7:
                student_id = evt['object_id'][len(ta_id)+1+len(button_id)]
                student = queue.dequeue(scene, int(student_id))
                for board in queue.TABoards:
                    board.dequeue(scene, int(student_id))
                teleport(taPos, student)                    #for testing purposes
                #teleport(evt['data']['position'],student)  <-- uncomment to teleport student to TA
    
    def scroll_up_mouse_handler(scene, evt, msg):
        if evt.type == "mousedown" and evt['data']['position'].distance_to(evt['data']['clickPos']) < 7:
            queue.scroll_up()
            
    def scroll_down_mouse_handler(scene, evt, msg):
        if evt.type == "mousedown" and evt['data']['position'].distance_to(evt['data']['clickPos']) < 7:
            queue.scroll_down()
    
    #enable buttons
    scene.update_object(queue.up_button, click_listener=True, evt_handler= scroll_up_mouse_handler)
    scene.update_object(queue.down_button, click_listener=True, evt_handler=scroll_down_mouse_handler)
    scene.update_object(queue.add_button, click_listener=True, evt_handler=enqueue_mouse_handler)
    
    #enable dequeuing buttons on the TA boards
    for button in (taBoard.get_display_list()):
        scene.update_object(button[2], click_listener=True, evt_handler=dequeue_mouse_handler)

scene.run_tasks()

