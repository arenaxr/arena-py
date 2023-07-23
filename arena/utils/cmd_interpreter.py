# A simple command interpreter to inspect/manipulate arena programs from the cli
import cmd, sys, json, threading, asyncio

class ArenaCmdInterpreter(cmd.Cmd):
    intro = 'Type help or ? to list available commands.\n'
    prompt = '# '
    file = None

    __show_keywords =  ('scene', 'users', 'auth', 'all_objects', 'msg_io')
    __get_keywords =  ('persisted_objs', 'persisted_scene_option', 'writable_scenes', 'user_list')

    def __serialize_obj(self, obj):
        if isinstance(obj, datetime):
            return str(obj)
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        raise TypeError("Type not serializable")
    
    def __init__(self, scene):
        super().__init__(completekey='tab')
        self._scene = scene

    def __cmd_loop_thread(self):
        self.cmdloop()
        
    def start(self):
        t = threading.Thread(name='interpreter_thread', target=self.__cmd_loop_thread)
        t.start()
    
    def do_show(self, arg):
        if arg not in self.__show_keywords:
            self.help_show()
            return            
        try:
            obj = getattr(self._scene, arg)
        except AttributeError:
            obj = {}            
        print(json.dumps(obj, indent=4, sort_keys=True, default=self.__serialize_obj))

    def help_show(self):
        print(f"Display scene attributes: {[i for i in self.__show_keywords]}")

    def do_get(self, arg):
        if arg not in self.__get_keywords:
            self.help_get()
            return     
        try:       
            scene_get = getattr(self._scene, f"get_{arg}")
        except AttributeError:
            return
        if callable(scene_get):
            print(scene_get(self._scene))
    
    def help_get(self):
        print(f"Scene get_* methods: {[i for i in self.__get_keywords]}. E.g:\n")
        print("\tget persisted_objs => returns all persisted objects in the scene (by executing scene.get_persisted_objs)\n")
        
    def _task_exit(self, loop):
        loop.stop()
        
    def do_exit(self, arg):
        answer = ""
        while answer not in ["y", "n"]:
            answer = input("This will terminate the ARENA program. Are you sure [Y/N]? ").lower()
        if answer == "y":
            print("Exiting...")
            tasks = [task for task in asyncio.all_tasks()]
            list(map(lambda task: task.cancel(), tasks))
                
            sys.exit()

    def do_quit(self, arg):
        self.do_exit(arg)

    def help_exit(self):
        print("Exit program.")

    def help_quit(self):
        self.help_exit()