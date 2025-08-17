#!/usr/bin/env python3
"""
数据分析Agent统一命令行工具
集成所有CLI功能，包括数据查询、状态检查、测试等
"""

import argparse
import asyncio
import sys
import json
import os
from typing import Optional, List

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_agent.agent import DataAnalysisAgent, AgentConfig
from data_agent.mcp_tools.mcp_client import MCPClient

class UnifiedAgentCLI:
    """统一的Agent命令行界面"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """创建命令行参数解析器"""
        parser = argparse.ArgumentParser(
            prog='data-agent-cli',
            description="数据分析Agent统一命令行工具",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
统一命令行工具，提供以下功能:
  1. 数据分析查询 (query)
  2. 系统状态检查 (status)
  3. MCP连通性测试 (test-mcp)
  4. 投资分析测试 (test-investment)

使用示例:
  # 数据分析查询
  %(prog)s query "分析苹果公司最近的财务数据"
  %(prog)s query --debug "获取特斯拉的实时股价"
  %(prog)s query --model deepseek "比较两家公司的投资价值"
  
  # 系统状态检查
  %(prog)s status
  %(prog)s status --verbose
  
  # MCP连通性测试
  %(prog)s test-mcp
  
  # 投资分析测试
  %(prog)s test-investment
            """
        )
        
        # 添加子命令
        subparsers = parser.add_subparsers(dest='command', help='可用命令')
        
        # 查询命令
        self._add_query_parser(subparsers)
        
        # 状态检查命令
        self._add_status_parser(subparsers)
        
        # MCP测试命令
        self._add_test_mcp_parser(subparsers)
        
        # 投资分析测试命令
        self._add_test_investment_parser(subparsers)
        
        return parser
    
    def _add_query_parser(self, subparsers):
        """添加查询命令解析器"""
        parser_query = subparsers.add_parser('query', help='数据分析查询')
        parser_query.add_argument(
            'query_text',
            nargs='?',
            help='数据分析查询文本'
        )
        parser_query.add_argument(
            '--debug',
            action='store_true',
            help='启用调试模式'
        )
        parser_query.add_argument(
            '--model',
            choices=['qwen', 'deepseek'],
            default='qwen',
            help='指定使用的LLM模型 (默认: qwen)'
        )
        parser_query.add_argument(
            '--format',
            choices=['json', 'text'],
            default='text',
            help='输出格式 (默认: text)'
        )
        parser_query.add_argument(
            '--session',
            help='指定会话ID'
        )
    
    def _add_status_parser(self, subparsers):
        """添加状态检查命令解析器"""
        parser_status = subparsers.add_parser('status', help='系统状态检查')
        parser_status.add_argument(
            '--verbose',
            '-v',
            action='store_true',
            help='显示详细状态信息'
        )
        parser_status.add_argument(
            '--json',
            action='store_true',
            help='以JSON格式输出'
        )
    
    def _add_test_mcp_parser(self, subparsers):
        """添加MCP测试命令解析器"""
        parser_test_mcp = subparsers.add_parser('test-mcp', help='MCP连通性测试')
        parser_test_mcp.add_argument(
            '--json',
            action='store_true',
            help='以JSON格式输出结果'
        )
    
    def _add_test_investment_parser(self, subparsers):
        """添加投资分析测试命令解析器"""
        parser_test_inv = subparsers.add_parser('test-investment', help='投资分析测试')
        parser_test_inv.add_argument(
            '--verbose',
            '-v',
            action='store_true',
            help='显示详细测试结果'
        )
    
    async def run(self, args: Optional[List[str]] = None):
        """运行CLI工具"""
        parsed_args = self.parser.parse_args(args)
        
        # 如果没有指定命令，显示帮助信息
        if not parsed_args.command:
            self.parser.print_help()
            return
        
        try:
            if parsed_args.command == 'query':
                await self._run_query(parsed_args)
            elif parsed_args.command == 'status':
                await self._run_status_check(parsed_args)
            elif parsed_args.command == 'test-mcp':
                await self._run_mcp_test(parsed_args)
            elif parsed_args.command == 'test-investment':
                await self._run_investment_test(parsed_args)
            else:
                print(f"未知命令: {parsed_args.command}")
                self.parser.print_help()
                sys.exit(1)
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
    
    async def _run_query(self, args):
        """运行查询命令"""
        if not args.query_text:
            print("错误: 请提供查询文本")
            print("使用 'data-agent-cli query -h' 查看帮助信息")
            sys.exit(1)
        
        # 配置Agent
        config = AgentConfig(
            debug_mode=args.debug,
            default_llm=args.model
        )
        
        # 创建Agent实例
        agent = DataAnalysisAgent(config)
        
        try:
            # 处理查询
            result = await agent.process_query(args.query_text)
            
            # 格式化输出
            if args.format == 'json':
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(result)
                
        except Exception as e:
            print(f"查询处理失败: {e}", file=sys.stderr)
            sys.exit(1)
    
    async def _run_status_check(self, args):
        """运行状态检查命令"""
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
            sys.exit(1)
        
        # 2. 检查MCP客户端
        print("\n2. 检查MCP客户端...")
        mcp_servers = {}
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
                        url = server_info.get('url', 'N/A')
                        print(f"     - {server_name}: {status} ({url})")
                        mcp_servers[server_name] = {
                            "url": url,
                            "healthy": healthy
                        }
                else:
                    print("   ! 无法获取服务器信息")
            else:
                print("   ✗ MCP客户端未初始化")
        except Exception as e:
            print(f"   ✗ MCP客户端检查失败: {e}")
        
        # 3. 检查可用工具
        print("\n3. 检查可用工具...")
        tools_list = []
        try:
            if agent.mcp_client:
                tools = agent.mcp_client.get_available_tools()
                tools_list = tools
                print(f"   ✓ 可用工具数量: {len(tools)}")
                if args.verbose:
                    print(f"   工具列表: {', '.join(tools)}")
                else:
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
        
        # 如果指定了JSON输出
        if args.json:
            status_info = {
                "agent": "initialized",
                "mcp_client": "available" if agent.mcp_client else "unavailable",
                "llm_manager": "available" if agent.llm_manager else "unavailable",
                "debug_manager": "available" if agent.debug_manager else "unavailable",
                "mcp_servers": mcp_servers,
                "available_tools": tools_list,
                "configuration": {
                    "debug_mode": agent.config.debug_mode,
                    "default_llm": agent.config.default_llm
                }
            }
            print("\n" + json.dumps(status_info, ensure_ascii=False, indent=2))
    
    async def _run_mcp_test(self, args):
        """运行MCP测试命令"""
        print("=== MCP服务连通性检查 ===\n")
        
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
        
        test_results = {
            "servers": {}
        }
        
        try:
            async with MCPClient(mcp_config) as mcp_client:
                print("✓ MCP客户端连接成功\n")
                
                # 显示服务器状态
                for server_name, server_info in mcp_client.server_info.items():
                    healthy = server_info.get('healthy', False)
                    status = "✓ 健康" if healthy else "✗ 不健康"
                    url = server_info.get('url', 'N/A')
                    print(f"  {server_name}: {status} ({url})")
                    
                    test_results["servers"][server_name] = {
                        "url": url,
                        "healthy": healthy
                    }
                    
                    if healthy:
                        # 尝试获取服务器说明
                        instructions = server_info.get('instructions', '')
                        if instructions:
                            print(f"    说明: {instructions[:50]}{'...' if len(instructions) > 50 else ''}")
                print()
                
        except Exception as e:
            error_msg = f"MCP服务连通性检查失败: {e}"
            print(f"✗ {error_msg}")
            test_results["error"] = error_msg
        
        # 如果指定了JSON输出
        if args.json:
            print(json.dumps(test_results, ensure_ascii=False, indent=2))
    
    async def _run_investment_test(self, args):
        """运行投资分析测试命令"""
        print("投资分析测试")
        print("=" * 50)
        
        try:
            # 配置Agent
            config = AgentConfig(
                debug_mode=args.verbose,
                langfuse_enabled=False,
                default_llm="qwen"
            )
            
            agent = DataAnalysisAgent(config)
            
            # 投资相关测试查询
            investment_queries = [
                "查询苹果公司(AAPL)最近一季度的财务数据",
                "分析特斯拉(TSLA)的巴菲特风格投资价值",
                "获取微软(MSFT)的实时股价和技术分析",
                "计算亚马逊(AMZN)的内在价值",
                "评估谷歌(GOOG)的投资风险"
            ]
            
            test_results = {
                "queries": []
            }
            
            for i, query in enumerate(investment_queries, 1):
                print(f"\n[{i}] 用户查询: {query}")
                print("-" * 40)
                
                query_result = {
                    "query": query,
                    "success": False
                }
                
                try:
                    result = await agent.process_query(query)
                    query_result["success"] = True
                    query_result["result"] = result
                    
                    if args.verbose:
                        print("处理结果:")
                        print(result[:500] + "..." if len(result) > 500 else result)
                    else:
                        print("处理结果: 成功")
                    
                    # 显示调试信息
                    mcp_calls = [log for log in agent.debug_manager.logs if log['type'] == 'mcp_input']
                    print(f"MCP调用次数: {len(mcp_calls)}")
                    query_result["mcp_calls"] = len(mcp_calls)
                    
                except Exception as e:
                    error_msg = f"处理查询时出错: {e}"
                    print(error_msg)
                    query_result["error"] = error_msg
                
                test_results["queries"].append(query_result)
                
                # 清空日志以准备下一个查询
                agent.debug_manager.clear_logs()
                
        except Exception as e:
            error_msg = f"投资分析测试失败: {e}"
            print(error_msg)
            test_results["error"] = error_msg
        
        print("\n" + "=" * 50)
        print("投资分析测试完成")

def main():
    """主函数"""
    cli = UnifiedAgentCLI()
    asyncio.run(cli.run())

if __name__ == "__main__":
    main()