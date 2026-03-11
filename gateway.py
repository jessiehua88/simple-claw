#!/usr/bin/env python3
"""
gateway.py - A simple web gateway for SimpleClaw

THIS IS THE GATEWAY. It's just a web server that:
1. Runs forever (always listening)
2. Receives messages from the outside world
3. Passes them to the AI
4. Returns the response

Run it:
    python gateway.py

Then it listens on http://localhost:8080

Send a message:
    curl -X POST http://localhost:8080/chat \
         -H "Content-Type: application/json" \
         -d '{"message": "Hello!"}'

That's it. That's a gateway.
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
from anthropic import Anthropic
from datetime import datetime

from tools import TOOLS, execute_tool

load_dotenv()
client = Anthropic()

# Store conversations by session (simple in-memory store)
sessions = {}


def build_system_prompt():
    """Build system prompt (simplified version)."""
    from pathlib import Path
    
    parts = [f"""You are a helpful AI assistant.
Current time: {datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")}
"""]
    
    soul = Path("SOUL.md")
    if soul.exists():
        parts.append("## Your Personality\n" + soul.read_text())
    
    return "\n\n".join(parts)


def chat_with_tools(messages):
    """Send messages to Claude, handle tool calls, return final response."""
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=build_system_prompt(),
        tools=TOOLS,
        messages=messages
    )
    
    # Process response, handling tool calls recursively
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
    
    if assistant_content:
        messages.append({"role": "assistant", "content": assistant_content})
    
    # Execute tools if needed
    if tool_uses:
        tool_results = []
        for tool_use in tool_uses:
            print(f"  🔧 Tool: {tool_use.name}")
            result = execute_tool(tool_use.name, tool_use.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result
            })
        
        messages.append({"role": "user", "content": tool_results})
        return chat_with_tools(messages)  # Recurse for more tool calls
    
    return "\n".join(text_parts)


class GatewayHandler(BaseHTTPRequestHandler):
    """
    THIS IS THE ACTUAL GATEWAY LOGIC
    
    It handles incoming HTTP requests and routes them to the AI.
    """
    
    def do_POST(self):
        """Handle incoming messages."""
        
        if self.path == "/chat":
            # Read the incoming message
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            message = data.get("message", "")
            session_id = data.get("session", "default")
            
            print(f"\n📨 Received: {message[:50]}...")
            
            # Get or create session
            if session_id not in sessions:
                sessions[session_id] = []
            
            messages = sessions[session_id]
            messages.append({"role": "user", "content": message})
            
            # Get AI response
            response_text = chat_with_tools(messages)
            
            print(f"📤 Responding: {response_text[:50]}...")
            
            # Send response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "response": response_text,
                "session": session_id
            }).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        """Health check endpoint."""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "alive"}).encode())
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
            <html>
            <body style="font-family: sans-serif; max-width: 600px; margin: 50px auto;">
                <h1>SimpleClaw Gateway</h1>
                <p>The gateway is running! Send POST requests to <code>/chat</code></p>
                <h3>Example:</h3>
                <pre style="background: #f0f0f0; padding: 15px;">
curl -X POST http://localhost:8080/chat \\
     -H "Content-Type: application/json" \\
     -d '{"message": "What time is it?"}'
                </pre>
            </body>
            </html>
            """)
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def main():
    """
    START THE GATEWAY
    
    This runs forever, listening for messages.
    It's the "always on" part.
    """
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), GatewayHandler)
    
    print(f"""
╔═══════════════════════════════════════════════════════╗
║           🦞 SimpleClaw Gateway Running               ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║   URL: http://localhost:{port}                         ║
║                                                       ║
║   This process stays alive, waiting for messages.     ║
║   THIS is what a gateway is.                          ║
║                                                       ║
║   Try: curl -X POST http://localhost:{port}/chat \\    ║
║        -H "Content-Type: application/json" \\         ║
║        -d '{{"message": "Hello!"}}'                    ║
║                                                       ║
║   Press Ctrl+C to stop                                ║
╚═══════════════════════════════════════════════════════╝
""")
    
    try:
        server.serve_forever()  # <-- THIS IS THE "ALWAYS ON" PART
    except KeyboardInterrupt:
        print("\n👋 Gateway stopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
