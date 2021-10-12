from arena import *
from config import *

from display_board import DisplayBoard
from ta_board import TABoard

class QBoard(DisplayBoard):
    """
    Qboard object
    Saves object_ids of students when they put their questions on the queue
    @param scene: scene to display
    @param board: board object to display on
    """
    def __init__(self, scene, board):
        super().__init__(scene, board, "queue")

        self.TABoards = []
        self.board = board
        self.ta_id = "ta"

        #button for enqueuing students
        self.add_button = Cylinder(
                object_id="add_button",
                position=Position(.1,3.3,-1.5),
                scale=Scale(.1,.05,.1),
                rotation=Rotation(0,0,90),
                color=Color(0,255,0),
                persist=True
            )

    def show_board(self):
        super().show_board(self.scene)
        self.scene.add_object(self.add_button)

    """
    !By storing the Text object, we run into the issue where the first or last item displayed on the queue overlaps with the new questions to be displayed
    !The current work around is to instead store the text and update upto MAX_DISPLAY_AMOUNT objects when scrolling. This change might cause a little lag.
    def add_to_queue(self,student,question):
        self.insert(
            (student,
            Text(object_id ="my_text"+str(self.size), text=student+str(self.size), rotation=Rotation(0,270,0), scale=Scale(.25,.25,.25), parent=self.board)
            ))
        for board in self.TABoards:
            board.add_to_queue(student,question)
            board.display()
    """

    #Stores only the text of the students' questions
    def add_to_queue(self,student,question):
        on_display = False

        if len(self.display_objects) < self.display_amt-1:
            on_display = True
            self.display_objects.append([
                Text(
                    object_id ="student_text"+str(self.size),
                    text=question,
                    rotation=Rotation(0,270,0),
                    scale=Scale(.25,.25,.25),
                    parent=self.board,
                    # align="left",
                    persist=True
                )
            ])

        self.insert([student, question, on_display])

        for board in self.TABoards:                     #update TABoards
            board.add_to_queue(student, question)
            board.display()

    #link multiple TABoards to the QBoard
    #@param ta_boards: list of TA Board objects to be created
    def add_ta_board(self, ta_boards, queue):
        for i in range(len(ta_boards)):
            ta_board = TABoard(self.scene, ta_boards[i], queue, self.ta_id + str(i))
            self.TABoards.append(ta_board)

    def delete_ta_board(self):
        #TODO: delete ta board
        pass

    #Removes specfied student from the queue and returns that student
    def dequeue(self, student_id):
        if self.size <= 0:
            print("queue empty!")
            return

        for board in self.TABoards:
            board.dequeue(self.scene, student_id)

        if self.q[student_id][2]: #if the question is currently on display
            #Updates the text of each object following the student that got removed to the text of the student after him/her
            for i in range(student_id - self.start_display,len(self.display_objects)):
                if i + self.start_display < self.size - 1:
                    self.scene.update_object(self.display_objects[i][0], text = self.q[i+1+self.start_display][1])
                    self.q[i+1+self.start_display][2] = True
        else:
            if student_id < self.start_display:
                self.start_display -= 1
                self.end_display -= 1

        student = self.q.pop(student_id)
        self.size -= 1

        if self.size < self.display_amt-1:
            self.end_display -= 1
            self.scene.delete_object(self.display_objects[len(self.display_objects)-1][0])
            self.display_objects.pop(len(self.display_objects)-1)

        return student[0]

    def display(self):
        display_list = self.get_display_list()
        for i in range(len(self.display_objects)):
            self.scene.add_object(self.display_objects[i][0])
            self.scene.update_object(self.display_objects[i][0],position=Position(-1.5, .25 + SPACING*i, 0))

    def enable_scrolling(self):
        super().enable_scrolling()
        for board in self.TABoards:
            board.enable_scrolling()

    def show_board(self):
        super().show_board()
        for board in self.TABoards:
            board.show_board()
