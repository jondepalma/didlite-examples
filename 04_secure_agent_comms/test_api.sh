#!/bin/bash
# Simple API test script
# Run this after starting the server with: python main.py

BASE_URL="http://localhost:8000"

echo "====================================================================="
echo "  Secure Agent Communication API - Test Script"
echo "====================================================================="
echo ""

# Check if server is running
echo "1. Checking server health..."
curl -s $BASE_URL/health | json_pp
echo ""
echo ""

# List agents
echo "2. Listing all agents..."
curl -s $BASE_URL/agents | json_pp
echo ""
echo ""

# Bob sends message to Alice
echo "3. Bob sends a message to Alice..."
RESPONSE=$(curl -s -X POST $BASE_URL/agents/bob/send \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "bob",
    "recipient": "alice",
    "content": "Hello Alice! This is a secure message from Bob."
  }')
echo "$RESPONSE" | json_pp

# Extract token
TOKEN=$(echo "$RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
echo ""
echo "Token extracted: ${TOKEN:0:80}..."
echo ""
echo ""

# Alice verifies Bob's message
echo "4. Alice verifies Bob's message..."
curl -s -X POST $BASE_URL/agents/alice/verify \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$TOKEN\"}" | json_pp
echo ""
echo ""

# Chris attempts forgery
echo "5. Chris attempts to forge a message..."
curl -s -X POST $BASE_URL/agents/chris/attack \
  -H "Content-Type: application/json" \
  -d '{"attack_type":"forge"}' | json_pp
echo ""
echo ""

# View message history
echo "6. View Bob's message history..."
curl -s $BASE_URL/agents/bob/messages | json_pp
echo ""
echo ""

echo "====================================================================="
echo "  Test Complete!"
echo "====================================================================="
