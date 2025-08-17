#!/usr/bin/env python3
"""
系统状态检查工具
用于检查数据分析Agent的依赖和MCP服务状态
"""

import asyncio
import sys
import os
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_agent.agent import DataAnalysisAgent, AgentConfig
from data_agent.mcp_tools.mcp_client import MCPClient

async def check_system_status():
    """检查系统状态"""
    print("=== 数据分析Agent系统状态检查 ===\n")
    
    # 1. 检查Agent初始化
    print("1. 检查Agent初始化...")
    try:
        config = AgentConfig(
            debug_mode=True,
            langfuse_enabled=False,
            default_llm="qwen"
        )
        agent = DataAnalysisAgent(config)
        print("   ✓ Agent初始化成功")
    except Exception as e:
        print(f"   ✗ Agent初始化失败: {e}")
        return False
    
    # 2. 检查MCP客户端
    print("\n2. 检查MCP客户端...")
    try:
        if agent.mcp_client:
            print("   ✓ MCP客户端初始化成功")
            
            # 检查服务器信息
            if hasattr(agent.mcp_client, 'server_info'):
                servers = agent.mcp_client.server_info
                print(f"   ✓ 发现 {len(servers)} 个MCP服务器:")
                for server_name, server_info in servers.items():
                    healthy = server_info.get('healthy', False)
                    status = "✓ 健康" if healthy else "✗ 不健康"
                    print(f"     - {server_name}: {status} ({server_info.get('url', 'N/A')})")
            else:
                print("   ! 无法获取服务器信息")
        else:
            print("   ✗ MCP客户端未初始化")
    except Exception as e:
        print(f"   ✗ MCP客户端检查失败: {e}")
    
    # 3. 检查可用工具
    print("\n3. 检查可用工具...")
    try:
        if agent.mcp_client:
            tools = agent.mcp_client.get_available_tools()
            print(f"   ✓ 可用工具数量: {len(tools)}")
            print(f"   工具列表: {', '.join(tools[:10])}{'...' if len(tools) > 10 else ''}")
        else:
            print("   ✗ MCP客户端不可用，无法获取工具列表")
    except Exception as e:
        print(f"   ✗ 获取工具列表失败: {e}")
    
    # 4. 检查LLM管理器
    print("\n4. 检查LLM管理器...")
    try:
        if agent.llm_manager:
            print("   ✓ LLM管理器初始化成功")
            print(f"   默认模型: {agent.config.default_llm}")
        else:
            print("   ✗ LLM管理器未初始化")
    except Exception as e:
        print(f"   ✗ LLM管理器检查失败: {e}")
    
    # 5. 检查调试管理器
    print("\n5. 检查调试管理器...")
    try:
        if agent.debug_manager:
            print("   ✓ 调试管理器初始化成功")
            print(f"   调试模式: {'启用' if agent.config.debug_mode else '禁用'}")
        else:
            print("   ✗ 调试管理器未初始化")
    except Exception as e:
        print(f"   ✗ 调试管理器检查失败: {e}")
    
    print("\n=== 状态检查完成 ===")
    return True

async def check_mcp_connectivity():
    """检查MCP服务连通性"""
    print("\n=== MCP服务连通性检查 ===\n")
    
    # 使用默认配置创建MCP客户端
    mcp_config = {
        "mcpServers": {
            "sec-fetch-production": {
                "type": "sse",
                "url": "http://localhost:8000/mcp",
                "headers": {},
                "serverInstructions": "SEC财报数据分析服务"
            },
            "sec-investment-analysis": {
                "type": "sse",
                "url": "http://localhost:8001/mcp",
                "headers": {},
                "serverInstructions": "SEC投资分析服务"
            },
            "sec-stock-query": {
                "type": "sse",
                "url": "http://localhost:8002/mcp",
                "headers": {},
                "serverInstructions": "Alpha Vantage股票查询服务"
            }
        }
    }
    
    try:
        async with MCPClient(mcp_config) as mcp_client:
            print("✓ MCP客户端连接成功")
            
            # 显示服务器状态
            for server_name, server_info in mcp_client.server_info.items():
                healthy = server_info.get('healthy', False)
                status = "✓ 健康" if healthy else "✗ 不健康"
                print(f"  {server_name}: {status} ({server_info.get('url', 'N/A')})")
                
                if healthy:
                    # 尝试获取服务器说明
                    instructions = server_info.get('instructions', '')
                    if instructions:
                        print(f"    说明: {instructions[:50]}{'...' if len(instructions) > 50 else ''}")
                
    except Exception as e:
        print(f"✗ MCP服务连通性检查失败: {e}")

def main():
    """主函数"""
    print("数据分析Agent系统诊断工具")
    print("=" * 40)
    
    # 检查系统状态
    success = asyncio.run(check_system_status())
    
    # 检查MCP连通性
    asyncio.run(check_mcp_connectivity())
    
    if success:
        print("\n✓ 系统检查完成，Agent可以正常工作")
        return 0
    else:
        print("\n✗ 系统检查发现问题，请检查上述错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())