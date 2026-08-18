"""Deprecated key access: dict-style access must honor the @deprecated properties
that attribute-style access already honors, and the backward-compatible attribute
key aliases must announce themselves.
"""
import os
import unittest
import warnings

from arena.attributes.data import DEPRECATED_ATTRIBUTE_ALIASES, Data
from arena.attributes.data_event import DataEvent
from arena.attributes.dynamic_body import Physics
from arena.attributes.rotation import Rotation
from arena.base_object import BaseObject
from arena.utils import deprecated

SENTINEL = "value-from-property"
THIS_FILE = os.path.basename(__file__)


class DeprecatedKeyHolder(BaseObject):
    """Stand-in for any class declaring a deprecated key as a property."""

    @property
    @deprecated("DEPRECATED: old_key is deprecated, use new_key instead.")
    def old_key(self):
        return SENTINEL


class TestDictStyleDeprecationWarnings(unittest.TestCase):
    def test_dict_access_to_deprecated_property_warns_and_returns_value(self):
        holder = DeprecatedKeyHolder(new_key="kept")
        with self.assertWarns(DeprecationWarning):
            value = holder["old_key"]
        self.assertEqual(value, SENTINEL)

    def test_attribute_and_dict_access_agree(self):
        holder = DeprecatedKeyHolder(new_key="kept")
        with warnings.catch_warnings(record=True) as attr_warnings:
            warnings.simplefilter("always")
            attr_value = holder.old_key
        with warnings.catch_warnings(record=True) as item_warnings:
            warnings.simplefilter("always")
            item_value = holder["old_key"]
        self.assertEqual(attr_value, item_value)
        self.assertEqual(
            [str(w.message) for w in attr_warnings],
            [str(w.message) for w in item_warnings],
        )

    def test_dict_access_to_deprecated_property_of_data_event_warns(self):
        event = DataEvent(target="an-object-id")
        with self.assertWarns(DeprecationWarning):
            self.assertIsNone(event["source"])
        with self.assertWarns(DeprecationWarning):
            self.assertIsNone(event["clickPos"])

    def test_dict_access_to_present_key_does_not_warn(self):
        event = DataEvent(target="an-object-id")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            self.assertEqual(event["target"], "an-object-id")
        self.assertEqual([], [str(w.message) for w in caught])

    def test_unknown_key_still_raises_key_error(self):
        event = DataEvent(target="an-object-id")
        for holder in (event, DeprecatedKeyHolder(new_key="kept")):
            with self.subTest(holder=type(holder).__name__):
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    with self.assertRaises(KeyError):
                        holder["no_such_key"]
                self.assertEqual([], [str(w.message) for w in caught])

    def test_methods_are_not_reachable_by_dict_access(self):
        # The fallback only consults properties, so methods and other class
        # attributes stay invisible to dict-style access.
        event = DataEvent(target="an-object-id")
        with self.assertRaises(KeyError):
            event["json"]

    def test_non_deprecated_property_is_reachable_by_dict_access(self):
        # The fallback is not limited to deprecated properties: any class-level
        # property is now readable with either access style.
        rotation = Rotation(0, 0, 0)
        self.assertNotIn("is_quaternion", vars(rotation))
        self.assertEqual(rotation["is_quaternion"], rotation.is_quaternion)


class TestWarningAttribution(unittest.TestCase):
    """Python's default warning filters only show a DeprecationWarning raised by the
    running program, so a warning attributed to arena-py itself is never seen."""

    def _record(self, call):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            call()
        return [os.path.basename(w.filename) for w in caught]

    def test_dict_access_warning_points_at_calling_code(self):
        event = DataEvent(target="an-object-id")
        self.assertEqual([THIS_FILE], self._record(lambda: event["source"]))

    def test_attribute_access_warning_points_at_calling_code(self):
        event = DataEvent(target="an-object-id")
        self.assertEqual([THIS_FILE], self._record(lambda: event.source))

    def test_alias_warning_points_at_calling_code(self):
        self.assertEqual([THIS_FILE], self._record(lambda: Data(clickable=True)))

    def test_deprecated_class_warns_once_and_points_at_calling_code(self):
        # Physics subclasses the also-deprecated DynamicBody; one construction must
        # still produce exactly one warning, the most derived one.
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            Physics(type="dynamic")
        self.assertEqual([Physics.__arena_deprecated__], [str(w.message) for w in caught])
        self.assertEqual([THIS_FILE], [os.path.basename(w.filename) for w in caught])


class TestDeprecatedAttributeAliases(unittest.TestCase):
    def _warnings_for(self, **kwargs):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            data = Data(**kwargs)
        return data, [str(w.message) for w in caught]

    def test_physics_alias_warns_exactly_once(self):
        data, messages = self._warnings_for(physics=True)
        self.assertEqual([DEPRECATED_ATTRIBUTE_ALIASES["physics"]], messages)
        self.assertEqual(True, data["physics"])

    def test_clickable_alias_warns_exactly_once(self):
        data, messages = self._warnings_for(clickable=True)
        self.assertEqual([DEPRECATED_ATTRIBUTE_ALIASES["clickable"]], messages)
        self.assertEqual(True, data["clickable"])

    def test_current_keys_do_not_warn(self):
        _, messages = self._warnings_for(physx_body={"type": "dynamic"}, click_listener={})
        self.assertEqual([], messages)

    def test_alias_does_not_double_warn_for_self_announcing_value(self):
        # Physics is itself decorated with @deprecated, so it has already warned by
        # the time the value reaches Data; the alias must not warn a second time.
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            physics = Physics(type="dynamic")
        self.assertTrue([str(w.message) for w in caught])
        _, messages = self._warnings_for(physics=physics)
        self.assertEqual([], messages)


if __name__ == "__main__":
    unittest.main()
