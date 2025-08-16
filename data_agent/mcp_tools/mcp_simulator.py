#!/usr/bin/env python3
"""
MCP服务模拟器
用于测试目的的简单MCP服务模拟器
"""

import asyncio
from aiohttp import web
import json
from datetime import datetime

# 模拟的MCP工具和数据
MOCK_TOOLS = {
    "sec-fetch-production": {
        "sec_financial_data_query": {
            "description": "查询公司财务数据",
            "parameters": ["company", "period"],
            "sample_data": {
                "company": "AAPL",
                "period": "Q1 2023",
                "revenue": 95000000000,
                "net_income": 25000000000,
                "eps": 1.52
            }
        },
        "sec_13f_institutional_data": {
            "description": "查询机构持仓数据",
            "parameters": ["institution", "quarter"],
            "sample_data": {
                "institution": "Berkshire Hathaway",
                "quarter": "Q1 2023",
                "holdings": [
                    {"symbol": "AAPL", "shares": 915000000, "value": 150000000000},
                    {"symbol": "TSM", "shares": 225000000, "value": 15000000000}
                ]
            }
        }
    },
    "sec-investment-analysis": {
        "buffett_style_analysis": {
            "description": "巴菲特风格投资分析",
            "parameters": ["company", "metrics"],
            "sample_data": {
                "company": "AAPL",
                "analysis": {
                    "moat_score": 8.5,
                    "management_quality": 9.0,
                    "valuation": "fair",
                    "long_term_potential": "high"
                }
            }
        },
        "intrinsic_value_calculation": {
            "description": "内在价值计算",
            "parameters": ["company", "method"],
            "sample_data": {
                "company": "AAPL",
                "intrinsic_value": 185.50,
                "current_price": 175.00,
                "margin_of_safety": 0.06
            }
        },
        "investment_risk_assessment": {
            "description": "投资风险评估",
            "parameters": ["company", "metrics"],
            "sample_data": {
                "company": "GOOG",
                "risk_analysis": {
                    "market_risk": "medium",
                    "credit_risk": "low",
                    "liquidity_risk": "low",
                    "operational_risk": "medium",
                    "overall_risk_score": 6.5
                }
            }
        }
    },
    "sec-stock-query": {
        "stock_price_query": {
            "description": "查询股票价格",
            "parameters": ["symbol", "exchange"],
            "sample_data": {
                "symbol": "AAPL",
                "price": 175.00,
                "change": 2.50,
                "change_percent": 1.45,
                "volume": 45000000
            }
        },
        "technical_analysis": {
            "description": "技术分析",
            "parameters": ["symbol", "indicators"],
            "sample_data": {
                "symbol": "AAPL",
                "sma_50": 172.30,
                "sma_200": 168.45,
                "rsi": 62.5,
                "macd": "bullish"
            }
        }
    }
}

async def health_check(request):
    """健康检查端点"""
    return web.json_response({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

async def list_tools(request):
    """列出可用工具"""
    server_name = request.match_info.get('server', 'unknown')
    tools = MOCK_TOOLS.get(server_name, {})
    return web.json_response({
        "tools": list(tools.keys()),
        "server": server_name
    })

async def call_tool(request):
    """调用工具"""
    tool_name = request.match_info.get('tool', 'unknown')
    server_name = request.match_info.get('server', 'unknown')
    
    try:
        # 解析请求参数
        data = await request.json()
        parameters = data.get('parameters', {})
        
        # 查找模拟数据
        tool_data = None
        target_server = None
        
        # 首先在指定服务器中查找
        if server_name in MOCK_TOOLS and tool_name in MOCK_TOOLS[server_name]:
            tool_data = MOCK_TOOLS[server_name][tool_name]
            target_server = server_name
        else:
            # 在所有服务器中查找
            for server, server_tools in MOCK_TOOLS.items():
                if tool_name in server_tools:
                    tool_data = server_tools[tool_name]
                    target_server = server
                    break
        
        if tool_data:
            # 使用参数更新模拟数据
            result_data = tool_data["sample_data"].copy()
            for key, value in parameters.items():
                if key in result_data:
                    result_data[key] = value
            
            return web.json_response({
                "status": "success",
                "tool": tool_name,
                "server": target_server,
                "parameters": parameters,
                "result": result_data,
                "timestamp": datetime.now().isoformat()
            })
        else:
            # 收集所有可用工具
            all_tools = []
            for server_tools in MOCK_TOOLS.values():
                all_tools.extend(server_tools.keys())
                
            return web.json_response({
                "status": "error",
                "tool": tool_name,
                "error": f"工具 {tool_name} 未找到",
                "available_tools": all_tools
            }, status=404)
            
    except Exception as e:
        return web.json_response({
            "status": "error",
            "tool": tool_name,
            "error": str(e)
        }, status=500)

async def create_app():
    """创建应用"""
    app = web.Application()
    
    # 添加CORS支持
    @web.middleware
    async def cors_middleware(request, handler):
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    app.middlewares.append(cors_middleware)
    
    # 路由
    app.router.add_get('/health', health_check)
    app.router.add_get('/{server}/tools', list_tools)
    app.router.add_get('/{server}/tools/{tool}', call_tool)
    app.router.add_post('/{server}/tools/{tool}', call_tool)
    
    # 也支持不带服务器前缀的路由
    app.router.add_get('/tools/{tool}', call_tool)
    app.router.add_post('/tools/{tool}', call_tool)
    
    return app

async def start_servers():
    """启动所有MCP服务"""
    servers = [
        (9000, "sec-fetch-production"),
        (9001, "sec-investment-analysis"),
        (9002, "sec-stock-query")
    ]
    
    runners = []
    
    for port, server_name in servers:
        app = await create_app()
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', port)
        await site.start()
        runners.append(runner)
        print(f"MCP服务 {server_name} 已启动在 http://localhost:{port}")
    
    print("所有MCP服务已启动。按 Ctrl+C 停止。")
    
    try:
        while True:
            await asyncio.sleep(3600)  # 每小时检查一次
    except KeyboardInterrupt:
        print("正在停止服务...")
        for runner in runners:
            await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(start_servers())