'''
oh-boards.py
    Demonstrates queue board and TA boards for enqueuing and dequeuing students in OH
    To test, run:
        > python3 oh-boards.py

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

import math
from arena import *

from question_board import QBoard
from config import *

scene = Scene(host="mqtt.arenaxr.org", realm="realm", scene="officehours")

#TA board label
ta_label = Text(
    object_id ="ta_boards_label",
    text="TA Boards",
    position=Position(.25,5.5,4),
    rotation=Rotation(0,270,0),
    persist=True
)

#TA board objects to be displayed
taB = Box(
    object_id="ta_board1",
    position=Position(.25,4,4),
    scale=BOARD_SIZE,
    color=Color(100,200,100),
    persist=True
)
taB2 = Box(
    object_id="ta_board2",
    position=Position(.25,4,8.1),
    scale=BOARD_SIZE,
    color=Color(200,100,100),
    persist=True
)

#create global main queue
qboard_box = Box(
    object_id="qboard",
    position=Position(.25,4,-3),
    scale=BOARD_SIZE,
    color=Color(100,100,200),
    persist=True
)

qboard = QBoard(scene, qboard_box)

#Main Queue label
qboard_label = Text(
    object_id ="qboard_label",
    text="Questions",
    position=Position(.25,5.5,-3),
    rotation=Rotation(0,270,0),
    persist=True
)

#Main queue label
qboard_button_label = Text(
    object_id ="qboard_button_label",
    text="Click to ask a question!",
    position=Position(2,0,0),
    scale=Scale(3,3,3),
    rotation=Rotation(-90,0,-90),
    parent=qboard.add_button,
    persist=True
)

#link TA boards to main queue
qboard.add_ta_board([taB, taB2], qboard)

#Teleports camera id of student to Position ta_position
def teleport(ta_position, student):
    for user in scene.users.values():
        if user.object_id == student:
            scene.manipulate_camera(
                user,
                position=ta_position
            )

@scene.run_once
def setup():
    global qboard
    global scene
    global taBoard

    qboard.show_board()
    scene.add_object(ta_label)
    scene.add_object(qboard_label)
    scene.add_object(qboard_button_label)
    scene.add_object(qboard.add_button)

    #enable scrolling for queue and TA boards
    qboard.enable_scrolling()

    #add student to main queue and TA boards
    def add_student_question(scene, evt, msg):
        if evt.type == "textinput":
            student = scene.all_objects[evt.data.writer]
            qboard.add_to_queue(student, evt.data.text)
            qboard.display()

    #remove student from main queue and TA boards
    def remove_student_question(scene, evt, msg):
        if evt.type == "mousedown" and evt['data']['position'].distance_to(evt['data']['clickPos']) < MAX_CLICK_DISTANCE:
            #extracts which board was pressed, but will need to adjust if len(TABoards) > 9
            board_num = int(evt['object_id'][len(ta_id)])
            #extracts which button was pressed, but will need to adjust if MAX_DISPLAY_AMOUNT > 9
            button_num = int(evt['object_id'][len(ta_id)+1+len(BUTTON_ID)])
            student_id  = qboard.TABoards[board_num].start_display + button_num
            student = qboard.dequeue(student_id)
            teleport(TA_POS, student)                    #for testing purposes
            #teleport(evt['data']['position'],student)  <-- uncomment to teleport student to TA

    #enable dequeuing buttons on the TA boards
    for board in qboard.TABoards:
        for button in board.display_objects:
            scene.update_object(button[1], click_listener=True, evt_handler=remove_student_question)

    #enable adding questions to question board
    scene.update_object(
            qboard.add_button,
            click_listener=True,
            evt_handler=add_student_question,
            textinput=TextInput(
                on="mouseup",
                title="What is your question?",
                label=f"{CLASS_NAME} Office Hours",
                placeholder="Example: what does the volatile keyword do in C?"
            )
        )

def user_join_callback(scene, camera, msg):
    #show a little greeting whenever a user joins OH
    greeting = Text(
        object_id=f"{camera.object_id}_greeting",
        text=f"Hello, Welcome to {CLASS_NAME} Office Hours!\nA TA will be with you shortly.",
        position=Position(0,0.35,-0.7),
        scale=Scale(0.2,0.2,0.2),
        parent=camera,
        ttl=5
    )
    scene.add_object(greeting)

scene.user_join_callback = user_join_callback

scene.run_tasks()
