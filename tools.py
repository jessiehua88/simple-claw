"""
Simple tools for the agent.
Each tool is a function that returns a string result.
"""

import os
import subprocess
import httpx
from pathlib import Path
from datetime import datetime


def read_file(path: str) -> str:
    """Read contents of a file."""
    try:
        p = Path(path).expanduser()
        if not p.exists():
            return f"Error: File not found: {path}"
        if p.stat().st_size > 100_000:  # 100KB limit
            return f"Error: File too large (>100KB): {path}"
        return p.read_text()
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(path: str, content: str) -> str:
    """Write content to a file. Creates parent directories if needed."""
    try:
        p = Path(path).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return f"Successfully wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


def list_directory(path: str = ".") -> str:
    """List contents of a directory."""
    try:
        p = Path(path).expanduser()
        if not p.exists():
            return f"Error: Directory not found: {path}"
        if not p.is_dir():
            return f"Error: Not a directory: {path}"
        items = sorted(p.iterdir())
        result = []
        for item in items[:50]:  # Limit to 50 items
            prefix = "📁 " if item.is_dir() else "📄 "
            result.append(f"{prefix}{item.name}")
        if len(items) > 50:
            result.append(f"... and {len(items) - 50} more items")
        return "\n".join(result) if result else "(empty directory)"
    except Exception as e:
        return f"Error listing directory: {e}"


def run_command(command: str) -> str:
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd()
        )
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += f"\n[stderr]: {result.stderr}"
        if result.returncode != 0:
            output += f"\n[exit code: {result.returncode}]"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out (30s limit)"
    except Exception as e:
        return f"Error running command: {e}"


def fetch_url(url: str) -> str:
    """Fetch content from a URL and extract text."""
    try:
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            response = client.get(url, headers={
                "User-Agent": "SimpleClaw/1.0 (AI Agent)"
            })
            response.raise_for_status()
            
            content_type = response.headers.get("content-type", "")
            if "text/html" in content_type:
                # Basic HTML to text extraction
                text = response.text
                # Remove script and style tags
                import re
                text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
                # Remove HTML tags
                text = re.sub(r'<[^>]+>', ' ', text)
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                # Limit length
                if len(text) > 10000:
                    text = text[:10000] + "... (truncated)"
                return text
            else:
                return response.text[:10000]
    except Exception as e:
        return f"Error fetching URL: {e}"


def get_current_time() -> str:
    """Get current date and time."""
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y at %I:%M %p")


def save_memory(content: str) -> str:
    """Save a note to today's memory file."""
    today = datetime.now().strftime("%Y-%m-%d")
    memory_dir = Path("memory")
    memory_dir.mkdir(exist_ok=True)
    memory_file = memory_dir / f"{today}.md"
    
    timestamp = datetime.now().strftime("%H:%M")
    entry = f"\n\n## {timestamp}\n{content}"
    
    with open(memory_file, "a") as f:
        f.write(entry)
    
    return f"Saved to memory/{today}.md"


def read_memory(date: str = None) -> str:
    """Read memory from a specific date (YYYY-MM-DD) or today."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    memory_file = Path("memory") / f"{date}.md"
    if not memory_file.exists():
        return f"No memory found for {date}"
    
    return memory_file.read_text()


# Tool definitions for Claude
TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file at the given path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Creates the file and parent directories if needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "list_directory",
        "description": "List the contents of a directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the directory (default: current directory)"
                }
            },
            "required": []
        }
    },
    {
        "name": "run_command",
        "description": "Run a shell command and return the output. Use for system tasks, git, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "fetch_url",
        "description": "Fetch and extract text content from a URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to fetch"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "get_current_time",
        "description": "Get the current date and time.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "save_memory",
        "description": "Save a note or memory to today's memory file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Content to save to memory"
                }
            },
            "required": ["content"]
        }
    },
    {
        "name": "read_memory",
        "description": "Read memory/notes from a specific date.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format (default: today)"
                }
            },
            "required": []
        }
    }
]


def execute_tool(name: str, args: dict) -> str:
    """Execute a tool by name with given arguments."""
    tools_map = {
        "read_file": lambda: read_file(args.get("path", "")),
        "write_file": lambda: write_file(args.get("path", ""), args.get("content", "")),
        "list_directory": lambda: list_directory(args.get("path", ".")),
        "run_command": lambda: run_command(args.get("command", "")),
        "fetch_url": lambda: fetch_url(args.get("url", "")),
        "get_current_time": lambda: get_current_time(),
        "save_memory": lambda: save_memory(args.get("content", "")),
        "read_memory": lambda: read_memory(args.get("date")),
    }
    
    if name not in tools_map:
        return f"Unknown tool: {name}"
    
    return tools_map[name]()
