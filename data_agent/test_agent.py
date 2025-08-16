"""
数据分析Agent测试
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

async def test_basic_functionality():
    """测试基本功能"""
    print("开始测试数据分析Agent...")
    
    # 配置Agent
    config = AgentConfig(
        mcp_endpoints=["http://localhost:8000/api"],
        debug_mode=True,
        langfuse_enabled=False
    )
    
    # 创建Agent实例
    agent = DataAnalysisAgent(config)
    
    # 测试用例
    test_cases = [
        "查看最近7天的销售数据",
        "分析用户行为数据",
        "比较两个产品的性能"
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n--- 测试用例 {i}: {query} ---")
        try:
            result = await agent.process_query(query)
            print("处理结果:")
            print(result[:200] + "..." if len(result) > 200 else result)
            
            # 检查是否有错误日志
            error_logs = [log for log in agent.debug_manager.logs if log['type'] == 'error']
            if error_logs:
                print(f"警告: 发现 {len(error_logs)} 个错误日志")
        except Exception as e:
            print(f"测试失败: {e}")
    
    print("\n--- 测试完成 ---")
    
    # 显示调试信息统计
    log_types = {}
    for log in agent.debug_manager.logs:
        log_type = log['type']
        log_types[log_type] = log_types.get(log_type, 0) + 1
    
    print("调试日志统计:")
    for log_type, count in log_types.items():
        print(f"  {log_type}: {count}")

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())