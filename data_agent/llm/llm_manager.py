import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
import httpx

# 加载环境变量
load_dotenv()

class LLMManager:
    """LLM管理器，支持多种大语言模型"""
    
    def __init__(self, default_model: str = "qwen"):
        self.default_model = default_model
        self.qwen_client = None
        self.deepseek_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """初始化LLM客户端"""
        # 初始化Qwen客户端
        dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
        if dashscope_api_key:
            self.qwen_client = OpenAI(
                api_key=dashscope_api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
        
        # 初始化DeepSeek客户端
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_api_key:
            self.deepseek_client = OpenAI(
                api_key=deepseek_api_key,
                base_url="https://api.deepseek.com"
            )
    
    async def generate(self, prompt: str, context: Dict[str, Any], model: Optional[str] = None) -> Dict[str, Any]:
        """调用指定的LLM生成文本"""
        if model is None:
            model = self.default_model
        
        if model == "qwen":
            return await self._call_qwen(prompt, context)
        elif model == "deepseek":
            return await self._call_deepseek(prompt, context)
        else:
            # 默认使用模拟实现
            return await self._call_mock_llm(prompt, context)
    
    async def _call_qwen(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """调用Qwen"""
        if not self.qwen_client:
            raise ValueError("Qwen client not initialized. Please check DASHSCOPE_API_KEY.")
        
        try:
            # 构建消息
            context_str = json.dumps(context, ensure_ascii=False, indent=2)
            full_prompt = f"{prompt}\n\n上下文信息:\n{context_str}\n\n请以JSON格式返回结果。"
            
            completion = self.qwen_client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": "你是一个数据分析助手，请以JSON格式返回结果。"},
                    {"role": "user", "content": full_prompt},
                ],
                extra_body={"enable_thinking": False},
                temperature=0.7,
                max_tokens=2048
            )
            
            response_content = completion.choices[0].message.content
            
            # 尝试解析返回的JSON
            try:
                return json.loads(response_content)
            except json.JSONDecodeError:
                # 如果不是JSON格式，返回包含文本的字典
                return {"response": response_content}
                
        except Exception as e:
            raise Exception(f"Qwen API call failed: {str(e)}")
    
    async def _call_deepseek(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """调用DeepSeek"""
        if not self.deepseek_client:
            raise ValueError("DeepSeek client not initialized. Please check DEEPSEEK_API_KEY.")
        
        try:
            # 构建消息
            context_str = json.dumps(context, ensure_ascii=False, indent=2)
            full_prompt = f"{prompt}\n\n上下文信息:\n{context_str}\n\n请以JSON格式返回结果。"
            
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个数据分析助手，请以JSON格式返回结果。"},
                    {"role": "user", "content": full_prompt},
                ],
                stream=False,
                temperature=0.7,
                max_tokens=2048
            )
            
            response_content = response.choices[0].message.content
            
            # 尝试解析返回的JSON
            try:
                return json.loads(response_content)
            except json.JSONDecodeError:
                # 如果不是JSON格式，返回包含文本的字典
                return {"response": response_content}
                
        except Exception as e:
            raise Exception(f"DeepSeek API call failed: {str(e)}")
    
    async def _call_mock_llm(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """模拟LLM调用（用于测试）"""
        # 模拟LLM返回结构化数据
        return context