import logging
import json
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

# 模拟langfuse导入
try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    Langfuse = None

logger = logging.getLogger(__name__)

class DebugManager:
    """调试管理器，用于跟踪LLM和MCP的输入输出"""
    
    def __init__(self, enabled: bool = True, langfuse_enabled: bool = False):
        self.enabled = enabled
        self.langfuse_enabled = langfuse_enabled and LANGFUSE_AVAILABLE
        self.logs = []
        self.current_session_id = None
        
        if self.langfuse_enabled:
            try:
                self.langfuse = Langfuse()
            except Exception as e:
                logger.warning(f"无法初始化Langfuse: {e}")
                self.langfuse_enabled = False
                self.langfuse = None
        else:
            self.langfuse = None
            
    def start_new_session(self) -> str:
        """开始新的调试会话，返回会话ID"""
        self.current_session_id = str(uuid.uuid4())
        return self.current_session_id
        
    def set_session(self, session_id: str):
        """设置当前会话ID"""
        self.current_session_id = session_id
            
    def log_llm_input(self, prompt: str, context: Any = None):
        """记录发送给LLM的输入"""
        if not self.enabled:
            return
            
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "llm_input",
            "prompt": prompt,
            "context": context,
            "session_id": self.current_session_id
        }
        
        self.logs.append(log_entry)
        logger.debug(f"LLM输入: {prompt[:100]}...")
        
        if self.langfuse_enabled and self.langfuse:
            try:
                self.langfuse.trace(
                    name="llm_input",
                    input={
                        "prompt": prompt,
                        "context": context
                    }
                )
            except Exception as e:
                logger.warning(f"Langfuse记录失败: {e}")
                
    def log_llm_output(self, output: str):
        """记录LLM的输出"""
        if not self.enabled:
            return
            
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "llm_output",
            "output": output,
            "session_id": self.current_session_id
        }
        
        self.logs.append(log_entry)
        logger.debug(f"LLM输出: {output[:100]}...")
        
        if self.langfuse_enabled and self.langfuse:
            try:
                self.langfuse.trace(
                    name="llm_output",
                    output=output
                )
            except Exception as e:
                logger.warning(f"Langfuse记录失败: {e}")
                
    def log_mcp_input(self, tool_name: str, parameters: Dict[str, Any]):
        """记录发送给MCP的输入"""
        if not self.enabled:
            return
            
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "mcp_input",
            "tool_name": tool_name,
            "parameters": parameters,
            "session_id": self.current_session_id
        }
        
        self.logs.append(log_entry)
        logger.debug(f"MCP输入 - 工具: {tool_name}, 参数: {parameters}")
        
        if self.langfuse_enabled and self.langfuse:
            try:
                self.langfuse.trace(
                    name=f"mcp_input_{tool_name}",
                    input=parameters
                )
            except Exception as e:
                logger.warning(f"Langfuse记录失败: {e}")
                
    def log_mcp_output(self, tool_name: str, output: Dict[str, Any]):
        """记录MCP的输出"""
        if not self.enabled:
            return
            
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "mcp_output",
            "tool_name": tool_name,
            "output": output,
            "session_id": self.current_session_id
        }
        
        self.logs.append(log_entry)
        logger.debug(f"MCP输出 - 工具: {tool_name}, 结果: {output}")
        
        if self.langfuse_enabled and self.langfuse:
            try:
                self.langfuse.trace(
                    name=f"mcp_output_{tool_name}",
                    output=output
                )
            except Exception as e:
                logger.warning(f"Langfuse记录失败: {e}")
                
    def log_error(self, error: Exception):
        """记录错误"""
        if not self.enabled:
            return
            
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "error",
            "error": str(error),
            "error_type": type(error).__name__,
            "session_id": self.current_session_id
        }
        
        self.logs.append(log_entry)
        logger.error(f"错误: {error}")
        
        if self.langfuse_enabled and self.langfuse:
            try:
                self.langfuse.trace(
                    name="error",
                    input=str(error)
                )
            except Exception as e:
                logger.warning(f"Langfuse记录失败: {e}")
                
    def get_logs(self, session_id: str = None) -> List[Dict[str, Any]]:
        """获取所有日志，可选择按会话ID过滤"""
        if session_id:
            return [log for log in self.logs if log.get("session_id") == session_id]
        return self.logs.copy()
        
    def get_sessions(self) -> List[Dict[str, Any]]:
        """获取所有会话信息"""
        sessions = {}
        for log in self.logs:
            session_id = log.get("session_id")
            if session_id and session_id not in sessions:
                sessions[session_id] = {
                    "session_id": session_id,
                    "start_time": log.get("timestamp"),
                    "log_count": 0
                }
            if session_id:
                sessions[session_id]["log_count"] += 1
                
        # 更新每个会话的结束时间
        for log in reversed(self.logs):
            session_id = log.get("session_id")
            if session_id and "end_time" not in sessions[session_id]:
                sessions[session_id]["end_time"] = log.get("timestamp")
                
        return list(sessions.values())
        
    def clear_logs(self):
        """清空日志"""
        self.logs.clear()
        
    def save_logs(self, filepath: str):
        """保存日志到文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, ensure_ascii=False, indent=2)
            logger.info(f"日志已保存到 {filepath}")
        except Exception as e:
            logger.error(f"保存日志失败: {e}")