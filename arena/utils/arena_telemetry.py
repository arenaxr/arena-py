import atexit
import sys
import os
import signal 
import time

from typing import Callable, Optional, List, Sequence

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider, ReadableSpan, Span
from opentelemetry.trace import NoOpTracerProvider, Status, StatusCode
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SpanExporter, SpanExportResult

from ..env_vars import (
    ARENA_TELEMETRY,
    OTLP_ENDPOINT
)

OTLP_ENDPOINT_DFT = "http://localhost:4317"    
TRACE_TOPIC_DFT = "realm/ns/scene/t/traces"

class MQTTSpanExporter(SpanExporter):
    """Implementation of :class:`SpanExporter` that sends spans to MQTT

    """

    def __init__(
        self,
        topic: Optional[str] = TRACE_TOPIC_DFT,
        service_name: Optional[str] = None,
        formatter: Callable[
            [ReadableSpan], str
        ] = lambda span: span.to_json()
        + os.linesep,
    ):
        # TODO: create mqtt client and assign its publish calls
        self.publish = None
        self.publish_flush = None
        
        self.topic = topic
        self.formatter = formatter
        self.service_name = service_name

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        for span in spans:
            #self.out.write(self.formatter(span))
            self.publish(self.topic, self.formatter(span))
        if self.publish_flush: self.publish_flush(True)
        return SpanExportResult.SUCCESS

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True
    
    def shutdown(self) -> None:
        print("shutdown exporter!")
        pass
    
def kill_handler(*args):
    sys.exit(0)
        
# patch sys.exit to save exit status
class ExitHooks(object):
    def __init__(self):
        self.exit_arg = None

    def hook(self):
        self._orig_exit = sys.exit
        sys.exit = self.exit
        
    def exit(self, arg=0):
        self.exit_arg = arg
        self._orig_exit(arg)
                
class ArenaTelemetry():
    
    parent_span: Span = None

    def __init__(self, name=sys.argv[0], id=None):
            
        service_name = f"{name}"
        if id: service_name = service_name + "({id})"
        # Service name is required for most backends
        resource = Resource(attributes={
            SERVICE_NAME: service_name
        })
        
        env_telemetry = os.environ.get(ARENA_TELEMETRY, 'None')
        otlp_endpoint = os.environ.get(OTLP_ENDPOINT, OTLP_ENDPOINT_DFT)
        tel_exporters = {
            'otlp': lambda: OTLPSpanExporter(otlp_endpoint, insecure=True),
            'mqtt': lambda: MQTTSpanExporter(), 
            'console': lambda: ConsoleSpanExporter()
        }        
        self.enabled = env_telemetry.lower() in tel_exporters.keys()
        if self.enabled:
            provider = TracerProvider(resource=resource)
            processor = BatchSpanProcessor(tel_exporters[env_telemetry]())
            provider.add_span_processor(processor)
            trace.set_tracer_provider(provider)
        else:
            if not env_telemetry.lower() in ('none', 'false', ''): print(f"Warn: Invalid telemetry processor specified: {env_telemetry}")
            # instanciate a no-op tracer
            provider = NoOpTracerProvider()
            trace.set_tracer_provider(provider)

        # creates a tracer from the global tracer provider
        self.tracer = trace.get_tracer("ARENA-py")
        
        # create a parent span
        self.parent_span = self.tracer.start_span("somescene")
        self.parent_span_ctx = trace.set_span_in_context(self.parent_span)        
    
             
    # record exit status on error 
    def set_error(self, error_msg):
        self.parent_span.set_status(Status(StatusCode.ERROR, error_msg))
        
    def __del__(self):
        self.parent_span.end()       
        
    # wrapper to otel start_as_current_span; force context to be parent span
    def start_span(self, name, **kwargs):
        if 'context' in kwargs: del kwargs['context']
        return self.tracer.start_as_current_span(name, context=self.parent_span_ctx, **kwargs)

    # wrapper to otel start_as_current_span to start a process message span; force context to be parent span
    def start_process_msg_span(self, obj_id, action, **kwargs):
        if 'context' in kwargs: del kwargs['context']
        return self.tracer.start_as_current_span(f"{obj_id} {action} process_message", context=self.parent_span_ctx, **kwargs)

    # wrapper to otel start_as_current_span to start a process message span; force context to be parent span
    def start_publish_span(self, obj_id, action, type, **kwargs):
        if 'context' in kwargs: del kwargs['context']
        return self.tracer.start_as_current_span(f"{obj_id} {action} publish_message {type}", context=self.parent_span_ctx, **kwargs)
        
    # add event to current span
    def add_event(self, name, **kwargs):
        if not self.enabled: return
        current_span = trace.get_current_span()
        current_span.add_event(name, kwargs)
