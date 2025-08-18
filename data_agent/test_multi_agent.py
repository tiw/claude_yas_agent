#!/usr/bin/env python3
"""
测试多Agent功能
"""

import asyncio
from data_agent.agent import AgentConfig, DataAnalysisAgent
from data_agent.demand_network_agent import DemandNetworkAgentConfig, DemandNetworkAnalysisAgent
from data_agent.multi_agent import SubAgentManager, AgentType


async def test_multi_agent():
    """测试多Agent功能"""
    print("测试多Agent功能...")
    
    # 创建主Agent
    config = AgentConfig(debug_mode=True)
    main_agent = DataAnalysisAgent(config)
    
    # 创建子Agent管理器
    sub_agent_manager = SubAgentManager(main_agent)
    
    # 注册需求网络分析Agent
    demand_config = DemandNetworkAgentConfig(debug_mode=True)
    demand_agent = DemandNetworkAnalysisAgent(demand_config)
    sub_agent_manager.register_sub_agent("demand_network", demand_agent, AgentType.DEMAND_NETWORK)
    
    # 测试Agent切换
    print("1. 测试主Agent...")
    result1 = await sub_agent_manager.execute_with_current_agent("分析苹果公司的财务数据")
    print(f"主Agent结果: {result1[:100]}...")
    
    print("\n2. 切换到需求网络分析Agent...")
    sub_agent_manager.switch_agent("demand_network")
    current_info = sub_agent_manager.get_current_agent_info()
    print(f"当前Agent信息: {current_info}")
    
    print("\n3. 测试需求网络分析Agent...")
    result2 = await sub_agent_manager.execute_with_current_agent("分析智能手机市场的需求趋势")
    print(f"需求网络分析Agent结果: {result2[:100]}...")
    
    print("\n4. 切换回主Agent...")
    sub_agent_manager.switch_agent("main")
    current_info = sub_agent_manager.get_current_agent_info()
    print(f"当前Agent信息: {current_info}")
    
    print("\n5. 测试主Agent again...")
    result3 = await sub_agent_manager.execute_with_current_agent("获取特斯拉的股票价格")
    print(f"主Agent结果: {result3[:100]}...")
    
    print("\n测试完成!")


if __name__ == "__main__":
    asyncio.run(test_multi_agent())