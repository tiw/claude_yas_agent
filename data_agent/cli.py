#!/usr/bin/env python3
"""
数据分析Agent CLI工具
"""

import argparse
import asyncio
import sys
import json
from typing import Optional
from data_agent.agent import DataAnalysisAgent, AgentConfig

class AgentCLI:
    """Agent命令行界面"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """创建命令行参数解析器"""
        parser = argparse.ArgumentParser(
            description="数据分析Agent CLI工具",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用示例:
  %(prog)s "分析苹果公司最近的财务数据"
  %(prog)s --debug "获取特斯拉的实时股价"
  %(prog)s --model deepseek "比较两家公司的投资价值"
        """
        )
        
        parser.add_argument(
            'query',
            nargs='?',
            help='数据分析查询'
        )
        
        parser.add_argument(
            '--debug',
            action='store_true',
            help='启用调试模式'
        )
        
        parser.add_argument(
            '--model',
            choices=['qwen', 'deepseek'],
            default='qwen',
            help='指定使用的LLM模型'
        )
        
        parser.add_argument(
            '--format',
            choices=['json', 'text'],
            default='text',
            help='输出格式'
        )
        
        parser.add_argument(
            '--session',
            help='指定会话ID'
        )
        
        return parser
    
    async def run(self, args: Optional[list] = None):
        """运行CLI工具"""
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.query:
            self.parser.print_help()
            return
        
        # 配置Agent
        config = AgentConfig(
            debug_mode=parsed_args.debug,
            default_llm=parsed_args.model
        )
        
        # 创建Agent实例
        agent = DataAnalysisAgent(config)
        
        try:
            # 处理查询
            result = await agent.process_query(parsed_args.query)
            
            # 格式化输出
            if parsed_args.format == 'json':
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(result)
                
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)

def main():
    """主函数"""
    cli = AgentCLI()
    asyncio.run(cli.run())

if __name__ == "__main__":
    main()