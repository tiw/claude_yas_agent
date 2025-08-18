import json
import os
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
import uuid


class ConversationMemory:
    """对话记忆管理器，管理短期对话历史"""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.history = []
        
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """添加消息到对话历史"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "id": str(uuid.uuid4())
        }
        
        if metadata:
            message["metadata"] = metadata
            
        self.history.append(message)
        
        # 保持历史记录在限制范围内
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
            
    def get_recent_history(self, count: int = None) -> List[Dict[str, Any]]:
        """获取最近的对话历史"""
        if count is None:
            return self.history.copy()
        return self.history[-count:] if len(self.history) >= count else self.history.copy()
        
    def clear_history(self):
        """清空对话历史"""
        self.history.clear()
        
    def get_context_window(self, token_limit: int = 4000) -> List[Dict[str, Any]]:
        """根据token限制获取上下文窗口"""
        # 简单的字符计数来估算token数量
        context = []
        total_chars = 0
        
        # 从最新消息开始，向后添加历史消息
        for message in reversed(self.history):
            message_chars = len(message["content"])
            if total_chars + message_chars > token_limit:
                break
            context.append(message)
            total_chars += message_chars
            
        # 保持时间顺序
        return list(reversed(context))


class PersistentSessionManager:
    """持久化会话管理器，管理长期记忆和会话持久化"""
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            self.storage_path = Path.home() / ".data_agent" / "sessions"
        else:
            self.storage_path = Path(storage_path)
            
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.current_session_file = None
        
    def start_new_session(self, session_id: str = None) -> str:
        """开始新的会话"""
        if session_id is None:
            session_id = str(uuid.uuid4())
            
        self.current_session_file = self.storage_path / f"session_{session_id}.json"
        return session_id
        
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """加载会话数据"""
        session_file = self.storage_path / f"session_{session_id}.json"
        if session_file.exists():
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return None
        return None
        
    def save_session(self, session_id: str, data: Dict[str, Any]):
        """保存会话数据"""
        session_file = self.storage_path / f"session_{session_id}.json"
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存会话失败: {e}")
            
    def get_session_list(self) -> List[Dict[str, Any]]:
        """获取所有会话列表"""
        sessions = []
        for file_path in self.storage_path.glob("session_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session_info = {
                        "session_id": file_path.stem.replace("session_", ""),
                        "created_at": data.get("created_at", ""),
                        "message_count": len(data.get("conversation_history", [])),
                        "file_name": file_path.name
                    }
                    sessions.append(session_info)
            except Exception:
                continue
        return sessions


class AgentMemory:
    """增强的Agent内存管理器，整合短期和长期记忆"""
    
    def __init__(self, project_root: str = ".", max_conversation_history: int = 10):
        # 短期记忆（对话历史）
        self.conversation_memory = ConversationMemory(max_history=max_conversation_history)
        
        # 长期记忆（持久化会话）
        self.session_manager = PersistentSessionManager()
        
        # 项目相关信息（从CLAUDE.md等加载）
        self.project_memory = {}
        
        # 用户偏好和设置
        self.user_preferences = {}
        
        self.project_root = Path(project_root)
        self.current_session_id = None
        self._load_project_memory()
        self._load_user_preferences()
        
    def _load_project_memory(self):
        """加载项目相关信息"""
        claude_file = self.project_root / "CLAUDE.md"
        if claude_file.exists():
            try:
                with open(claude_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.project_memory["project_info"] = content
            except Exception:
                pass
                
    def _load_user_preferences(self):
        """加载用户偏好设置"""
        user_prefs_file = Path.home() / ".data_agent" / "user_preferences.json"
        if user_prefs_file.exists():
            try:
                with open(user_prefs_file, 'r', encoding='utf-8') as f:
                    self.user_preferences = json.load(f)
            except Exception:
                pass
                
    def _save_user_preferences(self):
        """保存用户偏好设置"""
        user_prefs_dir = Path.home() / ".data_agent"
        user_prefs_dir.mkdir(exist_ok=True)
        user_prefs_file = user_prefs_dir / "user_preferences.json"
        
        try:
            with open(user_prefs_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
            
    def start_session(self, session_id: str = None) -> str:
        """开始新的会话"""
        self.current_session_id = self.session_manager.start_new_session(session_id)
        
        # 如果是现有会话，加载历史数据
        if session_id:
            session_data = self.session_manager.load_session(session_id)
            if session_data:
                # 恢复对话历史
                history = session_data.get("conversation_history", [])
                for msg in history:
                    self.conversation_memory.add_message(
                        msg["role"], 
                        msg["content"], 
                        msg.get("metadata")
                    )
        
        return self.current_session_id
        
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """添加消息到对话历史"""
        self.conversation_memory.add_message(role, content, metadata)
        self._save_current_session()
        
    def get_recent_history(self, count: int = None) -> List[Dict[str, Any]]:
        """获取最近的对话历史"""
        return self.conversation_memory.get_recent_history(count)
        
    def get_context_window(self, token_limit: int = 4000) -> List[Dict[str, Any]]:
        """获取上下文窗口"""
        return self.conversation_memory.get_context_window(token_limit)
        
    def _save_current_session(self):
        """保存当前会话"""
        if self.current_session_id:
            session_data = {
                "session_id": self.current_session_id,
                "created_at": datetime.now().isoformat(),
                "conversation_history": self.conversation_memory.history,
                "project_memory": self.project_memory,
                "user_preferences": self.user_preferences
            }
            self.session_manager.save_session(self.current_session_id, session_data)
            
    def set_user_preference(self, key: str, value: Any):
        """设置用户偏好"""
        self.user_preferences[key] = value
        self._save_user_preferences()
        
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """获取用户偏好"""
        return self.user_preferences.get(key, default)
        
    def remember_file_upload(self, filename: str, file_info: Dict[str, Any]):
        """记住文件上传信息"""
        if "uploaded_files" not in self.user_preferences:
            self.user_preferences["uploaded_files"] = {}
            
        self.user_preferences["uploaded_files"][filename] = {
            "info": file_info,
            "timestamp": datetime.now().isoformat()
        }
        self._save_user_preferences()
        
    def get_file_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """获取文件信息"""
        uploaded_files = self.user_preferences.get("uploaded_files", {})
        return uploaded_files.get(filename)
        
    def clear_conversation_history(self):
        """清空对话历史"""
        self.conversation_memory.clear_history()
        self._save_current_session()
        
    def get_session_list(self) -> List[Dict[str, Any]]:
        """获取会话列表"""
        return self.session_manager.get_session_list()