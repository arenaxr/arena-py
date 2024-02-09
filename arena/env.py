# Environment variables definitions
# When applicable, variable defaults are defined by ENV_DEFAULTS
#
import sys 
import os

REALM = "REALM"
"""
.. envvar:: REALM

The :envvar:`REALM` defines the ARENA Realm to listen to.
After connecting, the library listens to a scene topic as follows:
`{REALM}/s/{NAMESPACE}/{SCENE}`.
This variable overrides arguments passed in the scene's constructor.
"""

SCENE = "SCENE"
"""
.. envvar:: SCENE

The :envvar:`SCENE` defines ARENA Scene to listen to.
After connecting, the library listens to a scene topic as follows:
`{REALM}/s/{NAMESPACE}/{SCENE}`.
This variable overrides arguments passed in the scene's constructor.
"""

NAMESPACE = "NAMESPACE"
"""
.. envvar:: NAMESPACE

The :envvar:`NAMESPACE` defines ARENA Namespace to listen to.
After connecting, the library listens to a scene topic as follows:
`{REALM}/s/{NAMESPACE}/{SCENE}`.
This variable overrides arguments passed in the scene's constructor.
"""

ARENA_USERNAME = "ARENA_USERNAME"
"""
.. envvar:: ARENA_USERNAME

The :envvar:`ARENA_USERNAME` defines username used to authenticate.
If undefined, will try to use local authentication information previously saved.
"""

ARENA_PASSWORD = "ARENA_PASSWORD"
"""
.. envvar:: ARENA_PASSWORD

The :envvar:`ARENA_PASSWORD` defines password used to authenticate.
If undefined, will try to use local authentication information previously saved.
"""

MQTTH = "MQTTH"
"""
.. envvar:: MQTTH

The :envvar:`MQTTH` defines the MQTT host used by the library.
This variable allows to use a broker different from the host argument passed to the 
scene constructor
"""

DEVICE = "DEVICE"
"""
.. envvar:: DEVICE

The :envvar:`DEVICE` defines the name of a device, to publish and listen to. 
After connecting, the library listens to device topic as follows:
`{REALM}/d/{NAMESPACE}/{SCENE}`.

This variable overrides arguments passed in the command line.
"""

PROGRAM_OBJECT_ID = "PROGRAM_OBJECT_ID"
"""
.. envvar:: PROGRAM_OBJECT_ID

The :envvar:`PROGRAM_OBJECT_ID` indicates the object id in ARENA persist for this program.
This is passed by the runtime and used to identify the program object that represents the currently running program.
"""

ENABLE_INTERPRETER = "ENABLE_INTERPRETER"
"""
.. envvar:: ENABLE_INTERPRETER

The :envvar:`ENABLE_INTERPRETER` enables the a simple command line interpreter that
can be used to inspect library/program state. Set this variable with a value of 
`true`, `1` or `t` (case insensitive) to enable the interpreter.

Default: 'false'
"""

ARENA_TELEMETRY = "ARENA_TELEMETRY"
"""
.. envvar:: ARENA_TELEMETRY

The :envvar:`ARENA_TELEMETRY` environment variable enables the library's telemetry to generate 
traces, metrics, and logs. Set this variable with a value of `otlp`, `mqtt` or `console` (case insensitive) 
to enable telemetry using OpenTelemetry (OTEL) and its Protocol (OTLP), send JSON OTEL spans to MQTT, or to the console.
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
Default: "info". 
"""

PROGRAM_STATS_UPDATE_INTERVAL_MS = "PROGRAM_STATS_UPDATE_INTERVAL_MS"
"""
.. envvar:: PROGRAM_STATS_UPDATE_INTERVAL_MS

The :envvar:`PROGRAM_STATS_UPDATE_INTERVAL_MS` environment variable defines how often program
stats are published

Default: 5000. 
"""

""" Environment variables default values """
ENV_DEFAULTS = {
  ENABLE_INTERPRETER:   'false',
  OTLP_ENDPOINT:        'http://localhost:4317',
  OTEL_LOG_LEVEL:       'info',
  PROGRAM_STATS_UPDATE_INTERVAL_MS: 5000
}

def _get_env(env_var, dft_val=None):
  """ Get value of env variable with default defined by ENV_DEFAULTS; Returns dft_val if not defined in ENV_DEFAULTS """
  return os.environ.get(env_var, ENV_DEFAULTS.get(env_var, dft_val))

def _get_arena_env():
  """Get all variables defined in this module; skip credentials, private data and imports"""
  env = {}
  skip = ( ARENA_PASSWORD, ARENA_USERNAME, 'os', 'sys' )
  for key in [ v for v in dir(sys.modules[__name__]) if not v.startswith('_') and v not in skip]:
    env[key] = os.environ.get(key)
  return env
