# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a data analysis agent that can understand natural language queries and automatically execute complex data analysis tasks. The system integrates with MCP (Model Coordination Protocol) tools and supports multiple LLM models including Qwen and DeepSeek.

## Code Architecture and Structure

```
data_agent/
├── agent.py              # Main Agent class with core logic
├── cli.py                # Command-line interface
├── unified_cli.py        # Unified command-line interface
├── main.py               # Usage examples
├── demo.py               # Demo program
├── full_demo.py          # Full feature demo
├── production_mcp_example.py # Production MCP configuration example
├── test_agent.py         # Basic tests
├── test_llm.py           # LLM integration tests
├── test_mcp.py           # MCP integration tests
├── test_investment.py    # Investment analysis tests
├── test_session_debug.py # Session debugging tests
├── test_webclient.py     # Web client tests
├── check_status.py       # System status check tool
├── requirements.txt      # Dependencies
├── .env                  # Environment variables configuration
├── mcp_tools/           # MCP tools integration
│   ├── mcp_client.py    # MCP client
│   ├── mcp_config.py    # MCP configuration management
│   ├── mcp_config_example.py # MCP configuration examples
│   └── mcp_simulator.py # MCP simulator
├── utils/               # Utility modules
│   └── debug.py         # Debug manager
├── prompts/             # Prompt management
│   └── prompt_manager.py # Prompt manager
├── llm/                 # LLM integration
│   ├── llm_manager.py   # LLM manager
│   ├── qwen_llm.py      # Qwen integration
│   └── deepseek_llm.py  # DeepSeek integration
└── webclient/           # Web client
    ├── index.html       # Frontend interface
    ├── debug_monitor.html # Debug monitoring interface
    ├── server.py        # Web backend
    ├── start.sh         # Startup script
    └── test_debug_api.py # Debug API test
```

Key components:
1. **DataAnalysisAgent** (agent.py): Core class orchestrating all functionality
2. **MCP Integration**: Multi-service architecture integrating SEC financial data, investment analysis, and stock query services with elegant configuration management
3. **LLM Support**: Multiple language model support with Qwen as default
4. **Web Interface**: Complete frontend with chat interface and debugging monitoring
5. **Debug System**: Comprehensive debugging capabilities with session management

## Common Development Commands

### Installation and Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio black flake8

# Or use the install script
./install.sh
```

### Running the System

#### Command Line Interface
```bash
# Run basic test
python -m data_agent.test_agent

# Run demo
python -m data_agent.demo

# Run investment analysis test
python -m data_agent.test_investment

# Use original CLI tool
python -m data_agent.cli "Analyze Apple's recent financial data"

# CLI options
data-agent --debug "Get Tesla's real-time stock price"
data-agent --model deepseek "Compare two companies' investment value"
data-agent --format json "Analyze user behavior data"

# Use unified CLI tool
python -m data_agent.unified_cli query "Analyze Apple's recent financial data"
python -m data_agent.unified_cli status
python -m data_agent.unified_cli test-mcp
python -m data_agent.unified_cli test-investment

# Use installed CLI command (after pip install)
data-cli query "Analyze Apple's recent financial data"
data-cli status
data-cli test-mcp
data-cli test-investment
```

#### Web Interface
```bash
# Start web service
cd data_agent/webclient
python server.py

# Access in browser at http://localhost:8084
# Debug monitor at http://localhost:8084/debug-monitor.html
```

### Testing
```bash
# Run specific tests
python -m data_agent.test_agent
python -m data_agent.test_llm
python -m data_agent.test_mcp
python -m data_agent.test_investment

# Check system status
python -m data_agent.check_status

# Run all tests (if pytest is configured)
pytest
```

### Docker Deployment
```bash
# Build Docker image
docker build -t data-agent .

# Run container
docker run -p 8083:8083 -p 9000-9002:9000-9002 data-agent
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8
```

## Configuration

API keys and endpoints are configured in `.env` file:
- Qwen API Key: `DASHSCOPE_API_KEY`
- DeepSeek API Key: `DEEPSEEK_API_KEY`
- MCP API Keys: `MCP_API_KEY`, `MCP_INVESTMENT_API_KEY`, `ALPHA_VANTAGE_KEY`

### MCP Server Configuration

The system uses an elegant configuration management system for MCP servers:
- **Default ports**: 8000-8002 (SEC data, Investment analysis, Stock queries)
- **Configuration**: Uses `MCPConfigManager` for flexible server configuration
- **Extensibility**: Easy to add new MCP services and tool mappings

## Development Notes

1. The system uses an async architecture based on aiohttp for high concurrency
2. MCP tools integration supports automatic routing and load balancing
3. Comprehensive debugging capabilities with WebSocket real-time communication
4. Session management for multi-user concurrent usage
5. Multi-level caching mechanism for tool call results
6. Structured responses in JSON format for easy parsing
7. Security features including rate limiting and access logging

## System Status Monitoring

The system provides multiple ways to monitor status:
1. **Web API**: Access `/api/status` and `/api/mcp/status` endpoints
2. **CLI Tool**: Run `python -m data_agent.check_status`
3. **Debug Monitor**: View real-time logs in the web debug interface
4. **Log Files**: Check system logs for detailed information

The architecture is designed for extensibility with planned improvements including:
- Modular refactoring for loose coupling
- Unified tool abstraction
- Memory management system
- Streaming response support
- Parallel tool execution
- Plugin architecture

## MCP Configuration Management

The system now includes an elegant MCP configuration management system:
1. **MCPConfigManager**: Centralized configuration management
2. **ServerType enum**: Categorization of different MCP server types
3. **Dynamic tool mapping**: Flexible mapping between tools and servers
4. **Environment-based configuration**: Automatic API key detection from environment variables
5. **Extensible design**: Easy to add new servers and tools

See `data_agent/mcp_tools/mcp_config_example.py` for usage examples.

## Unified Command-Line Interface

The system now includes a unified CLI tool that combines all functionality:
1. **Data Analysis Queries**: `python -m data_agent.unified_cli query "your query"`
2. **System Status Check**: `python -m data_agent.unified_cli status`
3. **MCP Connectivity Test**: `python -m data_agent.unified_cli test-mcp`
4. **Investment Analysis Test**: `python -m data_agent.unified_cli test-investment`

Use `python -m data_agent.unified_cli --help` for detailed help information.

After installing the package with `pip install`, you can also use the shorter `data-cli` command:
- `data-cli query "your query"`
- `data-cli status`
- `data-cli test-mcp`
- `data-cli test-investment`