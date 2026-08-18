"""Deprecated key access: dict-style access reports the same deprecations that
attribute-style access already reports, without changing what any lookup that
works today returns, and deprecation warnings are attributed to the caller.
"""
import functools
import os
import sysconfig
import threading
import unittest
from unittest import mock
import warnings

from arena.attributes.color import Color
from arena.attributes.data_event import DataEvent
from arena.attributes.dynamic_body import DynamicBody, Physics
from arena.attributes.rotation import Rotation
from arena.base_object import BaseObject
from arena.objects.arena_object import Object
from arena.objects.light import Light
from arena.objects.text import Text
from arena.utils import deprecated
from arena.utils import utils as arena_utils

SENTINEL = "value-from-property"
THIS_FILE = os.path.basename(__file__)


class DeprecatedKeyHolder(BaseObject):
    """Stand-in for any class declaring a deprecated key as a property."""

    writes = []

    @property
    @deprecated("DEPRECATED: old_key is deprecated, use new_key instead.")
    def old_key(self):
        return SENTINEL

    @old_key.setter
    @deprecated("DEPRECATED: old_key is deprecated, use new_key instead.")
    def old_key(self, value):
        # Mirrors the deprecated setters in the library: records nothing, stores
        # nothing. The list only lets the tests prove the setter was reached.
        DeprecatedKeyHolder.writes.append(value)

    @property
    def plain_key(self):
        """A property that is not deprecated, and so is not a dict-style key."""
        return "not-a-key"

    @property
    @deprecated("DEPRECATED: broken_key is deprecated, use new_key instead.")
    def broken_key(self):
        raise AttributeError("'DeprecatedKeyHolder' object has no attribute 'missing'")


def record(call):
    """Runs call and returns (result, [messages], [(basename, lineno)])."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = call()
    return (
        result,
        [str(w.message) for w in caught],
        [(os.path.basename(w.filename), w.lineno) for w in caught],
    )


def compiled_accessor(filename):
    """A one-line `event["source"]` reader that claims to live in `filename`.

    The file need not exist: only the frame's co_filename decides whether the frame
    walk in warn_deprecated treats it as the calling program's code.
    """
    namespace = {}
    exec(compile('def access(event):\n    return event["source"]\n', filename, "exec"), namespace)
    return namespace["access"]


class TestDeprecatedPropertiesAreMarked(unittest.TestCase):
    """Dict-style access finds the deprecated properties through the marker the
    @deprecated decorator leaves on the getter, so the marker has to survive the
    property() wrapping at every site that declares one."""

    def test_library_deprecated_properties_carry_the_marker(self):
        for owner, name in (
            (DataEvent, "source"),
            (DataEvent, "clickPos"),
            (DataEvent, "position"),
            (Text, "text"),
            (Light, "light"),
        ):
            with self.subTest(prop=f"{owner.__name__}.{name}"):
                prop = getattr(owner, name)
                self.assertIsInstance(prop, property)
                self.assertIsNotNone(getattr(prop.fget, "__arena_deprecated__", None))
                self.assertIsNotNone(getattr(prop.fset, "__arena_deprecated__", None))


class TestDeprecatedKeyDeclarations(unittest.TestCase):
    """Which names dict-style access reaches is decided per class, when the class is
    created, so inheritance and overriding have to be accounted for."""

    def test_subclass_inherits_the_deprecated_keys_of_its_base(self):
        class Sub(DeprecatedKeyHolder):
            pass

        self.assertIn("old_key", Sub._arena_deprecated_read_keys)
        holder = Sub(new_key="kept")
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(SENTINEL, holder["old_key"])

    def test_a_name_redefined_as_something_else_is_no_longer_a_key(self):
        class Sub(DeprecatedKeyHolder):
            old_key = "just a class attribute now"

        self.assertNotIn("old_key", Sub._arena_deprecated_read_keys)
        holder = Sub(new_key="kept")
        _, messages, _ = record(
            lambda: self.assertRaises(KeyError, lambda: holder["old_key"])
        )
        self.assertEqual([], messages)


    def test_a_base_that_kept_the_property_does_not_revive_a_replaced_name(self):
        """Which definition of a name is a deprecated property is decided by the MRO,
        not by whether any base still carries it. Left replaces the property with a
        plain class attribute and Right inherits it, so `getattr` resolves Left's
        plain attribute - dict access must not answer with it."""

        class Left(DeprecatedKeyHolder):
            old_key = "just a class attribute now"

        class Right(DeprecatedKeyHolder):
            pass

        class Child(Left, Right):
            pass

        self.assertNotIn("old_key", Child._arena_deprecated_read_keys)
        self.assertNotIn("old_key", Child._arena_deprecated_write_keys)
        child = Child(new_key="kept")
        self.assertEqual("just a class attribute now", child.old_key)
        _, messages, _ = record(
            lambda: self.assertRaises(KeyError, lambda: child["old_key"])
        )
        self.assertEqual([], messages)

    def test_a_base_earlier_in_the_mro_keeping_the_property_still_decides(self):
        """The mirror image of the test above, so that it is the MRO order that is
        being pinned and not simply 'any replacement anywhere wins': here the base
        that declares the deprecated property comes first."""

        class Keeps(DeprecatedKeyHolder):
            @property
            @deprecated("DEPRECATED: old_key is deprecated, use new_key instead.")
            def old_key(self):
                return SENTINEL

        class Replaces(DeprecatedKeyHolder):
            old_key = "just a class attribute now"

        class Child(Keeps, Replaces):
            pass

        self.assertIn("old_key", Child._arena_deprecated_read_keys)
        child = Child(new_key="kept")
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(SENTINEL, child["old_key"])

    def test_a_property_whose_getter_is_not_deprecated_is_not_a_read_key(self):
        """Deprecation can be split across the accessors of one property. A getter
        that is not deprecated reports nothing attribute-style, so dict-style reads
        must not reach it either - that would widen dict access to a name that is not
        deprecated. Its write still goes through the deprecated setter."""

        class FreshGetter(DeprecatedKeyHolder):
            @DeprecatedKeyHolder.old_key.getter
            def old_key(self):
                return "not-deprecated-any-more"

        self.assertNotIn("old_key", FreshGetter._arena_deprecated_read_keys)
        self.assertIn("old_key", FreshGetter._arena_deprecated_write_keys)
        holder = FreshGetter(new_key="kept")
        _, messages, _ = record(
            lambda: self.assertRaises(KeyError, lambda: holder["old_key"])
        )
        self.assertEqual([], messages)

    def test_a_write_to_a_split_deprecation_still_reaches_the_deprecated_setter(self):
        class FreshGetter(DeprecatedKeyHolder):
            @DeprecatedKeyHolder.old_key.getter
            def old_key(self):
                return "not-deprecated-any-more"

        DeprecatedKeyHolder.writes = []
        item_holder = FreshGetter(new_key="kept")
        attr_holder = FreshGetter(new_key="kept")
        _, item_messages, _ = record(lambda: item_holder.__setitem__("old_key", "written"))
        _, attr_messages, _ = record(lambda: setattr(attr_holder, "old_key", "written"))
        self.assertEqual(
            ["DEPRECATED: old_key is deprecated, use new_key instead."], item_messages
        )
        self.assertEqual(attr_messages, item_messages)
        self.assertEqual(vars(attr_holder), vars(item_holder))
        self.assertNotIn("old_key", vars(item_holder))
        self.assertEqual(["written", "written"], DeprecatedKeyHolder.writes)


class TestDictStyleReads(unittest.TestCase):
    def test_dict_access_to_deprecated_property_warns_and_returns_value(self):
        holder = DeprecatedKeyHolder(new_key="kept")
        with self.assertWarns(DeprecationWarning):
            value = holder["old_key"]
        self.assertEqual(SENTINEL, value)

    def test_attribute_and_dict_access_agree(self):
        holder = DeprecatedKeyHolder(new_key="kept")
        attr_value, attr_messages, _ = record(lambda: holder.old_key)
        item_value, item_messages, _ = record(lambda: holder["old_key"])
        self.assertEqual(attr_value, item_value)
        self.assertEqual(attr_messages, item_messages)

    def test_dict_access_to_deprecated_property_of_data_event_warns(self):
        event = DataEvent(target="an-object-id")
        for key in ("source", "clickPos", "position"):
            with self.subTest(key=key):
                with self.assertWarns(DeprecationWarning):
                    self.assertIsNone(event[key])

    def test_dict_access_to_present_key_does_not_warn(self):
        event = DataEvent(target="an-object-id")
        value, messages, _ = record(lambda: event["target"])
        self.assertEqual("an-object-id", value)
        self.assertEqual([], messages)

    def test_stored_key_wins_over_a_same_named_deprecated_property(self):
        """The invariant the whole design rests on: a deprecated key that arrived on
        the wire is stored on the instance, and reading it must still return what
        arrived, silently. Consulting the property first would answer None instead."""
        event = DataEvent(target="an-object-id", source="a-camera-id")
        self.assertIn("source", vars(event))
        value, messages, _ = record(lambda: event["source"])
        self.assertEqual("a-camera-id", value)
        self.assertEqual([], messages)

        holder = DeprecatedKeyHolder(old_key="stored-on-the-instance")
        value, messages, _ = record(lambda: holder["old_key"])
        self.assertEqual("stored-on-the-instance", value)
        self.assertEqual([], messages)

    def test_every_wire_delivered_deprecated_key_reads_back_unchanged(self):
        """The production shape of the case above: a clientEvent payload carrying
        the deprecated keys, fed in the way scene.py feeds inbound messages."""
        payload = {
            "target": "an-object-id",
            "source": "a-camera-id",
            "clickPos": {"x": 1, "y": 2, "z": 3},
            "position": {"x": 4, "y": 5, "z": 6},
        }
        event, messages, _ = record(lambda: DataEvent(**payload))
        self.assertEqual([], messages)
        for key in payload:
            with self.subTest(key=key):
                value, messages, _ = record(lambda k=key: event[k])
                self.assertEqual([], messages)
                self.assertIsNotNone(value)

    def test_unknown_key_still_raises_key_error(self):
        holder = DeprecatedKeyHolder(new_key="kept")
        for target in (DataEvent(target="an-object-id"), holder):
            with self.subTest(target=type(target).__name__):
                _, messages, _ = record(
                    lambda t=target: self.assertRaises(KeyError, lambda: t["no_such_key"])
                )
                self.assertEqual([], messages)

    def test_methods_are_not_reachable_by_dict_access(self):
        event = DataEvent(target="an-object-id")
        with self.assertRaises(KeyError):
            event["json"]

    def test_non_deprecated_property_is_not_reachable_by_dict_access(self):
        """The fallback is limited to deprecated properties, so every other
        class-level property keeps raising KeyError as it did before."""
        # Object.all_objects is global class state, so do not leak this one.
        box = Object(object_id="deprecated-key-access-probe", object_type="box")
        self.addCleanup(Object.all_objects.pop, box.object_id, None)
        cases = (
            (Rotation(0, 0, 0), "is_quaternion"),
            (Color(0, 0, 0), "hex"),
            (box, "clickable"),
            (DeprecatedKeyHolder(new_key="kept"), "plain_key"),
        )
        for target, key in cases:
            with self.subTest(target=type(target).__name__, key=key):
                self.assertNotIn(key, vars(target))
                self.assertIsInstance(getattr(type(target), key), property)
                _, messages, _ = record(
                    lambda t=target, k=key: self.assertRaises(KeyError, lambda: t[k])
                )
                self.assertEqual([], messages)

    def test_non_string_key_raises_key_error(self):
        event = DataEvent(target="an-object-id")
        for key in (0, None, 3.5, b"source", (1, 2)):
            with self.subTest(key=key):
                with self.assertRaises(KeyError):
                    event[key]
        # list() reaches for event[0]; it must fail the same way it always did.
        with self.assertRaises(KeyError):
            list(event)

    def test_attribute_error_from_a_deprecated_getter_becomes_key_error(self):
        """A subscript must not raise AttributeError: dict-style access keeps the
        mapping contract, and the original error stays in the traceback chain."""
        holder = DeprecatedKeyHolder(new_key="kept")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with self.assertRaises(KeyError) as caught:
                holder["broken_key"]
        self.assertEqual("broken_key", caught.exception.args[0])
        self.assertIsInstance(caught.exception.__cause__, AttributeError)


class TestDictStyleWrites(unittest.TestCase):
    def setUp(self):
        DeprecatedKeyHolder.writes = []

    def test_write_to_deprecated_key_goes_through_the_property(self):
        holder = DeprecatedKeyHolder(new_key="kept")
        _, messages, _ = record(lambda: holder.__setitem__("old_key", "written"))
        self.assertEqual(
            ["DEPRECATED: old_key is deprecated, use new_key instead."], messages
        )
        self.assertEqual(["written"], DeprecatedKeyHolder.writes)
        self.assertNotIn("old_key", vars(holder))

    def test_write_matches_the_attribute_style_write(self):
        item_holder = DeprecatedKeyHolder(new_key="kept")
        attr_holder = DeprecatedKeyHolder(new_key="kept")
        _, item_messages, _ = record(lambda: item_holder.__setitem__("old_key", "written"))
        _, attr_messages, _ = record(lambda: setattr(attr_holder, "old_key", "written"))
        self.assertEqual(attr_messages, item_messages)
        self.assertEqual(vars(attr_holder), vars(item_holder))

    def test_deprecated_key_written_dict_style_does_not_reach_the_wire(self):
        event = DataEvent(target="an-object-id")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            event["source"] = "a-camera-id"
        self.assertNotIn("source", event.json())
        value, messages, _ = record(lambda: event["source"])
        self.assertIsNone(value)
        self.assertEqual(1, len(messages))

    def test_write_to_a_getter_only_deprecated_key_matches_the_attribute_write(self):
        """A deprecated property with no setter refuses an attribute-style write, so
        the dict-style write is refused the same way rather than quietly storing the
        deprecated key - which would put it back in json() and make the two access
        styles disagree again, the thing this change is for."""

        class ReadOnlyDeprecation(BaseObject):
            @property
            @deprecated("DEPRECATED: old_key is deprecated, use new_key instead.")
            def old_key(self):
                return SENTINEL

        holder = ReadOnlyDeprecation(new_key="kept")
        with self.assertRaises(AttributeError):
            holder["old_key"] = "written"
        with self.assertRaises(AttributeError):
            holder.old_key = "written"
        self.assertNotIn("old_key", vars(holder))
        self.assertNotIn("old_key", holder.json())

    def test_write_to_a_normal_key_stores_it_without_warning(self):
        holder = DeprecatedKeyHolder(new_key="kept")
        _, messages, _ = record(lambda: holder.__setitem__("new_key", "replaced"))
        self.assertEqual([], messages)
        self.assertEqual("replaced", holder["new_key"])

    def test_write_to_a_non_deprecated_property_name_is_stored_as_before(self):
        holder = DeprecatedKeyHolder(new_key="kept")
        _, messages, _ = record(lambda: holder.__setitem__("plain_key", "stored"))
        self.assertEqual([], messages)
        self.assertEqual("stored", vars(holder)["plain_key"])


class TestWarningAttribution(unittest.TestCase):
    """Python's default warning filters only show a DeprecationWarning raised by the
    running program, so a warning attributed to arena-py itself is never seen."""

    def test_dict_access_warning_points_at_calling_code(self):
        event = DataEvent(target="an-object-id")
        _, _, locations = record(lambda: event["source"])
        self.assertEqual([THIS_FILE], [name for name, _ in locations])

    def test_attribute_access_warning_points_at_calling_code(self):
        event = DataEvent(target="an-object-id")
        _, _, locations = record(lambda: event.source)
        self.assertEqual([THIS_FILE], [name for name, _ in locations])

    def test_caller_in_a_directory_sharing_the_package_prefix_is_not_skipped(self):
        """arenaxr also ships arena-robot; a directory whose path merely starts with
        the same characters as the package directory is not inside the package. The
        installed-package rule is switched off here so that this exercises only the
        package-directory rule, wherever arena-py itself happens to live."""
        event = DataEvent(target="an-object-id")
        sibling = arena_utils._PACKAGE_DIR.rstrip(os.sep) + "_robot" + os.sep + "mycode.py"
        access = compiled_accessor(sibling)
        with mock.patch.object(arena_utils, "_EXTERNAL_CODE_DIRS", ()):
            _, _, locations = record(lambda: access(event))
        self.assertEqual([("mycode.py", 2)], locations)

    def test_frames_of_the_standard_library_and_installed_packages_are_skipped(self):
        """A deprecated name reached through a stdlib callback or an installed
        package must not be blamed on that package: warnings would also record its
        already-warned registry in that module's globals."""
        event = DataEvent(target="an-object-id")
        paths = sysconfig.get_paths()
        for key in ("stdlib", "purelib"):
            with self.subTest(location=key):
                access = compiled_accessor(os.path.join(paths[key], "other_pkg", "mod.py"))
                _, _, locations = record(lambda: access(event))
                self.assertEqual([THIS_FILE], [name for name, _ in locations])

    def test_attribution_falls_back_to_the_library_without_a_caller_frame(self):
        """When the stack holds no frame of the calling program at all - here the
        deprecated read is the thread's target - the warning is attributed to
        arena-py, never to the standard library frame that happened to run it."""
        event = DataEvent(target="an-object-id")

        def read_in_thread():
            thread = threading.Thread(target=functools.partial(getattr, event, "source"))
            thread.start()
            thread.join()

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            read_in_thread()
        self.assertEqual(1, len(caught))
        self.assertTrue(
            os.path.abspath(caught[0].filename).startswith(arena_utils._PACKAGE_DIR),
            f"attributed to {caught[0].filename}",
        )


class TestDeprecatedClassWarnings(unittest.TestCase):
    def test_each_distinct_message_in_the_hierarchy_is_reported_once(self):
        """Physics is a deprecated subclass of the deprecated DynamicBody: the class
        change and the attribute-key change are different things to fix, so one
        construction reports both, each exactly once, at the caller's line."""
        _, messages, locations = record(lambda: Physics(type="dynamic"))
        self.assertEqual(
            [
                Physics.__arena_deprecated_msgs__[0],
                DynamicBody.__arena_deprecated_msgs__[0],
            ],
            messages,
        )
        self.assertEqual([THIS_FILE, THIS_FILE], [name for name, _ in locations])

    def test_a_message_repeated_in_the_hierarchy_is_reported_once(self):
        message = "DEPRECATED: repeated in the hierarchy."

        @deprecated(message)
        class Base(BaseObject):
            pass

        @deprecated(message)
        class Derived(Base):
            pass

        _, messages, _ = record(lambda: Derived())
        self.assertEqual([message], messages)

    def test_the_same_message_applied_twice_to_one_class_is_reported_once(self):
        """Each distinct message is reported once per construction, so applying the
        decorator again with a message the class already announces adds nothing. A
        genuinely different second message is still reported."""
        repeated = "DEPRECATED: applied twice."
        other = "DEPRECATED: a different thing to fix."

        @deprecated(repeated)
        @deprecated(repeated)
        class Doubly(BaseObject):
            pass

        @deprecated(other)
        @deprecated(repeated)
        class Both(BaseObject):
            pass

        _, messages, _ = record(lambda: Doubly())
        self.assertEqual([repeated], messages)
        self.assertEqual((repeated,), Doubly.__arena_deprecated_msgs__)
        _, messages, _ = record(lambda: Both())
        self.assertEqual([other, repeated], messages)

    def test_a_plain_deprecated_class_still_reports_its_own_message(self):
        _, messages, _ = record(lambda: DynamicBody(type="dynamic"))
        self.assertEqual([DynamicBody.__arena_deprecated_msgs__[0]], messages)


if __name__ == "__main__":
    unittest.main()
