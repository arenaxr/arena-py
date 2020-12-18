import json

class CustomEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for nested BaseObjects
    """
    def default(self, obj):
        if type(obj) == dict:
            return obj
        else:
            return vars(obj)

class BaseObject(object):
    """
    Basic Building Block for everything in ARENA-py.
    Can easily be interpreted and used like a JSON-able Python dictionary.
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return str(vars(self))

    def __getitem__(self, id):
        return self.__dict__[id]

    def __setitem__(self, id, attr):
        self.add(id, attr)

    def add(self, id, attr):
        self.__dict__[id] = attr

    def json(self, **kwargs): # kwargs are for additional param to add to json, like "action":"create"
        res = {k:v for k,v in vars(self).items() if k != "evt_handler"}
        res.update(kwargs)
        return json.dumps(res, cls=CustomEncoder)
