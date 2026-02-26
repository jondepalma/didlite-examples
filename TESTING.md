# Testing Guide for didlite-examples

This guide helps you validate the project setup and test all 8 examples.

## Initial Setup Validation

### 1. Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install All Dependencies

```bash
pip install -r requirements.txt
```

This will install `didlite` v0.2.6+ from PyPI along with all required packages for the examples.

### 3. Verify didlite Installation

```bash
python -c "import didlite; agent = didlite.AgentIdentity(); print('Success! Agent DID:', agent.did)"
```

Expected output:
```
Success! Agent DID: did:key:z6Mk...
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
# Make sure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### Issue: Port 8000 already in use

**Solution**:
```bash
# Find and kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Or modify main.py to use a different port
```

## Testing All Examples

### Example 1: FastAPI CMS

```bash
source venv/bin/activate
python 01_fastapi_cms/cms_server.py
```

Expected output:
- Agent DID displayed
- Article published successfully
- CMS response with tier, rate limit, and handler info

### Example 2: LangChain Brand Safety

```bash
source venv/bin/activate
python 02_langchain_brand_safety/main.py
```

Expected output:
- Brand identity DID
- Tweet published successfully
- Attack simulation blocked with safety error

### Example 3: AutoGen Editorial Workflow

```bash
source venv/bin/activate
python 03_autogen_editorial/workflow.py
```

Expected output:
- Copywriter and Editor DIDs
- Round 1: Draft accepted
- Round 2: Imposter access denied
- Round 3: Tampering detected

### Example 5: KeyStore Persistence

```bash
source venv/bin/activate
python 05_keystore_persistence/demo.py
```

Expected output:
- Scenario 1: MemoryKeyStore (identity changes on restart)
- Scenario 2: EnvKeyStore (identity preserved)
- Scenario 3: FileKeyStore (identity preserved with encryption)
- Comparison table of all three backends

### Example 6: Key Backup and Recovery

```bash
source venv/bin/activate
python 06_key_backup/demo.py
```

Expected output:
- Scenario 1: JWK export/import with disaster recovery
- Scenario 2: PEM export/import (OpenSSL compatible)
- Scenario 3: Public key sharing demonstration
- Scenario 4: Cross-system migration
- Format comparison table

### Example 7: Raw Signature Verification

```bash
source venv/bin/activate
python 07_raw_signatures/demo.py
```

Expected output:
- Scenario 1: Raw binary data signing
- Scenario 2: Tamper detection
- Scenario 3: File integrity verification
- Scenario 4: Custom binary protocol
- JWS vs Raw comparison table

### Example 8: Fast Routing

Terminal 1 (Server):
```bash
source venv/bin/activate
python 08_fast_routing/server.py
```

Terminal 2 (Demo):
```bash
source venv/bin/activate
python 08_fast_routing/demo.py
```

Expected output:
- Scenario 1: Free tier rate limiting (3 requests succeed, rest blocked)
- Scenario 2: Request routing by tier
- Scenario 3: Audit logging of all requests
- Scenario 4: Performance comparison (~40-50x speedup)

## Success Criteria

You have successfully set up the project if:

- ✅ didlite imports without errors
- ✅ You can create an AgentIdentity and see a DID
- ✅ All 8 examples run without errors
- ✅ Example 1: Article published successfully
- ✅ Example 2: Tweet published and attack blocked
- ✅ Example 3: All three rounds complete (accept, reject, tamper)
- ✅ Example 4: Server starts and demo shows attack scenarios
- ✅ Example 5: All three KeyStore backends demonstrate persistence
- ✅ Example 6: Key export/import in both JWK and PEM formats
- ✅ Example 7: Raw signatures and file integrity verification
- ✅ Example 8: Rate limiting and performance benchmarks

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
