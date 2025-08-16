import os
import httpx
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class DeepSeekLLM:
    """DeepSeek LLM 集成"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
        
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"  # 默认模型
    
    async def generate(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """调用DeepSeek生成文本"""
        # 构建完整的提示词
        full_prompt = self._build_prompt(prompt, context)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = [
            {
                "role": "user",
                "content": full_prompt
            }
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream": False
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.base_url, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    # 尝试解析返回的JSON，如果失败则返回原始文本
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        # 如果不是JSON格式，返回包含文本的字典
                        return {"response": content}
                else:
                    raise ValueError("Unexpected response format from DeepSeek API")
                    
            except Exception as e:
                raise Exception(f"DeepSeek API call failed: {str(e)}")
    
    def _build_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """构建完整的提示词"""
        # 将上下文转换为JSON字符串并添加到提示词中
        context_str = json.dumps(context, ensure_ascii=False, indent=2)
        return f"{prompt}\n\n上下文信息:\n{context_str}\n\n请以JSON格式返回结果。"