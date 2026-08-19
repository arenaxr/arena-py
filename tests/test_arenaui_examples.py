"""Tests the two canonical ARENAUI examples against recorded traces.

Both handlers act on the object the event fired on through evt.object, the
reference Scene attaches to an inbound clientEvent, rather than reaching back
out to the object variable the example created. These traces drive that path
end to end: a buttonClick arrives for the panel/prompt, and the example has to
publish the update/delete for that same object_id.
"""

import unittest

from arena.test_system import ArenaE2ETest


class TestArenauiExamples(unittest.TestCase):
    def test_arenaui_prompt_deletes_the_object_the_event_fired_on(self):
        """OK on the prompt deletes promptA, the object handed to the handler."""
        ArenaE2ETest.run_script(
            script_path="examples/objects/arenaui_prompt.py",
            trace_path="tests/trace_arenaui_prompt.json",
            scene_name="example",
            namespace="public",
        )

    def test_arenaui_button_panel_updates_the_object_the_event_fired_on(self):
        """Switching button sets updates button-panel, the event's own target."""
        ArenaE2ETest.run_script(
            script_path="examples/objects/arenaui_button_panel.py",
            trace_path="tests/trace_arenaui_button_panel.json",
            scene_name="example",
            namespace="public",
        )


if __name__ == "__main__":
    unittest.main()
