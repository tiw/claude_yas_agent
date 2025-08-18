class ObservabilityManager:
    """禁用的可观察性管理器"""
    
    def __init__(self, service_name: str = "data-analysis-agent"):
        self.service_name = service_name
        # 初始化空的tracer和meter
        self.tracer = self._create_noop_tracer()
        self.meter = self._create_noop_meter()
        
        # 初始化空的计数器
        self.query_counter = self._create_noop_counter()
        self.llm_call_counter = self._create_noop_counter()
        self.mcp_call_counter = self._create_noop_counter()
    
    def _create_noop_tracer(self):
        """创建无操作的tracer"""
        class NoopTracer:
            def start_as_current_span(self, name, *args, **kwargs):
                class NoopSpan:
                    def __enter__(self):
                        return self
                    def __exit__(self, *args):
                        pass
                return NoopSpan()
        return NoopTracer()
    
    def _create_noop_meter(self):
        """创建无操作的meter"""
        class NoopMeter:
            def create_counter(self, name, description=""):
                return self._create_noop_counter()
        return NoopMeter()
    
    def _create_noop_counter(self):
        """创建无操作的计数器"""
        class NoopCounter:
            def add(self, value, attributes=None):
                pass  # 什么都不做
        return NoopCounter()
    
    def record_query(self, query_type: str = "unknown"):
        """记录查询（无操作）"""
        pass
    
    def record_llm_call(self, model: str = "unknown"):
        """记录LLM调用（无操作）"""
        pass
    
    def record_mcp_call(self, tool: str = "unknown"):
        """记录MCP调用（无操作）"""
        pass