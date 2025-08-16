import os
import httpx
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class QwenLLM:
    """Qwen LLM 集成"""
    
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY not found in environment variables")
        
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.model = "qwen-max"  # 默认模型
    
    async def generate(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """调用Qwen生成文本"""
        # 构建完整的提示词
        full_prompt = self._build_prompt(prompt, context)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": {
                "prompt": full_prompt
            },
            "parameters": {
                "max_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.8
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.base_url, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                
                result = response.json()
                if "output" in result and "text" in result["output"]:
                    # 尝试解析返回的JSON，如果失败则返回原始文本
                    try:
                        return json.loads(result["output"]["text"])
                    except json.JSONDecodeError:
                        # 如果不是JSON格式，返回包含文本的字典
                        return {"response": result["output"]["text"]}
                else:
                    raise ValueError("Unexpected response format from Qwen API")
                    
            except Exception as e:
                raise Exception(f"Qwen API call failed: {str(e)}")
    
    def _build_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """构建完整的提示词"""
        # 将上下文转换为JSON字符串并添加到提示词中
        context_str = json.dumps(context, ensure_ascii=False, indent=2)
        return f"{prompt}\n\n上下文信息:\n{context_str}\n\n请以JSON格式返回结果。"