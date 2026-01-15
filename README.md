# Multi-Agent AI Assistant

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![AutoGen](https://img.shields.io/badge/AutoGen-0.6.1-green)](https://github.com/microsoft/autogen)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange?logo=openai&logoColor=white)](https://openai.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready multi-agent AI system powered by AutoGen and GPT-4o, featuring specialized autonomous agents for weather, search, email, and calendar management with an interactive CLI interface.

## Features

### Custom Enhancements (My Contributions)

This project builds upon AutoGen fundamentals with significant custom implementations:

- **Interactive CLI Interface** - Beautiful terminal-based chat with Rich library (full custom implementation)
- **Modern Configuration Management** - Environment-based config with validation and dotenv support
- **Structured Logging** - Comprehensive logging system with file + console outputs
- **Modular Architecture** - Clean separation of concerns with organized package structure
- **Robust Error Handling** - Graceful error handling and user-friendly error messages
- **Comprehensive Documentation** - Detailed inline documentation and developer guides

### Multi-Agent System

- **WeatherAssistant** - Real-time weather data, forecasts, and precipitation information
- **SearchAssistant** - Web search and deep research using Tavily API
- **EmailAssistant** - Gmail integration for reading, searching, drafting, and sending emails *(coming soon)*
- **CalendarAssistant** - Google Calendar management for event scheduling *(coming soon)*

### Technical Stack

- **AI Framework**: AutoGen 0.6.1 (agentchat, core, ext)
- **LLM**: OpenAI GPT-4o
- **APIs**: Tavily Search, Open-Meteo Weather, Gmail, Google Calendar
- **Backend**: FastAPI 0.115
- **CLI**: Rich 13.9.4
- **Language**: Python 3.12

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌────────────────────┐         ┌────────────────────┐      │
│  │  Interactive CLI   │         │   Slack Bot (TBD)  │      │
│  │   (Rich Library)   │         │    FastAPI Server  │      │
│  └─────────┬──────────┘         └──────────┬─────────┘      │
└────────────┼───────────────────────────────┼────────────────┘
             │                               │
             └───────────────┬───────────────┘
                             │
             ┌───────────────▼───────────────┐
             │   Multi-Agent Orchestrator    │
             │    (MagenticOneGroupChat)     │
             └───────────────┬───────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
    │ Weather │         │ Search  │        │  Email  │
    │Assistant│         │Assistant│        │Assistant│
    └────┬────┘         └────┬────┘        └────┬────┘
         │                   │                   │
    ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
    │ Weather │         │ Tavily  │        │  Gmail  │
    │  Tools  │         │  API    │        │   API   │
    └─────────┘         └─────────┘        └─────────┘
```

## Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API Key
- Tavily API Key
- (Optional) Google Cloud credentials for Gmail/Calendar

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Ctt011/autogen-multiagent-ai-assistant.git
cd autogen-multiagent-ai-assistant
```

2. **Navigate to code directory**
```bash
cd code
```

3. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Configure environment**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# Required:
#   - OPENAI_API_KEY
#   - TAVILY_SEARCH_KEY
# Optional:
#   - SLACK_BOT_TOKEN (for Slack integration)
#   - GOOGLE_CREDENTIALS_FILE (for Gmail/Calendar)
```

6. **Run the assistant**
```bash
python main.py
```

## Usage

### Interactive CLI

The CLI provides a beautiful terminal interface for chatting with the assistant:

```
Multi-Agent AI Assistant

Welcome! I'm your AI assistant powered by multiple specialized agents...

Commands:
  /help   - Show help message
  /agents - List available agents
  /clear  - Clear screen
  /quit   - Exit assistant

You> What's the weather in Paris?

Assistant
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current weather in Paris:
• Temperature: 15°C
• Conditions: Partly cloudy
• Wind: 12 km/h
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You> Latest news on AI developments

Assistant
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Answer: Recent developments in AI include...

Sources:
1. OpenAI announces GPT-5
   https://example.com/...
   Summary: OpenAI has revealed details...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Available Commands

| Command | Description |
|---------|-------------|
| `/help` | Display help message with examples |
| `/agents` | List all available agents and their capabilities |
| `/clear` | Clear the terminal screen |
| `/quit` or `/exit` | Exit the assistant |

### Example Queries

**Weather Information:**
- "What's the weather in London?"
- "Give me a 3-day forecast for Mumbai"
- "Will it rain tomorrow in Tokyo?"
- "Current temperature in New York"

**Web Search & Research:**
- "Latest developments in artificial intelligence"
- "Research quantum computing applications"
- "What's happening in tech news today?"
- "Find information about AutoGen framework"

## Project Structure

```
autogen-multiagent-ai-assistant/
├── code/                          # Main application code
│   ├── src/                       # Source package
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   ├── logger.py              # Logging setup
│   │   ├── agents.py              # Multi-agent orchestration
│   │   ├── cli.py                 # Interactive CLI interface
│   │   └── tools/                 # Agent tools
│   │       ├── __init__.py
│   │       ├── weather.py         # Weather API integration
│   │       └── search.py          # Tavily search integration
│   ├── main.py                    # Application entry point
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example              # Example configuration
│   └── README_DEV.md             # Developer documentation
├── .gitignore                     # Git ignore patterns
└── README.md                      # This file
```

## Configuration

All configuration is managed through environment variables in the `.env` file:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4o |
| `TAVILY_SEARCH_KEY` | Yes | Tavily API key for web search |
| `OPENAI_MODEL` | No | Model to use (default: gpt-4o) |
| `OPENAI_TEMPERATURE` | No | Temperature setting (default: 1.0) |
| `DEFAULT_TIMEZONE` | No | Default timezone (default: America/Los_Angeles) |
| `LOG_LEVEL` | No | Logging level (default: INFO) |
| `SLACK_BOT_TOKEN` | No | Slack bot token (optional) |
| `GOOGLE_CREDENTIALS_FILE` | No | Google API credentials (optional) |

## Development

### Running Tests

```bash
# Install development dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Type checking
mypy src/

# Linting
pylint src/
```

## Roadmap

### Phase 1: Core Features (Current)
- [x] Interactive CLI interface
- [x] Weather assistant
- [x] Search assistant
- [x] Configuration management
- [x] Logging system

### Phase 2: Extended Features
- [ ] Email assistant (Gmail integration)
- [ ] Calendar assistant (Google Calendar)
- [ ] Conversation memory/history
- [ ] Multi-LLM support (Claude, Gemini)

### Phase 3: Advanced Features
- [ ] Slack bot interface
- [ ] Web UI with FastAPI
- [ ] Voice interface integration
- [ ] Agent performance analytics
- [ ] Comprehensive test suite
- [ ] CI/CD pipeline

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [AutoGen](https://github.com/microsoft/autogen) - Multi-agent framework
- [OpenAI](https://openai.com/) - GPT-4o language model
- [Tavily](https://tavily.com/) - Search API
- [Open-Meteo](https://open-meteo.com/) - Free weather API
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting

## Contact

Camille Tran - [@Ctt011](https://github.com/Ctt011)

Project Link: [https://github.com/Ctt011/autogen-multiagent-ai-assistant](https://github.com/Ctt011/autogen-multiagent-ai-assistant)

---

**Built using AutoGen and GPT-4o**