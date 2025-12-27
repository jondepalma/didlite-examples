# Testing Guide for didlite-examples

This guide helps you validate the project setup and test Example 4 (Secure Agent Communications).

## Initial Setup Validation

### 1. Verify Submodule

```bash
# Check submodule is initialized
ls -la didlite-pkg/
# Should show didlite package contents
```

### 2. Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install didlite from Submodule

```bash
pip install -e ./didlite-pkg
```

### 4. Verify didlite Installation

```bash
python -c "import didlite; agent = didlite.AgentIdentity(); print('Success! Agent DID:', agent.did)"
```

Expected output:
```
Success! Agent DID: did:key:z6Mk...
```

### 5. Install Example Dependencies

```bash
pip install fastapi uvicorn pydantic
```

## Testing Example 4: Secure Agent Communications

### Start the Server

In your first terminal:

```bash
source venv/bin/activate
cd 04_secure_agent_comms
python main.py
```

Expected output:
```
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Access API Documentation

Open your browser to:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Run the Demo

In your second terminal:

```bash
source venv/bin/activate
cd 04_secure_agent_comms
python demo.py
```

For detailed cryptographic operations:

```bash
python demo.py --verbose
```

### Expected Demo Output

The demo will show:
1. Agent identities (DIDs) for Bob, Alice, and Chris
2. Successful message signing and verification
3. Attack scenarios:
   - Replay attacks
   - Forgery attempts
   - Message tampering detection
   - Token theft demonstration
4. Nonce protection demonstration

### Manual API Testing

#### List All Agents

```bash
curl http://localhost:8000/agents
```

Expected response:
```json
[
  {
    "name": "bob",
    "did": "did:key:z6Mk..."
  },
  ...
]
```

#### Send a Message

```bash
curl -X POST http://localhost:8000/agents/bob/send \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "bob",
    "recipient": "alice",
    "content": "Hello Alice!"
  }'
```

#### View Message History

```bash
curl http://localhost:8000/agents/bob/messages
```

## Troubleshooting

### Issue: ModuleNotFoundError for 'didlite'

**Solution**:
```bash
pip install -e ./didlite-pkg
```

### Issue: Port 8000 already in use

**Solution**:
```bash
# Find and kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Or modify main.py to use a different port
```

### Issue: Submodule is empty

**Solution**:
```bash
git submodule update --init --recursive
```

## Next Steps

Once Example 4 is working:

1. **Build Example 1** (FastAPI Gatekeeper)
   - Create `01_fastapi_gatekeeper/server.py`
   - Follow the specification in `dev-design/DIDLITE-EXAMPLES.md`

2. **Build Example 2** (LangChain Secure Tool)
   - Create `02_langchain_secure_tool/main.py`
   - Install: `pip install langchain langchain-openai`

3. **Build Example 3** (AutoGen Handshake)
   - Create `03_autogen_handshake/simulation.py`
   - Install: `pip install pyautogen`

## Success Criteria

You have successfully set up the project if:

- ✅ didlite imports without errors
- ✅ You can create an AgentIdentity and see a DID
- ✅ Example 4 server starts on port 8000
- ✅ The demo script runs and shows attack scenarios
- ✅ API documentation is accessible at http://localhost:8000/docs
- ✅ You can send and verify messages via the API

## Additional Testing

### Run the Shell Test Script

```bash
cd 04_secure_agent_comms
chmod +x test_api.sh
./test_api.sh
```

This script tests all API endpoints automatically.

### Test Identity Persistence

Agents use persistent DIDs. You can verify this by:

1. Starting the server
2. Noting Bob's DID from `/agents`
3. Restarting the server
4. Checking Bob's DID again (should be the same)

### Test Nonce Protection

1. Enable nonce tracking: `POST /nonce/enable`
2. Send a message: `POST /agents/bob/send`
3. Try to verify the same token twice
4. Second verification should fail with replay detection

## Performance Notes

- Token generation: < 1ms
- Signature verification: < 2ms
- No network calls required for identity resolution
- Lightweight enough for IoT and edge devices
