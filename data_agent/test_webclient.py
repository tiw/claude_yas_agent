#!/usr/bin/env python3
"""
Web客户端功能测试脚本
"""

import asyncio
import aiohttp
import json

async def test_web_client():
    """测试Web客户端功能"""
    base_url = "http://localhost:8080"
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. 测试健康检查接口
            print("1. 测试健康检查接口...")
            async with session.get(f"{base_url}/api/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"   ✓ 健康检查成功: {data}")
                else:
                    print(f"   ✗ 健康检查失败: {resp.status}")
            
            # 2. 测试聊天接口
            print("\n2. 测试聊天接口...")
            test_message = "分析苹果公司最近一季度的财务数据"
            async with session.post(
                f"{base_url}/api/chat",
                json={"message": test_message}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"   ✓ 聊天接口成功")
                    print(f"   响应: {str(data['response'])[:100]}...")
                else:
                    print(f"   ✗ 聊天接口失败: {resp.status}")
                    error_data = await resp.json()
                    print(f"   错误: {error_data}")
            
            # 3. 测试WebSocket连接
            print("\n3. 测试WebSocket连接...")
            try:
                async with session.ws_connect(f"{base_url}/api/ws") as ws:
                    print("   ✓ WebSocket连接成功")
                    
                    # 发送测试消息
                    test_msg = {"message": "获取特斯拉的实时股价"}
                    await ws.send_str(json.dumps(test_msg))
                    print("   ✓ 发送测试消息")
                    
                    # 等待响应
                    msg = await asyncio.wait_for(ws.receive(), timeout=10.0)
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        print(f"   ✓ 收到WebSocket响应: {str(data)[:100]}...")
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        print(f"   ✗ WebSocket错误: {ws.exception()}")
                    
                    await ws.close()
            except asyncio.TimeoutError:
                print("   ✗ WebSocket连接超时")
            except Exception as e:
                print(f"   ✗ WebSocket测试失败: {e}")
                
        except Exception as e:
            print(f"测试过程中出现错误: {e}")

if __name__ == "__main__":
    print("开始测试Web客户端功能...")
    asyncio.run(test_web_client())
    print("\n测试完成。")