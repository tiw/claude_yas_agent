#!/usr/bin/env python3
"""
LLM集成测试
测试Qwen和DeepSeek的集成
"""

import asyncio
import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_agent.agent import DataAnalysisAgent, AgentConfig

# 配置日志
logging.basicConfig(level=logging.INFO)

async def test_llm_integration():
    """测试LLM集成"""
    print("开始测试LLM集成...")
    
    # 测试Qwen
    print("\n--- 测试Qwen ---")
    try:
        config = AgentConfig(
            mcp_endpoints=["http://localhost:8000/api"],
            debug_mode=True,
            langfuse_enabled=False,
            default_llm="qwen"
        )
        
        agent = DataAnalysisAgent(config)
        result = await agent.process_query("你是谁？")
        print("Qwen回复:")
        print(result[:200] + "..." if len(result) > 200 else result)
    except Exception as e:
        print(f"Qwen测试失败: {e}")
    
    # 测试DeepSeek
    print("\n--- 测试DeepSeek ---")
    try:
        config = AgentConfig(
            mcp_endpoints=["http://localhost:8000/api"],
            debug_mode=True,
            langfuse_enabled=False,
            default_llm="deepseek"
        )
        
        agent = DataAnalysisAgent(config)
        result = await agent.process_query("你是谁？")
        print("DeepSeek回复:")
        print(result[:200] + "..." if len(result) > 200 else result)
    except Exception as e:
        print(f"DeepSeek测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm_integration())