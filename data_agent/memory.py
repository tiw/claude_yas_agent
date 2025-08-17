import json
import os
from typing import Any, Dict, List, Optional
from pathlib import Path

class MemoryManager:
    """内存管理器，实现多层级内存管理机制"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.claude_file = self.project_root / "CLAUDE.md"
        self.memory_data = {
            "enterprise_policy": {},
            "project_memory": {},
            "user_memory": {},
            "local_project_memory": {}
        }
        self._load_memory()
    
    def _load_memory(self):
        """加载内存数据"""
        # 从CLAUDE.md加载项目信息
        if self.claude_file.exists():
            with open(self.claude_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 简单解析CLAUDE.md内容
                self.memory_data["project_memory"]["project_info"] = content
        
        # 加载用户内存（从用户目录）
        user_memory_file = Path.home() / ".data_agent" / "user_memory.json"
        if user_memory_file.exists():
            try:
                with open(user_memory_file, 'r', encoding='utf-8') as f:
                    self.memory_data["user_memory"] = json.load(f)
            except Exception:
                pass
    
    def _save_user_memory(self):
        """保存用户内存"""
        user_memory_dir = Path.home() / ".data_agent"
        user_memory_dir.mkdir(exist_ok=True)
        user_memory_file = user_memory_dir / "user_memory.json"
        
        with open(user_memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory_data["user_memory"], f, ensure_ascii=False, indent=2)
    
    def get_memory(self, layer: str, key: str = None) -> Any:
        """获取指定层的内存数据"""
        if layer not in self.memory_data:
            return None
            
        if key:
            return self.memory_data[layer].get(key)
        return self.memory_data[layer]
    
    def set_memory(self, layer: str, key: str, value: Any):
        """设置指定层的内存数据"""
        if layer in self.memory_data:
            self.memory_data[layer][key] = value
            # 如果是用户内存，保存到文件
            if layer == "user_memory":
                self._save_user_memory()
    
    def update_project_info(self, project_info: str):
        """更新项目信息到CLAUDE.md"""
        with open(self.claude_file, 'w', encoding='utf-8') as f:
            f.write(project_info)
        self.memory_data["project_memory"]["project_info"] = project_info
    
    def get_project_structure(self) -> Dict[str, Any]:
        """获取项目结构信息"""
        return {
            "files": self._get_file_structure(),
            "encoding_standards": self.memory_data["project_memory"].get("encoding_standards", {}),
            "common_commands": self.memory_data["project_memory"].get("common_commands", []),
            "workflows": self.memory_data["project_memory"].get("workflows", [])
        }
    
    def _get_file_structure(self) -> List[str]:
        """获取文件结构"""
        files = []
        for root, dirs, filenames in os.walk(self.project_root):
            # 跳过常见的隐藏目录和虚拟环境
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__', 'node_modules']]
            
            for filename in filenames:
                if not filename.startswith('.'):
                    files.append(os.path.relpath(os.path.join(root, filename), self.project_root))
        
        return files