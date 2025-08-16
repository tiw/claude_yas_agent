#!/usr/bin/env python3
"""
测试调试监控功能
"""

import asyncio
import aiohttp
import json

async def test_debug_api():
    """测试调试API端点"""
    base_url = "http://localhost:8082"
    
    async with aiohttp.ClientSession() as session:
        # 测试健康检查
        try:
            async with session.get(f"{base_url}/api/health") as resp:
                health_data = await resp.json()
                print("健康检查:", health_data)
        except Exception as e:
            print("健康检查失败:", e)
            return
        
        # 测试获取调试日志
        try:
            async with session.get(f"{base_url}/api/debug/logs") as resp:
                logs_data = await resp.json()
                print("调试日志:", logs_data)
        except Exception as e:
            print("获取调试日志失败:", e)
        
        # 测试发送聊天消息
        try:
            chat_data = {"message": "分析苹果公司最近的财务数据"}
            async with session.post(f"{base_url}/api/chat", json=chat_data) as resp:
                chat_response = await resp.json()
                print("聊天响应:", chat_response)
        except Exception as e:
            print("发送聊天消息失败:", e)
        
        # 再次获取调试日志，查看是否有新增日志
        try:
            async with session.get(f"{base_url}/api/debug/logs") as resp:
                logs_data = await resp.json()
                print("更新后的调试日志数量:", len(logs_data.get("logs", [])))
        except Exception as e:
            print("获取更新后的调试日志失败:", e)

if __name__ == "__main__":
    asyncio.run(test_debug_api())