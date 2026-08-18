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
    """The names cls exposes as @deprecated properties, as (readable, writable).

    A name is *readable* dict-style when its getter is deprecated, so that dict-style
    reads reach exactly the names an attribute-style read would report as deprecated,
    and nothing wider: a property whose getter is not deprecated stays invisible to
    dict access even when its setter is deprecated. A name is *writable* through the
    property when either accessor is deprecated, so that a dict-style write always
    does what the attribute-style write does instead of silently storing a key the
    property would have handled.

    The walk goes over the reversed MRO, so the definition attribute lookup actually
    resolves - the first one in normal MRO order - is the one that decides. Unioning
    the direct bases' results instead would let a base that still carries the
    deprecated property re-add a name that an earlier base in the MRO has replaced
    with something else, and dict access would then answer with that replacement.

    Computed once per class, when the class is created, so that dict-style access
    costs a set lookup rather than a descriptor lookup on every read and write.
    """
    readable = set()
    writable = set()
    for ancestor in reversed(cls.__mro__):
        for name, value in ancestor.__dict__.items():
            deprecated_getter = deprecated_setter = False
            if isinstance(value, property):
                deprecated_getter = _is_deprecated_accessor(value.fget)
                deprecated_setter = _is_deprecated_accessor(value.fset)
            # The definition that wins the MRO decides, whatever it is: a name
            # redefined as anything else is no longer a deprecated property.
            (readable.add if deprecated_getter else readable.discard)(name)
            (writable.add if deprecated_getter or deprecated_setter else writable.discard)(name)
    return frozenset(readable), frozenset(writable)


class BaseObject(object):
    """
    Basic Building Block for everything in arena-py.
    Can easily be interpreted and used like a JSON-able Python dictionary.
    """

    # Names this class exposes as @deprecated properties: the ones dict-style reads
    # reach (getter deprecated), and the ones dict-style writes route through the
    # property (either accessor deprecated). See __getitem__ and __setitem__.
    _arena_deprecated_read_keys = frozenset()
    _arena_deprecated_write_keys = frozenset()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._arena_deprecated_read_keys, cls._arena_deprecated_write_keys = _deprecated_keys(cls)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return str(vars(self))

    def __getitem__(self, name):
        """Reads an attribute of this object with dict-style access.

        A key stored on the instance always wins, so a deprecated key that arrived on
        the wire still reads back as the value that arrived. Only when the key is
        absent, and only when the class exposes that name as a property with a
        @deprecated getter, is the property consulted, so that dict-style access
        reports the same deprecation attribute-style access already reports. Any
        other missing key raises KeyError, including a property whose getter is not
        deprecated and a key that is not a string at all.

        Presence checks are deliberately not extended the same way: `obj["source"]`
        can warn and return the deprecated property's value while `"source" in obj`
        stays False. `__contains__` is used throughout the library as a JSON-shape
        check, so a declared-but-absent key must not report as present there.
        """
        try:
            return self.__dict__[name]
        except KeyError:
            if name in type(self)._arena_deprecated_read_keys:
                try:
                    return getattr(self, name)
                except AttributeError as exc:
                    # A failed lookup is a KeyError for dict-style access, whatever
                    # the getter raised; the original is kept in the traceback chain.
                    raise KeyError(name) from exc
            raise

    def __setitem__(self, name, attr):
        """Writes an attribute of this object with dict-style access.

        A name the class exposes as a @deprecated property - deprecated getter,
        deprecated setter, or both - is routed through the property, so that writing
        it does exactly what the attribute-style write does, warning where the
        attribute-style write warns and refusing where it refuses. Storing such a
        name directly instead would put a key in the instance dict that the property
        was meant to handle, and ship it in json(). Every other name is stored as
        before.
        """
        if name in type(self)._arena_deprecated_write_keys:
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
