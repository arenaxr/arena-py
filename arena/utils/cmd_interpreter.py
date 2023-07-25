# A simple command interpreter 

import cmd, os, json, asyncio
from datetime import date, datetime
class ArenaCmdInterpreter(cmd.Cmd):
    intro = 'Type help or ? to list available commands.\n'
    prompt = '# '
    file = None

    def __serialize_obj(self, obj):
        if isinstance(obj, (datetime, date)):
            return str(obj)
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        raise TypeError("Type not serializable")
    
    def __init__(self, scene, show_attrs=('config_data', 'scene', 'users', 'auth', 'all_objects', 'msg_io'), get_callables=('persisted_objs', 'persisted_scene_option', 'writable_scenes', 'user_list')):
        super().__init__(completekey='tab')
        self._scene = scene
        self._show_attrs = show_attrs
        self._get_callables = get_callables

    # cmd loop; must externally setup a task/thread to run this
    def cmd_loop_task(self):
        self.cmdloop()
    
    def do_show(self, arg):
        if arg not in self._show_attrs:
            self.help_show()
            return            
        try:
            obj = getattr(self._scene, arg)
        except AttributeError:
            obj = {}            
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
            return
        if callable(scene_get):
            print(scene_get(self._scene))
    
    def help_get(self):
        print(f"Scene get_* methods: {[i for i in self._get_callables]}. E.g:\n")
        print("\tget persisted_objs => returns all persisted objects in the scene (by executing scene.get_persisted_objs)\n")
                
    def do_exit(self, arg):
        answer = ""
        while answer not in ["y", "n"]:
            answer = input("This will terminate the ARENA program. Are you sure [Y/N]? ").lower()
        if answer == "y":
            print("Exiting...")
            loop = asyncio.get_event_loop()
            loop.stop()
            os._exit(0)
        
        return True
            
    def do_quit(self, arg):
        return self.do_exit(arg)

    def help_exit(self):
        print("Exit program.")

    def help_quit(self):
        self.help_exit()