# Environment variables definitions
#

MQTTH = "MQTTH"
"""
.. envvar:: MQTTH

The :envvar:`MQTTH` defines the MQTT host used by the library.
This variable overrides arguments passed in the command line.

Default: None
"""

ARENA_USERNAME = "ARENA_USERNAME"
"""
.. envvar:: ARENA_USERNAME

The :envvar:`ARENA_USERNAME` defines username used to authenticate.
This variable overrides arguments passed in the command line.

Default: None
"""

ARENA_PASSWORD = "ARENA_PASSWORD"
"""
.. envvar:: ARENA_PASSWORD

The :envvar:`ARENA_PASSWORD` defines password used to authenticate.
This variable overrides arguments passed in the command line.

Default: None
"""

REALM = "REALM"
"""
.. envvar:: REALM

The :envvar:`REALM` defines the ARENA Realm to listen to.
After connecting, the library listens to a scene topic as follows:
`{REALM}/s/{NAMESPACE}/{SCENE}`.
This variable overrides arguments passed in the command line.

Default: None
"""

SCENE = "SCENE"
"""
.. envvar:: SCENE

The :envvar:`SCENE` defines ARENA Scene to listen to.
After connecting, the library listens to a scene topic as follows:
`{REALM}/s/{NAMESPACE}/{SCENE}`.
This variable overrides arguments passed in the command line.

Default: None
"""

NAMESPACE = "NAMESPACE"
"""
.. envvar:: NAMESPACE

The :envvar:`NAMESPACE` defines ARENA Namespace to listen to.
After connecting, the library listens to a scene topic as follows:
`{REALM}/s/{NAMESPACE}/{SCENE}`.
This variable overrides arguments passed in the command line.

Default: None
"""

DEVICE = "DEVICE"
"""
.. envvar:: DEVICE

The :envvar:`DEVICE` defines the name of a device, to publish and listen to. 
After connecting, the library listens to device topic as follows:
`{REALM}/d/{NAMESPACE}/{SCENE}`.

This variable overrides arguments passed in the command line.

Default: None
"""

ENABLE_INTERPRETER = "ENABLE_INTERPRETER"
"""
.. envvar:: ENABLE_INTERPRETER

The :envvar:`ENABLE_INTERPRETER` enables the a simple command line interpreter that
can be used to inspect library/program state. Set this variable with a value of 
`true`, `1` or `t` (case insensitive) to enable the interpreter.

Default: False
"""

ARENA_TELEMETRY = "ARENA_TELEMETRY"
"""
.. envvar:: ARENA_TELEMETRY

The :envvar:`ARENA_TELEMETRY` environment variable enables the library's telemetry to generate 
traces, metrics, and logs. Set this variable with a value of `otlp`, `mqtt` or `console` (case insensitive) 
to enable telemetry using OpenTelemetry (OTEL) and its Protocol (OTLP), send JSON OTEL spans to MQTT, or to the console.

Default: None
"""

OTLP_ENDPOINT = "OTLP_ENDPOINT"
"""
.. envvar:: OTLP_ENDPOINT

The :envvar:`OTLP_ENDPOINT` environment variable is used when OTLP telemetry is enabled (`ARENA_TELEMETRY=otlp`) to define 
the telemtry endpoint.

Our implementation uses OpenTelemetry (OTEL) and its Protocol (OTLP) for encoding and transport.

Default: "http://localhost:4317"
"""

OTEL_LOG_LEVEL = "OTEL_LOG_LEVEL"
"""
.. envvar:: OTEL_LOG_LEVEL

The :envvar:`OTEL_LOG_LEVEL` environment variable sets the log level used by the logger 
implementation (ArenaTelemetry) using OpenTelemetry (OTEL). 
Default: "info". Our logger uses OpenTelemetry (OTEL). 
"""
