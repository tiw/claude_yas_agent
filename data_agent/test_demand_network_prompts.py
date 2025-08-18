#!/usr/bin/env python3
"""
测试需求网络分析的prompt
"""

from data_agent.prompts.prompt_manager import PromptManager


def test_demand_network_prompts():
    """测试需求网络分析的prompt"""
    print("测试需求网络分析的prompt...")
    
    # 创建prompt管理器
    prompt_manager = PromptManager()
    
    # 测试获取需求网络查询解析prompt
    query_parser_prompt = prompt_manager.get_prompt("demand_network_query_parser")
    print(f"需求网络查询解析prompt长度: {len(query_parser_prompt)} 字符")
    print(f"是否包含需求网络工具: {'demand_network_analysis' in query_parser_prompt}")
    print(f"是否包含市场需求预测: {'market_demand_forecasting' in query_parser_prompt}")
    
    # 测试获取需求网络响应生成prompt
    response_generator_prompt = prompt_manager.get_prompt("demand_network_response_generator")
    print(f"\n需求网络响应生成prompt长度: {len(response_generator_prompt)} 字符")
    print(f"是否包含市场趋势: {'market_trends' in response_generator_prompt}")
    print(f"是否包含需求预测: {'demand_forecast' in response_generator_prompt}")
    
    # 测试默认prompt仍然可用
    default_query_parser = prompt_manager.get_prompt("query_parser")
    print(f"\n默认查询解析prompt长度: {len(default_query_parser)} 字符")
    print(f"是否包含SEC工具: {'sec_financial_data_query' in default_query_parser}")
    
    print("\n测试完成!")


if __name__ == "__main__":
    test_demand_network_prompts()