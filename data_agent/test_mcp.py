#!/usr/bin/env python3
"""
MCP集成测试
测试与实际MCP服务的集成
"""

import asyncio
import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_agent.agent import DataAnalysisAgent, AgentConfig
from data_agent.mcp_tools.mcp_client import MCPClient

# 配置日志
logging.basicConfig(level=logging.INFO)

async def test_mcp_client():
    """测试MCP客户端"""
    print("开始测试MCP客户端...")
    
    # 创建MCP配置
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
    
    # 测试MCP客户端初始化
    print("\n--- 测试MCP客户端初始化 ---")
    try:
        async with MCPClient(mcp_config) as mcp_client:
            print("MCP客户端初始化成功")
            
            # 获取可用工具
            tools = mcp_client.get_available_tools()
            print(f"可用工具数量: {len(tools)}")
            print(f"部分工具: {tools[:5]}")
            
            # 获取服务器说明
            instructions = mcp_client.get_server_instructions()
            print(f"服务器说明数量: {len(instructions)}")
            
    except Exception as e:
        print(f"MCP客户端测试失败: {e}")

async def test_mcp_with_agent():
    """测试Agent与MCP的集成"""
    print("\n--- 测试Agent与MCP集成 ---")
    
    try:
        # 配置Agent
        config = AgentConfig(
            debug_mode=True,
            langfuse_enabled=False,
            default_llm="qwen"
        )
        
        agent = DataAnalysisAgent(config)
        
        # 测试查询解析（模拟MCP工具调用）
        test_queries = [
            "查询苹果公司最近一季度的财务数据",
            "分析巴菲特可能会投资的股票",
            "获取特斯拉的实时股价和技术分析"
        ]
        
        for query in test_queries:
            print(f"\n测试查询: {query}")
            try:
                # 注意：实际的MCP服务可能需要API密钥才能正常工作
                result = await agent.process_query(query)
                print("处理结果:")
                print(result[:200] + "..." if len(result) > 200 else result)
            except Exception as e:
                print(f"处理查询时出错: {e}")
                
    except Exception as e:
        print(f"Agent与MCP集成测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_client())
    asyncio.run(test_mcp_with_agent())