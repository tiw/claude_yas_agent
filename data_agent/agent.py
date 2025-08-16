import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from data_agent.mcp_tools.mcp_client import MCPClient
from data_agent.utils.debug import DebugManager
from data_agent.prompts.prompt_manager import PromptManager
from data_agent.llm.llm_manager import LLMManager
from pydantic import BaseModel
import json
import os

logger = logging.getLogger(__name__)

class AgentConfig(BaseModel):
    """Agent配置"""
    debug_mode: bool = False
    langfuse_enabled: bool = False
    default_llm: str = "qwen"  # 默认使用Qwen
    mcp_config: Optional[Dict[str, Any]] = None  # 自定义MCP配置

class DataAnalysisAgent:
    """数据分析Agent"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        # 构建MCP配置
        if config.mcp_config:
            mcp_config = config.mcp_config
        else:
            mcp_config = {
                "mcpServers": {
                    "sec-fetch-production": {
                        "type": "sse",
                        "url": "http://localhost:9000/mcp",
                        "headers": {
                            "X-API-Key": os.getenv("MCP_API_KEY", "your-api-key-here")
                        },
                        "serverInstructions": "SEC财报数据分析服务，支持完整的13F和财务数据查询"
                    },
                    "sec-investment-analysis": {
                        "type": "sse",
                        "url": "http://localhost:9001/mcp",
                        "headers": {
                            "X-API-Key": os.getenv("MCP_INVESTMENT_API_KEY", "your-api-key-here")
                        },
                        "serverInstructions": "SEC投资分析服务，提供巴菲特风格的投资分析功能"
                    },
                    "sec-stock-query": {
                        "type": "sse",
                        "url": "http://localhost:9002/mcp",
                        "headers": {
                            "X-API-Key": os.getenv("ALPHA_VANTAGE_KEY", "your-alpha-vantage-key")
                        },
                        "serverInstructions": "Alpha Vantage股票查询服务，提供实时股票数据和技术分析"
                    }
                }
            }
        self.mcp_client = MCPClient(mcp_config)
        self.debug_manager = DebugManager(enabled=config.debug_mode, langfuse_enabled=config.langfuse_enabled)
        self.prompt_manager = PromptManager()
        self.llm_manager = LLMManager(default_model=config.default_llm)
        self.conversation_history = []
        
    async def process_query(self, user_input: str) -> str:
        """处理用户查询"""
        try:
            # 开始新的调试会话
            session_id = self.debug_manager.start_new_session()
            
            # 记录用户输入
            self.conversation_history.append({"role": "user", "content": user_input})
            self.debug_manager.log_llm_input(user_input, self.conversation_history)
            
            # 解析用户意图和参数
            parsed_query = await self._parse_query(user_input)
            
            # 执行数据分析
            result = await self._execute_analysis(parsed_query)
            
            # 记录结果
            self.conversation_history.append({"role": "assistant", "content": result})
            self.debug_manager.log_llm_output(result)
            
            return result
            
        except Exception as e:
            logger.error(f"处理查询时出错: {e}")
            self.debug_manager.log_error(e)
            return f"处理查询时出错: {str(e)}"
    
    async def _parse_query(self, user_input: str) -> Dict[str, Any]:
        """解析用户查询"""
        # 使用prompt管理器获取解析prompt
        parse_prompt = self.prompt_manager.get_prompt("query_parser")
        
        # 构建解析上下文
        context = {
            "user_input": user_input,
            "current_date": datetime.now().isoformat(),
            "supported_mcp_tools": self.mcp_client.get_available_tools()
        }
        
        # 调用LLM解析查询
        parsed_result = await self._call_llm(parse_prompt, context)
        
        # 记录原始LLM输出用于调试
        self.debug_manager.log_llm_output(f"原始LLM输出: {parsed_result}")
        
        # 确保返回的是字典
        if not isinstance(parsed_result, dict):
            logger.warning(f"LLM返回的不是字典格式: {type(parsed_result)}")
            parsed_result = {"intent": user_input, "mcp_tools": []}
        
        self.debug_manager.log_llm_output(json.dumps(parsed_result, ensure_ascii=False, indent=2))
        
        # 处理时间参数
        parsed_result = await self._handle_date_parameters(parsed_result)
        
        # 如果是相对时间表达式，进行预处理
        parsed_result = await self._preprocess_relative_time_expressions(user_input, parsed_result)
        
        return parsed_result
    
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
    
    async def _execute_analysis(self, parsed_query: Dict[str, Any]) -> str:
        """执行数据分析"""
        results = []
        
        # 获取需要调用的MCP工具
        tools_to_call = parsed_query.get("mcp_tools", [])
        
        # 使用异步上下文管理器初始化MCP客户端
        async with self.mcp_client as mcp_client:
            for tool_info in tools_to_call:
                tool_name = tool_info["name"]
                tool_params = tool_info.get("parameters", {})
                
                try:
                    # 调用MCP工具
                    self.debug_manager.log_mcp_input(tool_name, tool_params)
                    tool_result = await mcp_client.call_tool(tool_name, tool_params)
                    self.debug_manager.log_mcp_output(tool_name, tool_result)
                    
                    results.append({
                        "tool": tool_name,
                        "result": tool_result
                    })
                    
                except Exception as e:
                    logger.error(f"调用MCP工具 {tool_name} 时出错: {e}")
                    self.debug_manager.log_error(e)
                    # 尝试恢复或继续执行其他工具
                    results.append({
                        "tool": tool_name,
                        "error": str(e)
                    })
            
            # 合并结果并生成最终输出
            return await self._generate_final_response(parsed_query, results)
    
    async def _generate_final_response(self, parsed_query: Dict[str, Any], results: List[Dict]) -> str:
        """生成最终响应"""
        # 使用prompt管理器获取响应生成prompt
        response_prompt = self.prompt_manager.get_prompt("response_generator")
        
        # 构建生成上下文
        context = {
            "original_query": parsed_query,
            "analysis_results": results,
            "conversation_history": self.conversation_history[-5:]  # 最近5轮对话
        }
        
        # 调用LLM生成最终响应
        try:
            final_response_data = await self._call_llm(response_prompt, context)
            final_response = json.dumps(final_response_data, ensure_ascii=False, indent=2)
            self.debug_manager.log_llm_output(final_response)
        except Exception as e:
            logger.error(f"生成最终响应时出错: {e}")
            self.debug_manager.log_error(e)
            # 返回简化版的响应
            final_response = json.dumps({
                "report": {
                    "executive_summary": "数据分析完成",
                    "detailed_analysis": f"共调用 {len(results)} 个工具，其中 {len([r for r in results if 'error' not in r])} 个成功",
                    "key_insights": [],
                    "recommendations": []
                }
            }, ensure_ascii=False, indent=2)
        
        return final_response
    
    async def _call_llm(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """调用LLM"""
        self.debug_manager.log_llm_input(prompt, context)
        
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