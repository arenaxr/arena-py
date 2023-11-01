import json

class BaseObjectJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for nested BaseObjects.
    """
    def default(self, obj):
        if isinstance(obj, (tuple,list,dict)):
            return obj
        else:
            return vars(obj)

class BaseObject(object):
    """
    Basic Building Block for everything in arena-py.
    Can easily be interpreted and used like a JSON-able Python dictionary.
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return str(vars(self))

    def __getitem__(self, name):
        return self.__dict__[name]

    def __setitem__(self, name, attr):
        self.add(name, attr)

    def __contains__(self, attr):
        return attr in self.__dict__

    def add(self, name, attr):
        self.__dict__[name] = attr

    def json_encode(self, d):
        return json.dumps(d, cls=BaseObjectJSONEncoder)

    def json(self, **kwargs): # kwargs are for additional param to add to json, like "action":"create"
        res = vars(self).copy()
        res.update(kwargs)
        return self.json_encode(res)
