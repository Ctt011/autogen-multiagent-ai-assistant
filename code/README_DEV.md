# Multi-Agent AI Assistant - Development Guide

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys:
# - OPENAI_API_KEY (required)
# - TAVILY_SEARCH_KEY (required)
```

### 3. Run the Assistant

```bash
# Make sure you're in the code/ directory
cd code

# Run the interactive CLI
python main.py
```

## Features

### Interactive CLI
- Beautiful terminal interface with Rich library
- Color-coded messages and formatting
- Built-in commands: `/help`, `/agents`, `/clear`, `/quit`
- Markdown rendering for responses

### Multi-Agent System
- **WeatherAssistant**: Real-time weather data and forecasts
- **SearchAssistant**: Web search and deep research capabilities
- Autonomous agent coordination using AutoGen

### Configuration Management
- Environment-based configuration (.env file)
- Validation for required API keys
- Flexible settings for different deployment environments

## Project Structure

```
code/
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── logger.py           # Logging setup
│   ├── agents.py           # Multi-agent orchestration
│   ├── cli.py              # Interactive CLI interface
│   └── tools/
│       ├── __init__.py
│       ├── weather.py      # Weather tools
│       └── search.py       # Search tools
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Example configuration
└── README_DEV.md          # This file
```

## Custom Enhancements

This project builds upon the ProjectPro template with the following custom additions:

1. **Interactive CLI Interface** - User-friendly command-line chat (not in template)
2. **Modern Configuration** - Environment-based config with python-dotenv (enhanced)
3. **Structured Logging** - Comprehensive logging with file + console output (enhanced)
4. **Better Code Organization** - Modular architecture with clear separation of concerns
5. **Enhanced Error Handling** - Graceful error handling throughout the application

## Development

### Running Tests
```bash
# TODO: Add tests
python -m pytest tests/
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

## Troubleshooting

### "Configuration validation failed"
- Make sure you've created a `.env` file from `.env.example`
- Verify your OPENAI_API_KEY and TAVILY_SEARCH_KEY are set

### "No agents were successfully created"
- Check your API keys are valid
- Review the logs in `logs/assistant.log`

### Import errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Next Steps

Future enhancements to consider:
- Email and Calendar agents (Gmail/Google Calendar integration)
- Conversation memory/history
- Voice interface
- Web UI with FastAPI
- Unit tests and integration tests
