from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from flask import current_app

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

tracer = trace.get_tracer(__name__)

def trace_func(fn):
    def wrapper(*args, **kwargs):
        with tracer.start_as_current_span(fn.__name__):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                current_app.logger.error(f"Traced error in {fn.__name__}: {e}")
                raise
    return wrapper