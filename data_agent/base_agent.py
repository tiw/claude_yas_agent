from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from data_agent.mcp_tools.mcp_client import MCPClient
from data_agent.mcp_tools.mcp_config import MCPConfigManager, MCPServerConfig, ServerType
from data_agent.utils.debug import DebugManager
from data_agent.prompts.prompt_manager import PromptManager
from data_agent.llm.llm_manager import LLMManager
from data_agent.utils.observability_disabled import ObservabilityManager
from data_agent.utils.security import SecurityManager
from data_agent.memory import MemoryManager
from data_agent.enhanced_memory import AgentMemory
from data_agent.planning import ProjectPlanner
from data_agent.multi_agent import SubAgentManager
from data_agent.reflection import ReflectionEngine
from pydantic import BaseModel
import json
import os
import logging

logger = logging.getLogger(__name__)


class BaseAgentConfig(BaseModel):
    """基础Agent配置"""
    debug_mode: bool = False
    langfuse_enabled: bool = False
    default_llm: str = "qwen"
    mcp_config: Optional[Dict[str, Any]] = None


class BaseAgent:
    """基础Agent类，封装通用功能"""
    
    def __init__(self, config: BaseAgentConfig):
        self.config = config
        # 构建MCP配置
        if config.mcp_config:
            mcp_config = config.mcp_config
        else:
            # 使用新的配置管理器创建默认配置
            config_manager = MCPConfigManager()
            default_servers = config_manager.create_default_servers()
            mcp_config = config_manager.get_mcp_client_config()
            # 子类应该更新特定的URL
            
        self.mcp_client = MCPClient(mcp_config)
        self.debug_manager = DebugManager(enabled=config.debug_mode, langfuse_enabled=config.langfuse_enabled)
        self.prompt_manager = PromptManager()
        self.llm_manager = LLMManager(default_model=config.default_llm)
        self.observability = ObservabilityManager()
        self.security = SecurityManager()
        self.memory = MemoryManager()
        self.enhanced_memory = AgentMemory()
        self.planner = ProjectPlanner()
        self.sub_agent_manager = SubAgentManager(self)
        self.reflection_engine = ReflectionEngine(self)
        self.conversation_history = []
        
    async def process_query(self, user_input: str, user_id: str = "anonymous", files: list = None) -> str:
        """处理用户查询（带安全检查）- 子类应重写此方法"""
        raise NotImplementedError("子类必须实现process_query方法")
    
    async def _handle_date_parameters(self, parsed_query: Dict[str, Any]) -> Dict[str, Any]:
        """处理日期参数，如将'最近'转换为具体日期"""
        # 确保parsed_query是字典
        if not isinstance(parsed_query, dict):
            logger.warning(f"_handle_date_parameters received non-dict: {type(parsed_query)}")
            return parsed_query if parsed_query is not None else {}
            
        if "date_range" in parsed_query:
            date_range = parsed_query["date_range"]
            # 确保date_range是字典
            if isinstance(date_range, dict) and date_range.get("relative") == "recent":
                # 处理"最近"的逻辑
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)  # 默认最近30天
                
                # 根据具体需求调整时间范围
                if "days" in date_range:
                    start_date = end_date - timedelta(days=date_range["days"])
                elif "weeks" in date_range:
                    start_date = end_date - timedelta(weeks=date_range["weeks"])
                elif "months" in date_range:
                    start_date = end_date - timedelta(days=date_range["months"] * 30)
                
                parsed_query["date_range"]["start_date"] = start_date.isoformat()
                parsed_query["date_range"]["end_date"] = end_date.isoformat()
                parsed_query["date_range"]["relative"] = None  # 清除相对时间标记
                
        return parsed_query
    
    async def _preprocess_relative_time_expressions(self, user_input: str, parsed_query: Dict[str, Any]) -> Dict[str, Any]:
        """预处理相对时间表达式，如'最近'、'过去'等"""
        # 确保parsed_query是字典
        if not isinstance(parsed_query, dict):
            logger.warning(f"_preprocess_relative_time_expressions received non-dict: {type(parsed_query)}")
            parsed_query = {} if parsed_query is None else parsed_query
            
        import re
        
        # 检查用户输入中是否包含相对时间表达式
        recent_patterns = [
            (r"最近\s*(\d+)\s*天", "days"),
            (r"过去\s*(\d+)\s*天", "days"),
            (r"最近\s*(\d+)\s*周", "weeks"),
            (r"过去\s*(\d+)\s*周", "weeks"),
            (r"最近\s*(\d+)\s*个月", "months"),
            (r"过去\s*(\d+)\s*个月", "months"),
            (r"最近\s*几\s*天", "days"),
            (r"最近\s*几\s*周", "weeks"),
            (r"最近\s*几\s*个月", "months")
        ]
        
        for pattern, unit in recent_patterns:
            match = re.search(pattern, user_input)
            if match:
                # 确保parsed_query是字典后再操作
                if not isinstance(parsed_query, dict):
                    parsed_query = {}
                    
                # 初始化date_range如果不存在
                if "date_range" not in parsed_query:
                    parsed_query["date_range"] = {}
                
                # 设置相对时间标记
                parsed_query["date_range"]["relative"] = "recent"
                
                # 如果匹配到了具体数字，设置数量
                if match.groups() and match.group(1):
                    try:
                        parsed_query["date_range"][unit] = int(match.group(1))
                    except ValueError:
                        # 如果转换失败，使用默认值
                        parsed_query["date_range"][unit] = 7 if unit == "days" else 1
                else:
                    # 如果是"几"或没有具体数字，使用默认值
                    parsed_query["date_range"][unit] = 7 if unit == "days" else 1
                    
                break  # 只处理第一个匹配到的模式
        
        return parsed_query if isinstance(parsed_query, dict) else {}
    
    async def _call_llm(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """调用LLM"""
        self.debug_manager.log_llm_input(prompt, context)
        self.observability.record_llm_call(self.config.default_llm)
        
        try:
            # 调用实际的LLM
            result = await self.llm_manager.generate(prompt, context)
            
            # 如果返回的是包含response字段的字典，尝试解析其中的JSON
            if isinstance(result, dict) and "response" in result:
                response_text = result["response"]
                # 尝试从代码块中提取JSON
                import re
                json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response_text, re.DOTALL)
                if json_match:
                    try:
                        import json
                        parsed_json = json.loads(json_match.group(1))
                        return parsed_json
                    except json.JSONDecodeError:
                        pass
                # 如果没有代码块，直接尝试解析整个响应
                try:
                    import json
                    parsed_json = json.loads(response_text)
                    return parsed_json
                except json.JSONDecodeError:
                    pass
            
            return result
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            self.debug_manager.log_error(e)
            # 如果LLM调用失败，返回默认的上下文字典
            return context