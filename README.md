# AI Personal Assistant

A production-ready CLI assistant that integrates ChatGPT, Gmail, Google Calendar, task reminders, and a comprehensive logging system.

## Features

- **🤖 AI Query**: ChatGPT integration for intelligent query responses
- **📧 Email Management**: Gmail integration for email summarization
- **📅 Calendar**: Google Calendar integration for event scheduling
- **✅ Task Reminders**: Local task management with priorities and due dates
- **📝 Logging**: Comprehensive logging system for all operations

## Requirements

- Python 3.11 or higher
- OpenAI API key
- Google Cloud Platform credentials (for Gmail and Calendar)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/KRISHNA-JEE/AI-PERSONAL-AGENT.git
cd AI-PERSONAL-AGENT
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package:
```bash
pip install -e .
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and credentials
```

## Configuration

### OpenAI Setup

1. Get your API key from [OpenAI](https://platform.openai.com/api-keys)
2. Add it to your `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

### Gmail Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download the credentials as `credentials.json`
6. Place the file in the project root directory

### Google Calendar Setup

1. In the same Google Cloud project
2. Enable the Google Calendar API
3. Use the same `credentials.json` file
4. On first run, you'll be prompted to authorize the application

## Usage

### AI Queries

Ask ChatGPT questions directly from the command line:

```bash
assistant ask "What is the weather like today?"
assistant ask "Explain quantum computing in simple terms"
```

### Email Management

Fetch and summarize recent emails:

```bash
# Get last 10 emails from the past 7 days
assistant email

# Custom parameters
assistant email --max-results 5 --days-back 3
```

### Calendar

View upcoming calendar events:

```bash
# Get next 10 events for the next 7 days
assistant calendar

# Custom parameters
assistant calendar --max-results 5 --days-ahead 3
```

### Task Reminders

Manage your tasks and reminders:

```bash
# Add a reminder
assistant reminder add "Buy groceries"
assistant reminder add "Meeting with team" -d "Discuss Q1 goals" --priority high --due-date 2026-03-15

# List reminders
assistant reminder list
assistant reminder list --all  # Include completed
assistant reminder list --priority high  # Filter by priority

# Complete a reminder
assistant reminder complete 1

# Delete a reminder
assistant reminder delete 1
```

### Status Overview

Get a quick overview of your reminders:

```bash
assistant status
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_assistant --cov-report=html

# Run specific test file
pytest tests/test_reminders.py

# Run with verbose output
pytest -v
```

### Project Structure

```
AI-PERSONAL-AGENT/
├── ai_assistant/           # Main package
│   ├── __init__.py
│   ├── cli.py             # CLI interface
│   └── modules/           # Core modules
│       ├── __init__.py
│       ├── ai_query.py    # ChatGPT integration
│       ├── email.py       # Gmail integration
│       ├── calendar.py    # Google Calendar integration
│       ├── reminders.py   # Task management
│       └── logging_module.py  # Logging system
├── tests/                 # Test suite
│   ├── conftest.py
│   ├── test_ai_query.py
│   ├── test_email.py
│   ├── test_calendar.py
│   ├── test_reminders.py
│   └── test_logging.py
├── data/                  # Data storage
├── logs/                  # Log files
├── .env.example          # Environment template
├── .gitignore
├── requirements.txt
├── setup.py
└── README.md
```

## Logging

All operations are logged to help with debugging and monitoring:

- Log file location: `logs/assistant.log` (configurable via `.env`)
- Log level: `INFO` by default (configurable via `.env`)
- Logs include timestamps, module names, and detailed error information

## Security

- API keys and credentials are stored in `.env` (not committed to git)
- OAuth tokens are stored locally and refreshed automatically
- All sensitive data is excluded from version control via `.gitignore`

## Troubleshooting

### "OPENAI_API_KEY not found"
Make sure you've created a `.env` file and added your OpenAI API key.

### "Gmail credentials file not found"
Download `credentials.json` from Google Cloud Console and place it in the project root.

### "Not authenticated" errors
Run the respective command (email or calendar) and follow the OAuth flow in your browser.

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
