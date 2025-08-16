#!/usr/bin/env python3
"""
数据分析Agent使用示例
展示如何使用DataAnalysisAgent进行复杂的数据分析任务
"""

import asyncio
import logging
from data_agent.agent import DataAnalysisAgent, AgentConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def demo_complex_analysis():
    """演示复杂数据分析"""
    print("数据分析Agent演示")
    print("=" * 50)
    
    # 配置Agent
    config = AgentConfig(
        mcp_endpoints=["http://localhost:8000/api", "http://localhost:8001/api"],
        debug_mode=True,
        langfuse_enabled=False
    )
    
    # 创建Agent实例
    agent = DataAnalysisAgent(config)
    
    # 复杂查询示例
    queries = [
        "帮我分析最近30天的销售数据，按周分组",
        "查看最近一周的用户活跃度，并与上个月同期对比",
        "分析产品A和产品B在过去三个月的performance，并给出建议",
        "查看最近几天的订单量趋势"
    ]
    
    # 处理查询
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}] 用户查询: {query}")
        print("-" * 30)
        
        result = await agent.process_query(query)
        print(f"Agent回复:\n{result}")
        
        # 显示调试信息摘要
        print("\n调试信息:")
        llm_inputs = [log for log in agent.debug_manager.logs if log['type'] == 'llm_input']
        llm_outputs = [log for log in agent.debug_manager.logs if log['type'] == 'llm_output']
        mcp_calls = [log for log in agent.debug_manager.logs if log['type'] == 'mcp_input']
        
        print(f"  - LLM调用: {len(llm_inputs)} 次")
        print(f"  - MCP调用: {len(mcp_calls)} 次")
        print(f"  - 总日志条数: {len(agent.debug_manager.logs)}")
        
        # 清空日志以准备下一个查询
        agent.debug_manager.clear_logs()

async def demo_error_recovery():
    """演示错误恢复功能"""
    print("\n\n错误恢复功能演示")
    print("=" * 50)
    
    # 配置Agent
    config = AgentConfig(
        mcp_endpoints=["http://localhost:8000/api"],
        debug_mode=True,
        langfuse_enabled=False
    )
    
    # 创建Agent实例
    agent = DataAnalysisAgent(config)
    
    # 模拟一个可能出错的查询
    query = "获取不存在的工具数据"
    print(f"用户查询: {query}")
    print("-" * 30)
    
    result = await agent.process_query(query)
    print(f"Agent回复:\n{result}")
    
    # 显示错误日志
    error_logs = [log for log in agent.debug_manager.logs if log['type'] == 'error']
    if error_logs:
        print("\n错误处理:")
        for log in error_logs:
            print(f"  - 错误类型: {log['error_type']}")
            print(f"    错误信息: {log['error']}")

if __name__ == "__main__":
    asyncio.run(demo_complex_analysis())
    asyncio.run(demo_error_recovery())