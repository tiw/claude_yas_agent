import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class PromptManager:
    """Prompt管理器，用于管理各种prompt模板"""
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.prompts = {}
        self._load_default_prompts()
        
    def _load_default_prompts(self):
        """加载默认prompt"""
        self.prompts = {
            "query_parser": self._get_query_parser_prompt(),
            "response_generator": self._get_response_generator_prompt(),
            "data_analyzer": self._get_data_analyzer_prompt(),
            "reflection_analyzer": self._get_reflection_analyzer_prompt(),
            "demand_network_query_parser": self._get_demand_network_query_parser_prompt(),
            "demand_network_response_generator": self._get_demand_network_response_generator_prompt()
        }
        
    def _get_query_parser_prompt(self) -> str:
        """获取查询解析prompt"""
        return """你是一个智能查询解析器。请将用户输入解析为结构化查询。

用户输入: {user_input}
当前日期: {current_date}

请分析用户想要执行什么类型的数据分析，并提取必要的参数。

支持的MCP工具及其功能说明:
1. SEC财报数据分析服务 (sec-fetch-production):
   - sec_financial_data_query: 查询公司财务数据
   - sec_13f_institutional_data: 查询机构持仓数据
   - system_resource_monitor: 监控系统资源使用情况

2. 投资分析服务 (sec-investment-analysis):
   - buffett_style_analysis: 巴菲特风格投资分析
   - intrinsic_value_calculation: 内在价值计算
   - investment_risk_assessment: 投资风险评估

3. 股票查询服务 (sec-stock-query):
   - stock_price_query: 查询股票价格
   - technical_analysis: 技术分析
   - fundamental_analysis: 基本面分析
   - real_time_market_data: 实时市场数据

请严格按照以下JSON格式返回结果，不要包含其他文字:
{
  "intent": "获取苹果公司最近一季度的财务数据",
  "mcp_tools": [
    {
      "name": "sec_financial_data_query",
      "parameters": {
        "company": "AAPL",
        "period": "Q1 2023"
      }
    }
  ],
  "date_range": {
    "start_date": "2023-01-01",
    "end_date": "2023-03-31"
  },
  "filters": {
    "metrics": ["revenue", "net_income", "eps"]
  }
}

示例查询和对应的解析结果:
1. 用户输入: "查询苹果公司最近一季度的财务数据"
   解析结果:
   {
     "intent": "查询公司财务数据",
     "mcp_tools": [
       {
         "name": "sec_financial_data_query",
         "parameters": {
           "company": "AAPL"
         }
       }
     ]
   }

2. 用户输入: "分析巴菲特可能会投资的股票"
   解析结果:
   {
     "intent": "巴菲特风格投资分析",
     "mcp_tools": [
       {
         "name": "buffett_style_analysis",
         "parameters": {
           "company": "unknown"
         }
       }
     ]
   }

3. 用户输入: "获取特斯拉的实时股价和技术分析"
   解析结果:
   {
     "intent": "股票价格和技术分析",
     "mcp_tools": [
       {
         "name": "stock_price_query",
         "parameters": {
           "symbol": "TSLA"
         }
       },
       {
         "name": "technical_analysis",
         "parameters": {
           "symbol": "TSLA"
         }
       }
     ]
   }

注意事项:
1. 请只返回JSON格式的结果，不要包含其他文字
2. 如果没有相关字段，请设置为null或空数组
3. 日期格式为YYYY-MM-DD
4. 确保JSON格式正确，可以被直接解析
5. 根据用户查询选择最合适的MCP工具
6. 公司名称请使用股票代码表示（如苹果用AAPL，特斯拉用TSLA）
7. 如果不确定具体参数，可以设置为合理的默认值"""
        
    def _get_response_generator_prompt(self) -> str:
        """获取响应生成prompt"""
        return """你是一个数据分析报告生成器。请根据分析结果生成清晰、易懂的报告。

原始查询: {original_query}
分析结果: {analysis_results}

请严格按照以下JSON格式返回结果，不要包含其他文字:
{
  "report": {
    "executive_summary": "执行摘要",
    "detailed_analysis": "详细分析结果",
    "key_insights": ["关键洞察1", "关键洞察2"],
    "recommendations": ["建议1", "建议2"]
  }
}

注意事项:
1. 请只返回JSON格式的结果，不要包含其他文字
2. 确保JSON格式正确，可以被直接解析
3. 使用简洁明了的语言，避免过多的技术术语
4. 如果没有相关内容，请设置为null或空数组"""
        
    def _get_data_analyzer_prompt(self) -> str:
        """获取数据分析prompt"""
        return """你是一个数据分析专家。请分析提供的数据并提取关键洞察。

数据: {data}
分析目标: {analysis_goal}

请执行以下分析:
1. 数据质量检查
2. 关键指标计算
3. 趋势分析
4. 异常检测

以结构化格式返回分析结果。"""
        
    def _get_reflection_analyzer_prompt(self) -> str:
        """获取反思分析prompt"""
        return """你是一个AI反思专家。请对当前的分析结果进行深度思考和优化。

原始查询: {original_query}
当前结果: {current_result}

请执行以下反思和优化:
1. 分析当前结果的不足之处
2. 识别可能被忽略的要点
3. 提出改进建议
4. 如有必要，生成更深入的分析请求

请严格按照以下JSON格式返回结果，不要包含其他文字:
{
  "analysis": "当前结果的不足分析",
  "improvement_suggestions": ["建议1", "建议2"],
  "deep_analysis_needed": true,
  "new_query": "如果需要深入分析，请提供新的查询"
}"""
        
    def get_prompt(self, prompt_name: str) -> str:
        """获取指定名称的prompt"""
        return self.prompts.get(prompt_name, "")
        
    def add_prompt(self, prompt_name: str, prompt_template: str):
        """添加新的prompt"""
        self.prompts[prompt_name] = prompt_template
        
    def update_prompt(self, prompt_name: str, prompt_template: str):
        """更新现有prompt"""
        if prompt_name in self.prompts:
            self.prompts[prompt_name] = prompt_template
        else:
            raise ValueError(f"Prompt '{prompt_name}' 不存在")
            
    def load_prompts_from_file(self, filepath: str):
        """从文件加载prompts"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
                self.prompts.update(prompts_data)
            logger.info(f"从 {filepath} 加载了 {len(prompts_data)} 个prompts")
        except Exception as e:
            logger.error(f"加载prompts文件失败: {e}")
            
    def save_prompts_to_file(self, filepath: str):
        """保存prompts到文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.prompts, f, ensure_ascii=False, indent=2)
            logger.info(f"Prompts已保存到 {filepath}")
        except Exception as e:
            logger.error(f"保存prompts文件失败: {e}")
            
    def _get_demand_network_query_parser_prompt(self) -> str:
        """获取需求网络查询解析prompt"""
        return """你是一个需求网络分析查询解析器。请将用户输入解析为结构化查询，专门用于市场需求分析和趋势预测。

用户输入: {user_input}
当前日期: {current_date}

请分析用户想要执行什么类型的需求网络分析，并提取必要的参数。

支持的MCP工具及其功能说明:
1. 需求网络分析服务 (demand-network-analysis):
   - demand_network_analysis: 分析特定行业或产品的需求网络
   - market_demand_forecasting: 市场需求预测
   - consumer_behavior_analysis: 消费者行为分析
   - trend_prediction: 趋势预测

请严格按照以下JSON格式返回结果，不要包含其他文字:
{
  "intent": "分析智能手机市场的需求趋势",
  "mcp_tools": [
    {
      "name": "market_demand_forecasting",
      "parameters": {
        "industry": "smartphones",
        "region": "global",
        "time_horizon": "12_months"
      }
    }
  ],
  "date_range": {
    "start_date": "2023-01-01",
    "end_date": "2023-12-31"
  },
  "filters": {
    "segments": ["consumers", "businesses"],
    "metrics": ["demand_volume", "growth_rate", "market_share"]
  }
}

示例查询和对应的解析结果:
1. 用户输入: "分析电动汽车市场需求趋势"
   解析结果:
   {
     "intent": "电动汽车市场需求趋势分析",
     "mcp_tools": [
       {
         "name": "market_demand_forecasting",
         "parameters": {
           "industry": "electric_vehicles"
         }
       }
     ]
   }

2. 用户输入: "预测AI芯片未来6个月的市场需求"
   解析结果:
   {
     "intent": "AI芯片市场需求预测",
     "mcp_tools": [
       {
         "name": "market_demand_forecasting",
         "parameters": {
           "industry": "ai_chips",
           "time_horizon": "6_months"
         }
       }
     ]
   }

3. 用户输入: "分析消费者对可穿戴设备的购买行为"
   解析结果:
   {
     "intent": "可穿戴设备消费者行为分析",
     "mcp_tools": [
       {
         "name": "consumer_behavior_analysis",
         "parameters": {
           "product_category": "wearable_devices"
         }
       }
     ]
   }

注意事项:
1. 请只返回JSON格式的结果，不要包含其他文字
2. 如果没有相关字段，请设置为null或空数组
3. 日期格式为YYYY-MM-DD
4. 确保JSON格式正确，可以被直接解析
5. 根据用户查询选择最合适的MCP工具
6. 行业和产品类别请使用英文标识符"""
        
    def _get_demand_network_response_generator_prompt(self) -> str:
        """获取需求网络响应生成prompt"""
        return """你是一个需求网络分析报告生成器。请根据分析结果生成清晰、易懂的市场需求分析报告。

原始查询: {original_query}
分析结果: {analysis_results}

请严格按照以下JSON格式返回结果，不要包含其他文字:
{
  "report": {
    "executive_summary": "执行摘要",
    "detailed_analysis": "详细分析结果",
    "key_insights": ["关键洞察1", "关键洞察2"],
    "recommendations": ["建议1", "建议2"],
    "market_trends": ["市场趋势1", "市场趋势2"],
    "demand_forecast": {
      "short_term": "短期预测",
      "medium_term": "中期预测",
      "long_term": "长期预测"
    }
  }
}

注意事项:
1. 请只返回JSON格式的结果，不要包含其他文字
2. 确保JSON格式正确，可以被直接解析
3. 使用简洁明了的语言，避免过多的技术术语
4. 如果没有相关内容，请设置为null或空数组
5. 重点关注市场需求、消费者行为和市场趋势
6. 提供可操作的洞察和建议"""