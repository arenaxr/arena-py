"""Dict-style writes work on an Object, and Object.add stays what it was.

BaseObject advertises itself as usable "like a JSON-able Python dictionary" and
BaseObject.__setitem__ delegated the store to `self.add(name, attr)`. Object
also defines `add`, but as a classmethod registry - `Object.add(cls, obj)`,
which inserts into Object.all_objects - so on every Object the classmethod
shadowed the instance method and every dict-style write raised
`TypeError: Object.add() takes 2 positional arguments but 3 were given`.

Reads were unaffected, because __getitem__ goes straight to self.__dict__,
which is what made the asymmetry easy to miss.

These tests pin both halves: dict-style writes store the way __getitem__ reads,
and the registry classmethod still behaves exactly as before, since Object.add
is public API and renaming it is what this fix avoids.

They also re-pin the routing PR #248 added, because that ran through the same
line: a name declared as a @deprecated property still goes through the property
rather than being stored. A name the class exposes as a plain read-only property
is not routed, so a write to one is stored and the property keeps reporting what
data says -- a deliberate divergence between the two access styles, pinned here
under its own name.

Object.all_objects and Object.private_objects are global class state, so every
test clears them before and after itself to avoid leaking objects into the rest
of the suite.
"""

import inspect
import json
import unittest
import warnings

from arena.attributes.attribute import Attribute
from arena.base_object import BaseObject
from arena.objects import Box, Object, Text


class ObjectDictWriteTestCase(unittest.TestCase):
    def setUp(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    def tearDown(self):
        Object.all_objects.clear()
        Object.private_objects.clear()


class TestDictStyleWritesOnAnObject(ObjectDictWriteTestCase):
    def test_write_of_a_new_key_stores_it(self):
        """The reported case."""
        box = Box(object_id="b", position=(0, 0, 0))
        box["foo"] = 1
        self.assertEqual(1, box["foo"])
        self.assertEqual(1, vars(box)["foo"])

    def test_write_round_trips_through_the_read(self):
        """__getitem__ reads self.__dict__, so __setitem__ has to write it: the
        two access styles must agree about where a plain key lives.

        Only names the class does not expose as a property. A read-only property
        name diverges on purpose -- see
        TestReadOnlyPropertyNamesDiverge below.
        """
        box = Box(object_id="b", position=(0, 0, 0))
        for key, value in (("foo", 1), ("position", 1)):
            with self.subTest(key=key):
                box[key] = value
                self.assertEqual(value, box[key])

    def test_write_addresses_the_top_level_payload_not_data(self):
        """Dict access on an Object reaches the same keys vars(obj) holds, so a
        write lands beside object_id and persist, not inside data. Reaching an
        attribute still means obj.data or obj["data"], unchanged by this fix."""
        box = Box(object_id="b", position=(0, 0, 0))
        box["ttl"] = 30
        payload = json.loads(box.json())
        self.assertEqual(30, payload["ttl"])
        self.assertNotIn("ttl", payload["data"])

    def test_write_of_an_existing_top_level_key_overwrites_it(self):
        box = Box(object_id="b", position=(0, 0, 0))
        self.assertFalse(box["persist"])
        box["persist"] = True
        self.assertTrue(box["persist"])

    def test_object_writes_match_a_plain_base_object(self):
        """A dict-style write on an Object must do what one on any other
        BaseObject does; only the shadowed name made them differ."""
        attribute = Attribute(x=1)
        box = Box(object_id="b", position=(0, 0, 0))
        attribute["y"] = 2
        box["y"] = 2
        self.assertEqual(2, vars(attribute)["y"])
        self.assertEqual(2, vars(box)["y"])

    def test_write_works_on_every_object_subclass_depth(self):
        """The shadow came from Object, so it applied to every subclass of it."""
        for factory in (
            lambda: Object(object_id="o"),
            lambda: Box(object_id="b"),
            lambda: Text(object_id="t", text="hi"),
        ):
            instance = factory()
            with self.subTest(cls=type(instance).__name__):
                instance["foo"] = "bar"
                self.assertEqual("bar", instance["foo"])


class TestRegistryClassmethodIsUnchanged(ObjectDictWriteTestCase):
    """Object.add is public API. The fix must not rename it or change it."""

    def test_add_still_registers_an_object(self):
        box = Box(object_id="b", position=(0, 0, 0))
        Object.all_objects.clear()
        Object.add(box)
        self.assertIs(box, Object.get("b"))
        self.assertTrue(Object.exists("b"))

    def test_add_is_still_a_classmethod_taking_one_argument(self):
        self.assertTrue(isinstance(Object.__dict__["add"], classmethod))
        # bound to the class, so cls is already supplied: one argument left, and
        # still named "obj". Object.add(self) is how Object.__init__ and
        # Program.__init__ call it.
        self.assertEqual(["obj"], list(inspect.signature(Object.add).parameters))

    def test_a_dict_style_write_does_not_touch_the_registry(self):
        """The bug was a call into the registry. A write must not add entries -
        nor start registering the value under some attribute of it."""
        box = Box(object_id="b", position=(0, 0, 0))
        before = dict(Object.all_objects)
        box["foo"] = 1
        self.assertEqual(before, Object.all_objects)

    def test_base_object_add_still_stores_an_attribute(self):
        """BaseObject.add is public too, and remains the storage helper."""
        holder = BaseObject(x=1)
        holder.add("y", 2)
        self.assertEqual(2, holder["y"])


class TestReadOnlyPropertyNamesDiverge(ObjectDictWriteTestCase):
    """A dict-style write to a read-only property name is stored on the instance
    and does not change the property, so for such a name the two access styles
    deliberately disagree.

    __setitem__ routes only names declared as @deprecated properties through the
    property (PR #248); every other name is stored. Object.clickable is a plain
    read-only property computed from data, so it is stored past -- accepted
    behaviour, not something this fix introduces or tries to change.
    """

    def test_write_to_a_read_only_property_name_is_stored_and_leaves_the_property(self):
        box = Box(object_id="b", position=(0, 0, 0))
        self.assertFalse(box.clickable)

        box["clickable"] = 1

        # stored where __getitem__ reads, and the property still reports data
        self.assertEqual(1, box["clickable"])
        self.assertEqual(1, vars(box)["clickable"])
        self.assertFalse(box.clickable)

    def test_such_a_write_ships_a_top_level_key_in_the_payload(self):
        """Being stored means being published, like any other top-level write.

        Spelled out rather than left implied: "clickable" is a name the schema
        gives a meaning inside data, so a top-level one is the caller's doing.
        """
        box = Box(object_id="b", position=(0, 0, 0))
        box["clickable"] = 1
        payload = json.loads(box.json())
        self.assertEqual(1, payload["clickable"])
        self.assertNotIn("clickable", payload["data"])


class TestDeprecatedRoutingStillApplies(ObjectDictWriteTestCase):
    """PR #248 routes names declared as @deprecated properties through the
    property instead of storing them. That ran through the same line."""

    def test_deprecated_key_on_an_object_still_takes_the_property_route(self):
        text = Text(object_id="t", text="hi")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            text["text"] = "bye"
        self.assertEqual(1, len(caught))
        self.assertIn("deprecated", str(caught[0].message).lower())
        # the property swallowed it: no shadow key, and data.text is untouched
        self.assertNotIn("text", vars(text))
        self.assertEqual("hi", text.data.text)

    def test_a_plain_key_on_an_object_is_stored_without_warning(self):
        box = Box(object_id="b", position=(0, 0, 0))
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            box["foo"] = 1
        self.assertEqual([], [str(w.message) for w in caught])
        self.assertEqual(1, vars(box)["foo"])


if __name__ == "__main__":
    unittest.main()
