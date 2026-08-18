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


def _is_deprecated_accessor(accessor):
    """True for a property getter/setter marked by the @deprecated decorator."""
    return getattr(accessor, "__arena_deprecated__", None) is not None


def _deprecated_keys(cls):
    """The names cls declares as @deprecated properties, its bases' included.

    Computed once per class, when the class is created, so that dict-style access
    costs a set lookup rather than a descriptor lookup on every read and write.
    """
    names = set()
    for base in cls.__bases__:
        names |= getattr(base, "_arena_deprecated_keys", frozenset())
    for name, value in cls.__dict__.items():
        if isinstance(value, property) and (
            _is_deprecated_accessor(value.fget) or _is_deprecated_accessor(value.fset)
        ):
            names.add(name)
        else:
            # a name redefined as anything else is no longer a deprecated property
            names.discard(name)
    return frozenset(names)


class BaseObject(object):
    """
    Basic Building Block for everything in arena-py.
    Can easily be interpreted and used like a JSON-able Python dictionary.
    """

    # Names this class declares as @deprecated properties; dict-style access reaches
    # exactly these and nothing else. See __getitem__.
    _arena_deprecated_keys = frozenset()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._arena_deprecated_keys = _deprecated_keys(cls)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return str(vars(self))

    def __getitem__(self, name):
        """Reads an attribute of this object with dict-style access.

        A key stored on the instance always wins, so a deprecated key that arrived on
        the wire still reads back as the value that arrived. Only when the key is
        absent, and only when the class declares that name as a @deprecated property,
        is the property consulted, so that dict-style access reports the same
        deprecation attribute-style access already reports. Any other missing key
        raises KeyError, including a non-deprecated property and a key that is not a
        string at all.

        Presence checks are deliberately not extended the same way: `obj["source"]`
        can warn and return the deprecated property's value while `"source" in obj`
        stays False. `__contains__` is used throughout the library as a JSON-shape
        check, so a declared-but-absent key must not report as present there.
        """
        try:
            return self.__dict__[name]
        except KeyError:
            if name in type(self)._arena_deprecated_keys:
                try:
                    return getattr(self, name)
                except AttributeError as exc:
                    # A failed lookup is a KeyError for dict-style access, whatever
                    # the getter raised; the original is kept in the traceback chain.
                    raise KeyError(name) from exc
            raise

    def __setitem__(self, name, attr):
        """Writes an attribute of this object with dict-style access.

        A name the class declares as a @deprecated property is routed through the
        property, so that writing it warns and does exactly what the attribute-style
        write does. Every other name is stored as before.
        """
        if name in type(self)._arena_deprecated_keys:
            setattr(self, name, attr)
            return
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
