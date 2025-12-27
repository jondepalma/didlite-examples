# Quick Start Guide

Get up and running with the Secure Agent Communication system in 5 minutes.

## Prerequisites

✅ Python 3.8+
✅ Virtual environment activated
✅ didlite package installed (from submodule)

## Step 1: Activate Virtual Environment

```bash
source venv/bin/activate
```

## Step 2: Verify Installation

```bash
# Check that didlite is installed
pip list | grep didlite

# Should show: didlite 0.1.5
```

## Step 3: Start the Server

```bash
python main.py
```

You should see:
```
============================================================
Secure Agent Communication API
============================================================

Starting server...
API Documentation: http://127.0.0.1:8000/docs
API Root: http://127.0.0.1:8000/

Agents initialized:
  - BOB: did:key:z6Mkf5rGMoatrSj1f4CyvuHBeXJELe9RPdzo2rJqBrZRQ
  - ALICE: did:key:z6MkoTHsgNNrby8JzCNQ1iRLyW5QQ6R8Xuu6AA8igGrMV
  - CHRIS: did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH

============================================================
```

## Step 4: Run the Interactive Demo

Open a **new terminal**, activate the venv, and run:

```bash
source venv/bin/activate
python demo.py
```

The demo will automatically:
1. List all agent identities
2. Have Bob send a signed message to Alice
3. Have Alice verify the message
4. Demonstrate Chris's attack attempts
5. Show message history

## Step 5: Explore the API

### Web Browser

Visit http://localhost:8000/docs for interactive API documentation.

### Command Line

```bash
# List agents
curl http://localhost:8000/agents

# Bob sends message
curl -X POST http://localhost:8000/agents/bob/send \
  -H "Content-Type: application/json" \
  -d '{"sender":"bob","recipient":"alice","content":"Hello!"}'

# Alice verifies (paste the token from above)
curl -X POST http://localhost:8000/agents/alice/verify \
  -H "Content-Type: application/json" \
  -d '{"token":"YOUR_TOKEN_HERE"}'
```

## Common Operations

### Send a Message

```bash
curl -X POST http://localhost:8000/agents/bob/send \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "bob",
    "recipient": "alice",
    "content": "This is a secure message"
  }'
```

### Verify a Message

```bash
curl -X POST http://localhost:8000/agents/alice/verify \
  -H "Content-Type: application/json" \
  -d '{"token": "PASTE_TOKEN_HERE"}'
```

### Execute Attack

```bash
curl -X POST http://localhost:8000/agents/chris/attack \
  -H "Content-Type: application/json" \
  -d '{"attack_type": "forge"}'
```

Attack types: `replay`, `forge`, `intercept`, `token_theft`

### View Message History

```bash
curl http://localhost:8000/agents/bob/messages
```

## Troubleshooting

### Server won't start

**Error**: `ModuleNotFoundError: No module named 'didlite'`

**Solution**: Install didlite from the submodule:
```bash
source venv/bin/activate
pip install -e ./didlite-pkg
```

### Port already in use

**Error**: `Address already in use`

**Solution**: Change the port in `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Change to 8001
```

### Demo script fails

**Error**: `Connection refused`

**Solution**: Make sure the server is running first:
```bash
# Terminal 1
python main.py

# Terminal 2 (new terminal)
python demo.py
```

## What's Next?

- Read the full [README.md](README.md) for detailed architecture
- Explore the [didlite documentation](didlite-pkg/docs/)
- Try building your own agent interactions
- Extend the system with new attack scenarios

## Architecture at a Glance

```
Agent (Bob) → Create Message → Sign with Private Key → JWS Token
                                                           ↓
                                                     Send to Alice
                                                           ↓
Agent (Alice) ← Verified Payload ← Verify Signature ← Extract DID
                                                           ↓
                                                    Resolve DID to Public Key
```

**Key Insight**: The DID **IS** the public key (encoded). No database lookups needed!

## Need Help?

- Check the API docs: http://localhost:8000/docs
- Read the full README: [README.md](README.md)
- Review didlite docs: [didlite-pkg/CLAUDE.md](didlite-pkg/CLAUDE.md)
