"""
"MQTTSpanExporter/ArenaTelemetry stub classes for `arena-py` branch `rustpython`.
"""

import sys


class ArenaTelemetry:
    """ArenaTelemetry stub class for `arena-py` branch `rustpython`."""

    def __init__(self, name=sys.argv[0], id=None):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass

    def exit(self, error_msg=None, print_msg=True):
        pass

    def __del__(self):
        pass

    def start_span(self, name, **kwargs):
        return self

    def start_process_msg_span(self, obj_id, action, **kwargs):
        return self

    def start_publish_span(self, obj_id, action, type, **kwargs):
        return self

    def add_event(self, name, span=None, print_msg=True, **kwargs):
        pass

    def set_error(self, error_msg, span=None, print_msg=True):
        pass
