# Lumina CLI Chatbot

A command-line chatbot powered by Google Gemini 2.5 Flash with conversation memory, real-time token tracking, and cost monitoring.

---

## Features

- Conversational AI powered by Google Gemini 2.5 Flash
- Conversation memory across turns
- Real-time token usage and USD cost tracking per message
- Session-level cost summary
- Save and load conversation history as JSON
- Three-bullet conversation summary on demand
- Styled terminal interface with slash commands

---

## Tech Stack

| Tech | Purpose |
|------|---------|
| Python 3.14 | Core language |
| Google Gemini 2.5 Flash | AI model |
| tiktoken | Token counting |
| python-dotenv | Environment configuration |

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/lumina-cli-chatbot.git
cd lumina-cli-chatbot
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp project2/.env.example project2/.env
```

Open `.env` and add your API key:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get a free API key at https://aistudio.google.com

### 5. Run

```bash
cd project2
python -m chatbot.cli
```

---

## Commands

| Command | Description |
|---------|-------------|
| /help | Show all available commands |
| /cost | Show token usage and total spend |
| /summary | Summarize the conversation in 3 bullets |
| /clear | Wipe history and start fresh |
| /save [file] | Save history to JSON (default: conversation.json) |
| /load [file] | Load history from JSON |
| /quit | Exit |

---

## Project Structure

```
project2_cli_chatbot/
├── .venv/
├── project2/
│   ├── chatbot/
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   ├── memory.py
│   │   ├── pricing.py
│   │   └── providers.py
│   ├── .env
│   ├── .env.example
│   └── requirements.txt
├── .gitignore
└── README.md
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| GEMINI_API_KEY | Your Google Gemini API key |

---

## License

This project is open source and available under the MIT License.
