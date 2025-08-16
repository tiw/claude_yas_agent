#!/usr/bin/env python3
"""
测试会话调试功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_agent.utils.debug import DebugManager

async def test_session_debug():
    """测试会话调试功能"""
    print("测试会话调试功能...")
    
    # 创建调试管理器
    debug_manager = DebugManager(enabled=True)
    
    # 开始第一个会话
    session1_id = debug_manager.start_new_session()
    print(f"开始会话1: {session1_id}")
    
    # 记录一些日志
    debug_manager.log_llm_input("这是第一个会话的LLM输入")
    debug_manager.log_llm_output("这是第一个会话的LLM输出")
    debug_manager.log_mcp_input("test_tool", {"param": "value1"})
    
    # 开始第二个会话
    session2_id = debug_manager.start_new_session()
    print(f"开始会话2: {session2_id}")
    
    # 记录一些日志
    debug_manager.log_llm_input("这是第二个会话的LLM输入")
    debug_manager.log_mcp_input("test_tool2", {"param": "value2"})
    debug_manager.log_error(Exception("这是第二个会话的错误"))
    
    # 测试获取所有日志
    all_logs = debug_manager.get_logs()
    print(f"所有日志数量: {len(all_logs)}")
    
    # 测试按会话获取日志
    session1_logs = debug_manager.get_logs(session1_id)
    print(f"会话1日志数量: {len(session1_logs)}")
    
    session2_logs = debug_manager.get_logs(session2_id)
    print(f"会话2日志数量: {len(session2_logs)}")
    
    # 测试获取会话信息
    sessions = debug_manager.get_sessions()
    print(f"会话数量: {len(sessions)}")
    for session in sessions:
        print(f"  会话ID: {session['session_id']}, 日志数: {session['log_count']}")

if __name__ == "__main__":
    asyncio.run(test_session_debug())