import uuid

from ..base_object import *
from ..attributes import Animation, Data, Position, Rotation, Scale, ATTRIBUTE_KEYWORD_TRANSLATION
from ..utils import *


class Object(BaseObject):
    """
    Object class. Defines a generic object in the ARENA.
    """

    type = "object"
    object_type = "entity"
    all_objects = {} # dict of all objects created so far
    private_objects = {} # dict of all private objects created so far

    # Bounds for cascaded orphan reaping, see remove_descendants(). The scene graph
    # is only defined by free-form "parent" strings, so a malformed scene can nest
    # arbitrarily deep or wide; these caps keep a single delete from stalling the
    # message loop, and reaping stops with a printed warning when either is reached.
    MAX_REAP_DESCENDANTS = 10000 # most descendants dropped for one deleted object
    MAX_REAP_DEPTH = 64 # deepest level of nesting followed below the deleted object

    def __init__(self, evt_handler=None, update_handler=None, **kwargs):
        # "object_id" is required in kwargs, defaulted to random uuid4
        object_id = kwargs.get("object_id", str(uuid.uuid4()))
        if "object_id" in kwargs: del kwargs["object_id"]

        # "persist" is required in kwargs, defaulted to false
        persist = kwargs.get("persist", False)
        if "persist" in kwargs: del kwargs["persist"]

        # special case for "parent" (can be an Object)
        if "parent" in kwargs and isinstance(kwargs["parent"], Object):
            kwargs["parent"] = kwargs["parent"].object_id

        # "ttl" is optional
        ttl = kwargs.get("ttl", None)
        if "ttl" in kwargs: del kwargs["ttl"]

        private = kwargs.get("private", False)
        if "private" in kwargs: del kwargs["private"]

        private_userid = kwargs.get("private_userid", None)
        if "private_userid" in kwargs: del kwargs["private_userid"]

        # remove timestamp, if exists
        if "timestamp" in kwargs: del kwargs["timestamp"]

        # remove "updatedAt", if exists
        if "updatedAt" in kwargs: del kwargs["updatedAt"]

        # remove "action", if exists
        if "action" in kwargs: del kwargs["action"]

        # default "object_type" to entity
        if "object_type" not in kwargs:
            kwargs["object_type"] = Object.object_type

        if "position" not in kwargs:
            kwargs["position"] = Position(0,0,0)

        if "rotation" not in kwargs:
            kwargs["rotation"] = Rotation(0,0,0)

        if "scale" not in kwargs:
            kwargs["scale"] = Scale(1,1,1)

        # print warning if object is being created with the same id as an existing object
        if Object.exists(object_id):
            if not Object.get(object_id).persist:
                print("[WARNING]", f"An object with object_id of {object_id} was already created. The previous object will be overwritten.")
            Object.remove(Object.get(object_id))

        # setup attributes in the "data" field
        data = kwargs.get("data", kwargs)
        data = Data(**data)
        super().__init__(
                object_id=object_id,
                type=Object.type,
                persist=persist,
                data=data
            )
        if ttl:
            self.ttl = ttl

        # This is with regard to its interaction
        if private:
            # Note: public objects *can* have private clicks, mouseover, etc.
            self.private = private

        if private_userid:
            self._private_userid = private_userid  # None is public
            self.private = True # private objects are always private interaction

        self.evt_handler = Object._checked_handler("evt_handler", evt_handler)
        self.update_handler = Object._checked_handler("update_handler", update_handler)
        self.animations = []

        # add current object to all_objects dict
        Object.add(self)
        # If private, add to private_objects dict
        if private_userid:
            Object.add_private(self)

        self.delayed_prop_tasks = {}  # dict of delayed property tasks

    @staticmethod
    def _checked_handler(name, handler):
        """Returns handler if it can be called back, otherwise None.

        evt_handler and update_handler are local-only fields: json_preprocess
        strips them on the way out, so they never legitimately appear on the
        wire in either direction. But Scene.process_message reaches both
        __init__ and update_attributes with the raw inbound payload, so without
        this a top-level "evt_handler" in a create or update message would bind
        on any object this client knows -- a remote sender silencing that
        object's events for the life of the process.

        json.loads cannot produce a callable, so requiring one here leaves the
        documented contract true no matter who called: a value a remote sender
        can send is rejected outright, never coerced or stored.

        Event.__init__ guards its own local-only "object" field at the same
        parsing boundary, but not with the same test or the same disposition: it
        keeps the value only when isinstance(_object, Object) holds and
        substitutes None silently, None being that field's documented answer for
        "nothing was resolved". A handler has no equivalent neutral value, so
        this tests callable() instead and warns as it drops the value, rather
        than coercing quietly.
        """
        if handler is None or callable(handler):
            return handler
        print("[WARNING]", f"Ignoring non-callable {name} of type {type(handler).__name__}; handlers must be callable.")
        return None

    def update_attributes(self, evt_handler=None, update_handler=None, **kwargs):
        evt_handler = Object._checked_handler("evt_handler", evt_handler)
        if evt_handler:
            self.evt_handler = evt_handler

        update_handler = Object._checked_handler("update_handler", update_handler)
        if update_handler:
            self.update_handler = update_handler

        if "data" not in self:
            return

        if "persist" in kwargs:
            self.persist = kwargs.pop("persist")

        if "ttl" in kwargs:
            self.ttl = kwargs.pop("ttl")

        private_given = "private" in kwargs
        if private_given:
            self.private = kwargs.pop("private")

        if "private_userid" in kwargs:
            # Track the value, not the key's presence. __init__ only marks an object
            # private when private_userid is truthy, so update_object(obj,
            # private_userid=None) - the way an object is returned to public - has to
            # undo that marking instead of asserting it. Asserting it published
            # "private": true on the public topic, and left the private_objects entry
            # in place: Object.remove() can no longer find that entry, because the
            # object no longer names its former recipient, so the strong reference the
            # entry holds survived delete_object(), and delete_user_objects() for the
            # former recipient went on to drop a now-public object from all_objects.
            private_userid = kwargs.pop("private_userid")
            previous_userid = getattr(self, "_private_userid", None)
            if previous_userid and previous_userid != private_userid:
                Object.private_objects.get(previous_userid, {}).pop(self.object_id, None)
            self._private_userid = private_userid  # None is public
            if private_userid:
                self.private = True # private objects are always private interaction
                # Index only a recipient the scene already knows about. add_private()
                # raises for an unknown user, which is what construction wants, but
                # would be a new way for an update to fail; an unknown user has no
                # index that could fall out of date anyway.
                if private_userid in Object.private_objects:
                    Object.add_private(self)
            elif not private_given:
                # Drop the flag rather than storing False: an object created public
                # carries no "private" key at all, and add_object()/update_object()
                # read the flag as getattr(obj, "private", True), so storing False
                # would also stop setting program_id. An explicit private= in the
                # same call wins, matching __init__.
                self.__dict__.pop("private", None)

        data = self.data
        Data.update_data(data, kwargs)

        if self.update_handler:
            self.update_handler(self)

    def dispatch_animation(self, animation):
        if isinstance(animation, (tuple, list)):
            self.animations += list(animation)
        elif isinstance(animation, Animation):
            self.animations += [animation]
        return self.animations

    def remove_animation_at_index(self, idx):
        if 0 <= idx < len(self.animations):
            return self.animations.pop(idx)
        return -1

    def clear_animations(self):
        self.animations = []

    @property
    def clickable(self):
        return "click_listener" in self.data or "clickable" in self.data

    def json_preprocess(self, **kwargs):
        # kwargs are for additional param to add to json, like "action":"create"
        # "camera" and "hands" are the back-references Scene maintains between a
        # user and its hands for handler convenience (user.hands[type] = obj;
        # obj.camera = user). They are local state like the rest of this list,
        # they have no place on the wire -- the server pairs a hand with its user
        # through data.dep -- and left in they form a reference cycle that makes
        # json.dumps raise "Circular reference detected" from either end.
        # "hand_found_callback" and "hand_remove_callback" are the other two
        # locals Camera.__init__ sets alongside "hands", and they are local in
        # exactly the same way: handler slots a program fills in, never anything
        # the server reads. Unset they published as null; once set, the encoder
        # falls through to vars() on the function and publishes {}.
        skipped_keys = ["evt_handler", "update_handler", "animations", "delayed_prop_tasks", "_private_userid",
                        "camera", "hands", "hand_found_callback", "hand_remove_callback"]
        json_payload = {k: v for k, v in vars(self).items() if k not in skipped_keys}
        json_payload.update(kwargs)
        return json_payload

    def json_postprocess(self, json_payload, json_data): # to be done by subclasses, if needed
        pass

    def json(self, **kwargs):
        json_data = {}
        json_payload = self.json_preprocess(**kwargs)
        data = vars(json_payload["data"])

        for k,v in data.items():
            if v is None:
                json_data[k] = v

            # color should be a hex string
            elif "color" == k:
                json_data["color"] = v.hex

            elif "material" == k:
                json_data["material"] = vars(v).copy()
                if "color" in v:
                    color = v["color"]
                    json_data["material"]["color"] = color.hex

            # rotation should be in quaternions
            elif "rotation" == k:
                rot = data["rotation"]
                # always publish quaternions on wire format to avoid persist euler->quat merges
                json_data["rotation"] = rot.quaternion

            elif "look_at" == k:
                if isinstance(v, str):
                    json_data["look-at"] = v
                elif isinstance(v, Object):
                    json_data["look-at"] = v.object_id

            # for animation, replace "start" and "end" with "from" and "to"
            elif isinstance(k, str) and "animation" == k[:len("animation")]:
                animation = vars(v).copy()
                Utils.dict_key_replace(animation, "start", "from")
                Utils.dict_key_replace(animation, "end", "to")
                json_data[k] = animation

            # Translate and remove underscores from any other keys.
            # Must be done last since ATTRIBUTE_KEYWORD_TRANSLATION contains all attributes,
            # which may interfere with special casing above from, say "rotation" for example.
            elif k in ATTRIBUTE_KEYWORD_TRANSLATION:
                json_data[ATTRIBUTE_KEYWORD_TRANSLATION[k]] = v

            # allow: likely unknown/misspelled attribute to this library version
            else:
                json_data[k] = v

        json_payload.pop("delayed_prop_tasks", None)

        json_payload["data"] = json_data
        self.json_postprocess(json_payload, json_data)
        return self.json_encode(json_payload)

    # methods for global objects dictionary
    @classmethod
    def get(cls, object_id):
        return Object.all_objects.get(object_id, None)

    @classmethod
    def add(cls, obj):
        object_id = obj.object_id
        Object.all_objects[object_id] = obj

    @classmethod
    def add_private(cls, obj):
        private_userid = getattr(obj, "_private_userid", None)
        if private_userid is None:
            raise ValueError("No private user id specified")
        if private_userid not in Object.private_objects:
            raise ValueError(f"User {private_userid} does not exist")
        Object.private_objects[private_userid][obj.object_id] = obj

    @classmethod
    def remove(cls, obj):
        object_id = obj.object_id
        del Object.all_objects[object_id]
        # Private objects are indexed a second time, per user, by add_private().
        # Dropping only the all_objects entry would leave a strong reference in
        # private_objects, and get_private_objects() would keep handing back
        # objects that are gone from the scene.
        private_userid = getattr(obj, "_private_userid", None)
        if private_userid is not None:
            Object.private_objects.get(private_userid, {}).pop(object_id, None)
        if (hasattr(obj, "delayed_prop_tasks")):
            for task in obj.delayed_prop_tasks.values():  # Cancel all pending tasks
                task.cancel()

    @classmethod
    def remove_descendants(cls, object_id):
        """Removes every descendant of object_id from the local object store.

        The ARENA server publishes a single delete for the object that was actually
        deleted, so each client is responsible for dropping the objects that delete
        orphaned. Returns the list of removed descendant object_ids.
        """
        # Index parent -> children in a single pass over the store, so the walk
        # below never has to re-scan all_objects.
        #
        # Only scene objects are indexed. all_objects also holds records that are
        # not part of the scene graph, such as Program, whose data.parent names
        # the runtime the program should be deployed to. Indexing those would let
        # a scene object whose id happens to match a runtime name reap the
        # program along with its real children. Every renderable type subclasses
        # Object, so an isinstance check keeps new scene objects covered while
        # leaving non-scene records out.
        children_of = {}
        for child in list(cls.all_objects.values()):
            if not isinstance(child, Object):
                continue
            parent = getattr(getattr(child, "data", None), "parent", None)
            if parent:
                children_of.setdefault(parent, []).append(child.object_id)

        removed = []
        # Visited ids terminate cycles and repeated parents in malformed chains.
        # The deleted object counts as visited so a cycle back to it cannot loop.
        visited = {object_id}
        frontier = list(children_of.get(object_id, []))
        depth = 1
        bound_hit = None

        while frontier:
            if depth > cls.MAX_REAP_DEPTH:
                bound_hit = f"MAX_REAP_DEPTH ({cls.MAX_REAP_DEPTH})"
                break
            next_frontier = []
            for child_id in frontier:
                if child_id in visited:
                    continue
                visited.add(child_id)
                if len(removed) >= cls.MAX_REAP_DESCENDANTS:
                    bound_hit = f"MAX_REAP_DESCENDANTS ({cls.MAX_REAP_DESCENDANTS})"
                    break
                child = cls.all_objects.get(child_id)
                if child is not None: # already gone, e.g. a delete raced this one
                    cls.remove(child)
                    removed.append(child_id)
                next_frontier.extend(children_of.get(child_id, []))
            if bound_hit:
                break
            frontier = next_frontier
            depth += 1

        if bound_hit:
            print("[WARNING]", f"Stopped reaping descendants of {object_id} after "
                  f"{len(removed)} objects: hit {bound_hit}. Orphaned descendants "
                  f"may remain in the local scene state.")
        return removed

    @classmethod
    def exists(cls, object_id):
        return object_id in Object.all_objects
