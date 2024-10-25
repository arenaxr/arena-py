from config import *
from display_board import DisplayBoard

from arena import *


class TABoard(DisplayBoard):
    """
    TABoard object
    Shows students' questions with button to dequeue individual questions. If the button is pressed then student teleports to the TA)
    @param scene: scene to display
    @param board: board object to display on
    @qboard: the main QBoard that students can submit questions
    @board_id: a unique identifier for the board
    """
    def __init__(self, scene, board, qboard, board_id):
        super().__init__(scene, board, board_id)
        self.queue = qboard
        self.board = board
        self.id = board_id

    """
    Dequeues students from the TA board
       @param student_id: student's index in the queue
    """
    def dequeue(self, student_id):
        if self.size <= 0:
            print("queue empty!")
            return

        for i in range(student_id - self.start_display,len(self.display_objects)):
            if i + self.start_display < self.size - 1:
                self.scene.update_object(self.display_objects[i][0], text = self.q[self.start_display+i+1][1])

        student = self.q.pop(student_id)

        self.size -= 1
        if self.size < self.display_amt-1:
            self.end_display -= 1
            self.scene.delete_object(self.display_objects[len(self.display_objects)-1][0])
            self.scene.delete_object(self.display_objects[len(self.display_objects)-1][1])
            self.display_objects.pop(len(self.display_objects)-1)

        return student[0]

    def display(self):
        for i in range(len(self.display_objects)):
            self.scene.update_object(
                self.display_objects[i][0],position=Position(-1.5, .25 + SPACING*i, 0))
            self.scene.update_object(
                self.display_objects[i][1],position=Position(-1.2, .25 + SPACING*i, .45),scale=Scale(.05,.05,.025))

    #Add question to TA Board
    def add_to_queue(self,student,question):
        #insert tuple containing (student, question, button to dequeue student)
        if len(self.display_objects) < self.display_amt-1:
            self.display_objects.append([
                Text(
                        object_id=self.id+str(self.size),
                        value=f"[{student.displayName}]: {question}",
                        rotation=Rotation(0,270,0),
                        scale=Scale(.25,.25,.25),
                        parent=self.board
                    ),
                Cylinder(
                        object_id=self.id+BUTTON_ID+str(len(self.display_objects)),
                        rotation=Rotation(0,0,90),
                        parent=self.board
                    )
            ])

        self.insert([student, f"[{student.displayName}]: {question}"])
