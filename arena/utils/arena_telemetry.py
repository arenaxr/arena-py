"""
ArenaTelemetry stub class for `arena-py`.

The full OpenTelemetry implementation lives on the `telemetry` branch.
This stub preserves the API surface so callers work unchanged, while
routing errors and events to stderr/stdout so they remain visible.
"""

import sys


class ArenaTelemetry:
    """ArenaTelemetry stub that prints errors/events instead of tracing."""

    def __init__(self, name=sys.argv[0], id=None):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass

    def exit(self, error_msg=None, print_msg=True):
        if error_msg and print_msg:
            print(error_msg, file=sys.stderr)

    def __del__(self):
        pass

    def start_span(self, name, **kwargs):
        return self

    def start_process_msg_span(self, obj_id, action, **kwargs):
        return self

    def start_publish_span(self, obj_id, action, type, **kwargs):
        return self

    def add_event(self, name, span=None, print_msg=True, **kwargs):
        pass  # Tracing-only; span.add_event() is too noisy for console

    def set_error(self, error_msg, span=None, print_msg=True):
        print(error_msg, file=sys.stderr)

