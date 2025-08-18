#!/usr/bin/env python3
"""
测试增强的内存管理器
"""

import asyncio
import json
from data_agent.enhanced_memory import AgentMemory


async def test_enhanced_memory():
    """测试增强的内存管理器"""
    print("测试增强的内存管理器...")
    
    # 创建内存管理器
    memory = AgentMemory()
    
    # 开始新会话
    session_id = memory.start_session()
    print(f"开始新会话: {session_id}")
    
    # 添加对话历史
    memory.add_message("user", "你好，我想分析一个文件")
    memory.add_message("assistant", "好的，请上传文件")
    memory.add_message("user", "我已经上传了一个销售数据文件")
    
    # 记住文件信息
    memory.remember_file_upload("sales_data.csv", {
        "content_preview": "日期,销售额,产品类型\n2023-01-01,1000,电子产品",
        "file_path": "/uploads/sales_data.csv",
        "size": 10240
    })
    
    # 获取最近历史
    recent_history = memory.get_recent_history(3)
    print(f"最近对话历史: {len(recent_history)} 条")
    for msg in recent_history:
        print(f"  {msg['role']}: {msg['content'][:50]}...")
    
    # 获取文件信息
    file_info = memory.get_file_info("sales_data.csv")
    print(f"文件信息: {file_info}")
    
    # 获取上下文窗口
    context_window = memory.get_context_window(1000)
    print(f"上下文窗口: {len(context_window)} 条消息")
    
    # 设置用户偏好
    memory.set_user_preference("default_model", "qwen-plus")
    memory.set_user_preference("language", "zh-CN")
    
    # 获取用户偏好
    model = memory.get_user_preference("default_model")
    language = memory.get_user_preference("language")
    print(f"用户偏好 - 模型: {model}, 语言: {language}")
    
    # 获取会话列表
    sessions = memory.get_session_list()
    print(f"会话列表: {len(sessions)} 个会话")
    
    print("测试完成!")


if __name__ == "__main__":
    asyncio.run(test_enhanced_memory())