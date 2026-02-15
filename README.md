# Plan: AI Personal Assistant with ChatGPT, Gmail & Calendar

## TL;DR
Build a production-ready CLI assistant that integrates ChatGPT for queries, Gmail for email summarization, Google Calendar for scheduling, and task reminders with a logging system. Start with a modular architecture using Python 3.11+ and .env for secure credential management. All five core modules (AI query, email, calendar, reminders, logging) are MVP features. Include pytest tests and docstrings for each module to ensure maintainability. Structure code to support GUI upgrade (Tkinter) later without major refactoring.

## Project Structure
```
ai_personal_agent/
├── config/
│   ├── __init__.py
│   └── settings.py              # Load from .env
├── modules/
│   ├── __init__.py
│   ├── ai_handler.py            # ChatGPT API wrapper
│   ├── email_handler.py         # Gmail API wrapper
│   ├── calendar_handler.py      # Google Calendar wrapper
│   ├── task_scheduler.py        # Schedule reminders
│   └── logger.py                # Logging utility
├── core/
│   ├── __init__.py
│   └── assistant.py             # Main orchestrator
├── tests/
│   ├── __init__.py
│   ├── test_ai_handler.py
│   ├── test_email_handler.py
│   ├── test_calendar_handler.py
│   ├── test_task_scheduler.py
│   └── test_assistant.py
├── .env.example                 # Template for credentials
├── .gitignore                   # Ignore .env and __pycache__
├── requirements.txt             # Python dependencies
├── setup.py                     # Package metadata
├── main.py                      # CLI entry point
└── README.md                    # Documentation
```

## Steps

### Step 1: Initialize project structure & dependencies
- Create directory structure and files listed above
- Create `requirements.txt` with: openai, google-api-python-client, google-auth-oauthlib, google-auth-httplib2, python-dotenv, schedule, pytest, pytest-cov, requests
- Add `.gitignore` to exclude `.env`, `__pycache__`, `.pytest_cache`, `assistant.log`, `.venv`
- Create `.env.example` with placeholder keys: OPENAI_API_KEY, GMAIL_CREDENTIALS_PATH, CALENDAR_CREDENTIALS_PATH

### Step 2: Set up configuration & logging
- Build `config/settings.py` to load `.env` variables using `python-dotenv`
- Create `modules/logger.py` with Python's logging module configured to write to `assistant.log` with timestamps, levels (INFO/DEBUG/ERROR)
- Document that users must copy `.env.example` → `.env` and fill in real API keys

### Step 3: Implement AI Handler (ChatGPT)
- Build `modules/ai_handler.py` with `ask_chatgpt(question: str) → str` that calls OpenAI API (using `openai.ChatCompletion.create`)
- Add error handling for invalid API keys, network errors, quota limits
- Include docstrings and type hints on all functions
- Create `tests/test_ai_handler.py` with pytest mocks for OpenAI API calls

### Step 4: Implement Email Handler (Gmail)
- Build `modules/email_handler.py` with:
  - `authenticate_gmail()` that uses OAuth2 credentials
  - `get_unread_emails() → list` that fetches latest unread emails
  - `summarize_emails()` that chains `get_unread_emails()` → calls `ask_chatgpt()` for each email body
- Add error handling for missing credentials, malformed emails
- Include `_decode_email_body()` helper to parse MIME-encoded emails
- Create `tests/test_email_handler.py` with mocked Gmail API responses

### Step 5: Implement Calendar Handler (Google Calendar)
- Build `modules/calendar_handler.py` with:
  - `authenticate_calendar()` using OAuth2
  - `create_event(title, start_time, end_time, description) → event_id` to add calendar events
  - `get_upcoming_events(days=7) → list` to fetch upcoming events
- Add error handling for invalid datetime format, quota limits
- Create `tests/test_calendar_handler.py` with mocked Calendar API calls

### Step 6: Implement Task Scheduler (Reminders)
- Build `modules/task_scheduler.py` with:
  - `schedule_reminder(task_name, trigger_time)` using `schedule` library
  - `run_scheduler()` with background loop checking pending tasks
  - Integrate with logger to log all triggered reminders
- Example: schedule daily email summary at 8:00 AM
- Create `tests/test_task_scheduler.py` with time mocking

### Step 7: Build main orchestrator
- Create `core/assistant.py` as the central coordinator:
  - Initialize all handlers (AI, email, calendar, scheduler)
  - Expose public methods: `ask_question()`, `summarize_emails()`, `schedule_event()`, `set_reminder()`, `run()`
  - Load configuration on startup
  - Log all actions
- Create `tests/test_assistant.py` with integration tests
- Add docstrings describing expected workflows

### Step 8: Create CLI interface
- Build `main.py` as entry point with:
  - `print()` menu showing: (1) Ask AI, (2) Summarize emails, (3) Schedule event, (4) Set reminder, (5) Exit
  - `input()` loop to capture user selections
  - Chain to appropriate handler methods (e.g., if choice==1, call `assistant.ask_question()`)
  - Catch exceptions and display user-friendly error messages
- Log all user interactions

### Step 9: Document & prepare for GUI upgrade
- Create `README.md` with: setup instructions, API key setup, CLI usage examples, architecture overview
- Add `setup.py` for potential packaging
- Structure handler classes to be UI-agnostic (no `print()` in business logic, return strings instead)
- Add comments noting where Tkinter/Flask would slot in later

## Verification

### Unit tests
- Run `pytest tests/` (target: >80% code coverage)
- Mock all external API calls (OpenAI, Gmail, Calendar)
- Test success paths, error handling, edge cases

### Manual CLI testing
- Create `.env` with test API keys
- Run `python main.py`, test each menu option
- Verify logs written to `assistant.log`

### Integration test
- Chain full workflow (ask AI → log result → confirm in assistant.log)

### Check credentials
- Verify `.env` is in `.gitignore` so keys never leak

## Decisions

- **CLI first, GUI later**: Start with CLI (faster development), design code as UI-agnostic so Tkinter/Flask upgrade won't require refactoring
- **.env for credentials**: Most secure practice; `.env.example` shows structure without exposing keys
- **All 5 modules as MVP**: Full feature set from day one ensures portfolio value; reminders optional can be removed if time-constrained
- **Production-grade code**: Include tests + docstrings immediately to avoid technical debt
- **No external database**: Use `.log` file for records; can add SQLite/PostgreSQL later if needed

