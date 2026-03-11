#!/bin/bash
# Test the gateway with a simple message

echo "Sending message to gateway..."
echo ""

curl -X POST http://localhost:8080/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "What time is it? Also, what files are in the current directory?"}' \
     | python3 -m json.tool

echo ""
echo "Done!"
