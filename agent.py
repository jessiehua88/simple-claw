#!/usr/bin/env python3
"""
SimpleClaw - A minimal AI agent with tools and memory.
"""

import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from tools import TOOLS, execute_tool

# Load environment variables
load_dotenv()

# Initialize
console = Console()
client = Anthropic()

# System prompt - customize this!
SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools.

You can:
- Read and write files
- Run shell commands  
- Fetch content from URLs
- Save and recall memories

Be concise and helpful. When using tools, explain what you're doing briefly.

Current working directory: {cwd}
"""

def chat(messages: list[dict], model: str = "claude-sonnet-4-20250514") -> dict:
    """Send messages to Claude and handle tool use."""
    
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT.format(cwd=os.getcwd()),
        tools=TOOLS,
        messages=messages
    )
    
    return response


def process_response(response, messages: list[dict]) -> str:
    """Process Claude's response, handling any tool calls."""
    
    # Collect all content from the response
    assistant_content = []
    text_parts = []
    tool_uses = []
    
    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)
            assistant_content.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            tool_uses.append(block)
            assistant_content.append({
                "type": "tool_use",
                "id": block.id,
                "name": block.name,
                "input": block.input
            })
    
    # Add assistant message with all content
    if assistant_content:
        messages.append({"role": "assistant", "content": assistant_content})
    
    # If there are tool calls, execute them
    if tool_uses:
        tool_results = []
        
        for tool_use in tool_uses:
            console.print(f"[dim]🔧 Using tool: {tool_use.name}[/dim]")
            
            # Execute the tool
            result = execute_tool(tool_use.name, tool_use.input)
            
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result
            })
        
        # Add tool results to messages
        messages.append({"role": "user", "content": tool_results})
        
        # Get Claude's response to the tool results
        response = chat(messages)
        return process_response(response, messages)
    
    # No more tool calls, return the text
    return "\n".join(text_parts)


def main():
    """Main chat loop."""
    console.print(Panel.fit(
        "[bold blue]🦞 SimpleClaw[/bold blue]\n"
        "[dim]A minimal AI agent with tools and memory[/dim]\n"
        "[dim]Type 'quit' to exit, 'clear' to reset conversation[/dim]",
        border_style="blue"
    ))
    
    messages = []
    
    while True:
        try:
            # Get user input
            console.print()
            user_input = console.input("[bold green]You:[/bold green] ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                console.print("[dim]Goodbye! 👋[/dim]")
                break
            
            if user_input.lower() == "clear":
                messages = []
                console.print("[dim]Conversation cleared.[/dim]")
                continue
            
            # Add user message
            messages.append({"role": "user", "content": user_input})
            
            # Get response
            console.print()
            response = chat(messages)
            result = process_response(response, messages)
            
            # Display response
            console.print("[bold blue]Assistant:[/bold blue]")
            console.print(Markdown(result))
            
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Goodbye! 👋[/dim]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
