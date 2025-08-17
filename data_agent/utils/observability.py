from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

class ObservabilityManager:
    """可观察性管理器"""
    
    def __init__(self, service_name: str = "data-analysis-agent"):
        self.service_name = service_name
        self._setup_tracing()
        self._setup_metrics()
    
    def _setup_tracing(self):
        """设置追踪"""
        tracer_provider = TracerProvider()
        
        # 控制台输出（开发环境）
        console_exporter = ConsoleSpanExporter()
        tracer_provider.add_span_processor(
            BatchSpanProcessor(console_exporter)
        )
        
        # OTLP导出器（生产环境）
        try:
            otlp_exporter = OTLPSpanExporter()
            tracer_provider.add_span_processor(
                BatchSpanProcessor(otlp_exporter)
            )
        except Exception:
            pass  # OTLP不可用时忽略
        
        trace.set_tracer_provider(tracer_provider)
        self.tracer = trace.get_tracer(self.service_name)
    
    def _setup_metrics(self):
        """设置指标"""
        # 创建指标读取器
        reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
        meter_provider = MeterProvider(metric_readers=[reader])
        metrics.set_meter_provider(meter_provider)
        self.meter = metrics.get_meter(self.service_name)
        
        # 定义指标
        self.query_counter = self.meter.create_counter(
            "queries_processed",
            description="处理的查询数量"
        )
        
        self.llm_call_counter = self.meter.create_counter(
            "llm_calls",
            description="LLM调用次数"
        )
        
        self.mcp_call_counter = self.meter.create_counter(
            "mcp_calls",
            description="MCP调用次数"
        )
    
    def record_query(self, query_type: str = "unknown"):
        """记录查询"""
        self.query_counter.add(1, {"query_type": query_type})
    
    def record_llm_call(self, model: str = "unknown"):
        """记录LLM调用"""
        self.llm_call_counter.add(1, {"model": model})
    
    def record_mcp_call(self, tool: str = "unknown"):
        """记录MCP调用"""
        self.mcp_call_counter.add(1, {"tool": tool})