#!/usr/bin/env python3
"""
数据分析Agent完整使用示例
展示如何使用支持多种LLM的数据分析Agent
"""

import asyncio
import logging
from data_agent.agent import DataAnalysisAgent, AgentConfig

# 配置日志
logging.basicConfig(level=logging.INFO)

async def main():
    """主函数 - 演示Agent的完整功能"""
    print("数据分析Agent完整功能演示")
    print("=" * 50)
    
    # 1. 使用Qwen进行数据分析
    print("\n[1] 使用Qwen进行数据分析")
    print("-" * 30)
    
    config_qwen = AgentConfig(
        mcp_endpoints=["http://localhost:8000/api"],
        debug_mode=True,
        langfuse_enabled=False,
        default_llm="qwen"
    )
    
    agent_qwen = DataAnalysisAgent(config_qwen)
    result_qwen = await agent_qwen.process_query("帮我分析最近7天的销售数据")
    print("Qwen分析结果:")
    print(result_qwen)
    
    # 2. 使用DeepSeek进行数据分析
    print("\n[2] 使用DeepSeek进行数据分析")
    print("-" * 30)
    
    config_deepseek = AgentConfig(
        mcp_endpoints=["http://localhost:8000/api"],
        debug_mode=True,
        langfuse_enabled=False,
        default_llm="deepseek"
    )
    
    agent_deepseek = DataAnalysisAgent(config_deepseek)
    result_deepseek = await agent_deepseek.process_query("分析用户行为数据")
    print("DeepSeek分析结果:")
    print(result_deepseek)
    
    # 3. 显示调试信息
    print("\n[3] 调试信息摘要")
    print("-" * 30)
    print(f"Qwen Agent日志条数: {len(agent_qwen.debug_manager.logs)}")
    print(f"DeepSeek Agent日志条数: {len(agent_deepseek.debug_manager.logs)}")
    
    # 4. 演示相对时间处理
    print("\n[4] 相对时间表达式处理")
    print("-" * 30)
    
    result_time = await agent_qwen.process_query("查看最近几天的订单趋势")
    print("时间处理结果:")
    print(result_time)

if __name__ == "__main__":
    asyncio.run(main())