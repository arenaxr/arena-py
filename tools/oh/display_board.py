from arena import *
from config import *

class DisplayBoard(Object):
    """
    DisplayBoard object
    Basic queue with scrolling fuctionality and the ability to dequeue students anywhere in the queue
    @param scene: scene to display
    @param board: board object to display on
    @param max_display: max students to display at a time
    @id: a unique identifier for the board
    """
    def __init__(self, scene, board, id, max_display=MAX_DISPLAY_AMOUNT):
        self.scene = scene

        self.start_display = 0
        self.end_display = 0

        self.display_amt = max_display + 1
        self.size = 0

        self.board = board

        #queue to hold students' questions
        self.q = []

        #objects to be displayed in scene
        self.display_objects = []

        #button for scrolling up
        self.up_button = Cylinder(
                            object_id="up_button_"+id,
                            position=Position(-.5,.4,-.4),
                            scale=Scale(.05,.4,.025),
                            rotation=Rotation(0,0,90),
                            persist=True,
                            parent=self.board
                        )
        #button for scrolling down
        self.down_button = Cylinder(
                            object_id="down_button_"+id,
                            position=Position(-.5,.3,-.4),
                            scale=Scale(.05,.4,.025),
                            rotation=Rotation(0,0,90),
                            persist=True,
                            parent=self.board
                        )

    def insert(self, item):
        self.q.append(item)
        self.size += 1
        if self.size < self.display_amt:
            self.end_display += 1

    def get_display_list(self):
        return self.q[self.start_display:self.end_display]

    def scroll_up(self):
        if self.start_display == 0 and (self.end_display - self.start_display < self.display_amt):
            return

        self.start_display -= 1
        self.end_display -= 1
        display_list = self.get_display_list()
        for i in range(len(self.display_objects)):
            self.scene.update_object(self.display_objects[i][0],text=display_list[i][1])

    def scroll_down(self):
        if self.end_display == self.size and (self.end_display - self.start_display < self.display_amt):
            return

        self.start_display += 1
        self.end_display += 1
        display_list = self.get_display_list()
        for i in range(len(self.display_objects)):
            self.scene.update_object(self.display_objects[i][0],text=display_list[i][1])

    ###Scene Setup Functions ###
    def scroll_up_mouse_handler(self, scene, evt, msg):
        if evt.type == "mousedown" and evt['data']['position'].distance_to(evt['data']['clickPos']) < MAX_CLICK_DISTANCE:
            self.scroll_up()

    def scroll_down_mouse_handler(self, scene, evt, msg):
        if evt.type == "mousedown" and evt['data']['position'].distance_to(evt['data']['clickPos']) < MAX_CLICK_DISTANCE:
            self.scroll_down()

    #enable scrolling events
    def enable_scrolling(self):
        self.scene.update_object(
            self.up_button, click_listener=True, evt_handler= self.scroll_up_mouse_handler)
        self.scene.update_object(
            self.down_button, click_listener=True, evt_handler= self.scroll_down_mouse_handler)

    #initialize board in scene
    def show_board(self):
        self.scene.add_object(self.up_button)
        self.scene.add_object(self.down_button)
        self.scene.add_object(self.board)
