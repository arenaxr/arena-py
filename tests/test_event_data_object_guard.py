"""Event data must refuse a live Arena Object, the way scene data already does.

Data.update_data raises ValueError for an Object stored as a direct value
under any key but "parent". DataEvent.update_data had no equivalent guard: its
fallback is
`try: data[k] = Attribute(**v) / except: data[k] = v`, and an Object fails that
coercion, so it was stored as-is.

That matters because Event.json() serializes every data key straight out of
vars(), so a stored Object rides onto the wire carrying exactly the private
state Object.json_preprocess exists to strip -- evt_handler, update_handler,
animations, delayed_prop_tasks -- and a camera- or hand-shaped value does not
even get that far: obj.camera <-> user.hands is a real cycle, so json.dumps
raises "Circular reference detected" at publish time, far from the assignment
that caused it.

These tests pin the guard, and pin that it fires at assignment time for every
key and for Object subclasses at any inheritance depth, since that is what makes
the error point at the caller's mistake rather than at a later publish. The guard
inspects direct values only -- an Object reached through a list or dict value is
still accepted, and still leaks or cycles at publish time -- so nothing here
claims otherwise; recursing is a follow-up.

Object.all_objects and Object.private_objects are global class state, so every
test clears them before and after itself to avoid leaking objects into the rest
of the suite.
"""

import json
import unittest

from arena.attributes import Position
from arena.attributes.data import Data
from arena.attributes.data_event import DataEvent
from arena.events import Event
from arena.objects import Box, Camera, HandLeft, Model, Object

PRIVATE_KEYS = ("evt_handler", "update_handler", "animations", "delayed_prop_tasks")


class ObjectWithNoObjectId(Object):
    """An Object subclass whose __init__ deliberately skips super().__init__.

    That leaves the instance with no object_id at all, which is the shape the
    guard's defensive getattr exists for. Owned by this file on purpose: a user
    subclass that skips super() is the case that has to keep working, and pinning
    it against a stub keeps the test independent of whether any particular
    library class happens to skip super() today.
    """

    def __init__(self):
        pass


class EventDataObjectGuardTestCase(unittest.TestCase):
    def setUp(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    def tearDown(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    @staticmethod
    def make_camera(object_id="camera_test_test"):
        """Builds a Camera the way Scene does, from a data dict.

        Camera.__init__ only calls super().__init__ when data carries a position
        or rotation, so the position here is what makes it a usable object.
        """
        return Camera(object_id=object_id, data={"position": {"x": 0, "y": 1.6, "z": 0}})

    @classmethod
    def make_linked_hand(cls, object_id="handLeft_test_test"):
        """Builds a hand joined to a camera as Scene._process_message joins them.

        That pairing (user.hands[object_type] = obj; obj.camera = user) is a
        genuine reference cycle, which is why it belongs in these tests.
        """
        camera = cls.make_camera()
        hand = HandLeft(object_id=object_id, data={"position": {"x": 0, "y": 1, "z": 0}})
        camera.hands[hand.object_type] = hand
        hand.camera = camera
        return hand


class TestObjectIsRejected(EventDataObjectGuardTestCase):
    def test_object_under_the_object_key_is_rejected(self):
        """The reported case: the key that reads as if it were meant to work."""
        box = Box(object_id="box1", position=(1, 2, 3))
        with self.assertRaises(ValueError) as caught:
            DataEvent(object=box)
        self.assertEqual("Invalid Arena Object as attribute object: box1", str(caught.exception))

    def test_object_under_any_other_key_is_rejected(self):
        """The key name is irrelevant: nothing in event data may hold an Object."""
        box = Box(object_id="box1", position=(1, 2, 3))
        for key in ("anykey", "target", "targetPosition", "parent"):
            with self.subTest(key=key):
                with self.assertRaises(ValueError) as caught:
                    DataEvent(**{key: box})
                self.assertEqual(
                    f"Invalid Arena Object as attribute {key}: box1", str(caught.exception)
                )

    def test_parent_is_not_exempt_the_way_it_is_in_scene_data(self):
        """Data exempts "parent" because a scene object legitimately takes one.

        Event data has no parent semantics, and no caller in the library passes
        an Object through event data -- Scene's event builders all reduce an
        Object to its object_id first -- so copying that exemption here would
        only reopen the leak under one key.
        """
        box = Box(object_id="box1", position=(1, 2, 3))
        # Scene data accepts the key. Exactly what it stores there is Data's
        # business and a known follow-up, so this only pins that it is accepted,
        # not that the value survives as a live Object.
        self.assertIn("parent", Data.update_data({}, {"parent": box}))
        with self.assertRaises(ValueError) as caught:
            DataEvent(parent=box)
        self.assertEqual("Invalid Arena Object as attribute parent: box1", str(caught.exception))

    def test_subclass_more_than_one_level_deep_is_rejected(self):
        """Model subclasses GltfModel, which subclasses Object.

        The guard decides by walking the MRO, so depth does not matter. Deciding
        on the first base alone -- as Data.update_data still does -- would let
        Model, GLTF, Card, ButtonPanel, Prompt and ThickLine straight through.
        """
        model = Model(object_id="model1", url="model.glb")
        with self.assertRaises(ValueError) as caught:
            DataEvent(thing=model)
        self.assertEqual("Invalid Arena Object as attribute thing: model1", str(caught.exception))

    def test_object_itself_is_rejected(self):
        """A bare Object is an Arena Object too, whatever its own first base is."""
        obj = Object(object_id="plain1")
        with self.assertRaises(ValueError):
            DataEvent(thing=obj)

    def test_object_without_an_object_id_still_reports_a_usable_error(self):
        """A subclass that skips super().__init__ has no object_id at all.

        Reading it unguarded for the message would raise AttributeError from
        inside the guard, hiding the actual problem. The guard falls back to the
        class name instead, so the caller still learns what they passed.
        """
        with self.assertRaises(ValueError) as caught:
            DataEvent(thing=ObjectWithNoObjectId())
        self.assertEqual(
            "Invalid Arena Object as attribute thing: ObjectWithNoObjectId",
            str(caught.exception),
        )


class TestEventConstructionIsRejected(EventDataObjectGuardTestCase):
    def test_event_with_an_object_in_a_data_dict_is_rejected(self):
        """The repro from the issue: Event(data={...}) reaches DataEvent directly.

        Event.__init__ consumes a *top-level* "object" kwarg, so this data-dict
        spelling is the path that still reached DataEvent unguarded.
        """
        box = Box(object_id="box1", position=(1, 2, 3))
        with self.assertRaises(ValueError):
            Event(object_id="e1", type="mousedown", data={"object": box})

    def test_private_object_state_can_no_longer_reach_the_wire(self):
        """The point of the guard: an Object passed as a direct value is refused
        at assignment, so this payload is never built and there is nothing to
        publish. Only direct values -- an Object inside a list or dict value is
        still accepted and still published, which is the follow-up."""
        box = Box(object_id="box1", position=(1, 2, 3))
        box.evt_handler = lambda scene, evt, msg: None
        with self.assertRaises(ValueError):
            Event(object_id="e1", type="mousedown", data={"leak": box})

    def test_hand_target_is_refused_at_assignment_not_at_publish(self):
        """A hand carries a real reference cycle, so before the guard this only
        failed later, as "Circular reference detected" out of json.dumps."""
        hand = self.make_linked_hand()
        with self.assertRaises(ValueError):
            Event(object_id="e1", type="mousedown", data={"target": hand})


class TestNormalEventDataStillWorks(EventDataObjectGuardTestCase):
    """The guard must not narrow anything that already worked."""

    def test_ordinary_event_data_is_unchanged(self):
        event = DataEvent(target="an-object-id", targetPosition=(1, 2, 3))
        self.assertEqual("an-object-id", event.target)
        self.assertIsInstance(event.targetPosition, Position)
        self.assertEqual((1, 2, 3), (event.targetPosition.x, event.targetPosition.y, event.targetPosition.z))

    def test_none_and_scalar_and_dict_values_are_unchanged(self):
        event = DataEvent(nothing=None, number=7, flag=True, nested={"a": 1})
        self.assertIsNone(event.nothing)
        self.assertEqual(7, event.number)
        self.assertTrue(event.flag)
        self.assertEqual(1, event.nested.a)

    def test_an_object_id_string_for_a_target_is_still_the_supported_spelling(self):
        """What Scene's own event builders do, and what must keep working."""
        box = Box(object_id="box1", position=(1, 2, 3))
        wire = json.loads(
            Event(
                object_id="e1", type="mousedown", target=box.object_id, targetPosition=box.data.position
            ).json()
        )
        self.assertEqual("box1", wire["data"]["target"])
        for private_key in PRIVATE_KEYS:
            self.assertNotIn(private_key, json.dumps(wire))


if __name__ == "__main__":
    unittest.main()
