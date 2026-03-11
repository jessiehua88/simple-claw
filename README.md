# 🦞 SimpleClaw

A minimal AI agent with tools and memory. Think of it as a tiny, hackable version of [OpenClaw](https://github.com/openclaw/openclaw).

## Features

- **Claude API** with function calling
- **Tools:** read/write files, run commands, fetch URLs
- **Memory:** simple file-based daily notes
- **CLI interface** with rich formatting

## Quick Start

```bash
# Clone the repo
git clone https://github.com/jessiehua88/simple-claw.git
cd simple-claw

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up your API key
cp .env.example .env
# Edit .env and add your Anthropic API key

# Run it!
python agent.py
```

## Tools Available

| Tool | Description |
|------|-------------|
| `read_file` | Read contents of a file |
| `write_file` | Write content to a file |
| `list_directory` | List directory contents |
| `run_command` | Run shell commands |
| `fetch_url` | Fetch and extract text from URLs |
| `get_current_time` | Get current date/time |
| `save_memory` | Save notes to daily memory file |
| `read_memory` | Read notes from a specific date |

## Customization

### Change the Model

In `agent.py`, find the `chat()` function and change the model:

```python
model: str = "claude-sonnet-4-20250514"  # or "claude-3-haiku-20240307" for cheaper
```

### Add Your Own Tools

1. Add a function to `tools.py`
2. Add the tool definition to the `TOOLS` list
3. Add it to the `execute_tool()` function

### Customize the System Prompt

Edit `SYSTEM_PROMPT` in `agent.py` to change the agent's personality and instructions.

## Project Structure

```
simple-claw/
├── agent.py          # Main chat loop and Claude integration
├── tools.py          # Tool definitions and implementations
├── requirements.txt  # Python dependencies
├── .env.example      # Example environment variables
├── .gitignore
├── memory/           # Daily memory files (gitignored)
└── README.md
```

## Ideas for Extension

- [ ] Add web search (Brave API, Tavily, etc.)
- [ ] Add a web UI (Flask, FastAPI + htmx)
- [ ] Connect to Telegram/Discord/Slack
- [ ] Add semantic memory search (embeddings)
- [ ] Add image understanding (vision)
- [ ] Add scheduled tasks (cron-like)

## License

MIT - do whatever you want with it! 🎉
