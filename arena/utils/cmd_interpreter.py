"""
The ArenaCmdInterpreter is a simple line-oriented command interpreter that
allows to inspect library/program state. It looks at :envvar:`ENABLE_INTERPRETER` 
to enable the interpreter. 

The :class:`.ArenaCmdInterpreter` receives a :class:`.Scene` instance and provides commands
to inspect attributes and execute functions (callables) given to the constructor.

The commands available are:
  show: displays attributes
  info: excutes scene functions that output information
  help: displays the commands available
  exit: terminates the program
  
"""

import cmd, os, json, asyncio, threading, time
from datetime import date, datetime
from ..env import (
    ENABLE_INTERPRETER,
    _get_env
)

class ArenaCmdInterpreter(cmd.Cmd):
    intro = 'Welcome to the arena-py console. Type help or ? to list available commands.\n'
    prompt = '# '
    file = None

    def __serialize_obj(self, obj):
        if isinstance(obj, (datetime, date)):
            return str(obj)
        if hasattr(obj, '__dict__'):
            return {k: v for k, v in vars(obj).items() if k.startswith("_") == False} # ignore private members
        raise TypeError("Type not serializable")

    def __init__(self, scene, show_attrs=('config_data', 'scene', 'users', 'all_objects', 'msg_io'), get_callables=('persisted_objs', 'persisted_scene_option', 'writable_scenes', 'user_list'), start_cmd_event=None):
        self.enable_interp = _get_env(ENABLE_INTERPRETER).lower() in ('true', '1', 't')
        if not self.enable_interp: return
        super().__init__(completekey='tab')
        self._scene = scene
        self._show_attrs = show_attrs
        self._get_callables = get_callables
        
        # start interpreter thread
        t = threading.Thread(name='interpreter_thread', target=self.__cmd_loop_thread, args=(start_cmd_event,))
        t.start()

    def __cmd_loop_thread(self, start_cmd_event):
        if start_cmd_event: start_cmd_event.wait(5) # try to start cmd last; wait on event with timeout
        self.cmdloop()

    def do_show(self, arg):
        if arg not in self._show_attrs:
            self.help_show()
            return
        try:
            obj = getattr(self._scene, arg)
        except AttributeError:
            print(f"Could not find attr {arg}")
            return

        print(json.dumps(obj, indent=4, sort_keys=True, default=self.__serialize_obj))

    def help_show(self):
        print(f"Display scene attributes: {[i for i in self._show_attrs]}")

    def do_get(self, arg):
        if arg not in self._get_callables:
            self.help_get()
            return
        try:
            scene_get = getattr(self._scene, f"get_{arg}")
        except AttributeError:
            print(f"Could not find attr get_{arg}")
            return

        try:
            if callable(scene_get):
                print(scene_get())
        except Exception as e:
            print(e)

    def help_get(self):
        print(f"Scene get_* methods: {[i for i in self._get_callables]}. E.g:\n")
        print("\tget persisted_objs => returns all persisted objects in the scene (by executing scene.get_persisted_objs)\n")

    def do_exit(self, arg):
        answer = ""
        while answer not in ["y", "n"]:
            answer = input("This will terminate the ARENA program. Are you sure [Y/N]? ").lower()
        if answer == "y":
            print("Exiting...")
            self._scene.exit(0)

        return True

    def help_exit(self):
        print("Exit program.")
