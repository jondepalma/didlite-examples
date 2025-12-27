# Secure Agent Communication System

A FastAPI-based demonstration of cryptographically secure communication between AI agents using [didlite](https://github.com/jondepalma/didlite-pkg) for decentralized identity and message signing.

## Overview

This application simulates secure communication between autonomous AI agents using W3C DID (Decentralized Identifier) standards and JWS (JSON Web Signature) tokens. Each agent has a unique cryptographic identity, and all messages are signed to ensure:

- **Authentication**: Recipients can verify who sent the message
- **Integrity**: Any tampering with messages is detected
- **Non-repudiation**: Senders cannot deny sending signed messages

## Agents

The system includes three agents:

1. **Bob** (Good Actor): Honest agent who sends legitimate messages
2. **Alice** (Good Actor): Honest agent who sends legitimate messages
3. **Chris** (Bad Actor): Malicious agent who attempts various attacks

Each agent has a persistent DID-based identity using Ed25519 cryptography.

## Architecture

```
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│    Bob      │        │   Alice     │        │   Chris     │
│  (Good)     │        │  (Good)     │        │   (Bad)     │
└──────┬──────┘        └──────┬──────┘        └──────┬──────┘
       │                      │                      │
       │  Signed Message      │                      │
       ├─────────────────────>│                      │
       │  (JWS Token)         │                      │
       │                      │                      │
       │                      │  Attack Attempts     │
       │                      │<─────────────────────┤
       │                      │  (Replay, Forge,     │
       │                      │   Intercept, Theft)  │
       │                      │                      │
       └──────────────────────┴──────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │   didlite Library  │
                    │  - DID Generation  │
                    │  - JWS Signing     │
                    │  - Verification    │
                    └────────────────────┘
```

## Key Concepts

### Separation of Concerns: didlite vs. Application Layer

This demo illustrates an important architectural principle:

**didlite (Cryptographic Layer)**:
- ✅ DID generation and management
- ✅ JWS token signing
- ✅ Signature verification
- ✅ Cryptographic identity binding

**Application Layer (This Demo)**:
- 🔧 Nonce tracking for replay protection
- 🔧 Message expiration policies
- 🔧 Audience claims
- 🔧 Business logic

didlite intentionally focuses **only** on the cryptographic primitives, keeping it lightweight and versatile. Application-level security features (like replay protection) are your responsibility.

### ⚠️  Educational Disclaimer

This demo uses a **simple file-based nonce tracker** (`nonces.json`) to illustrate replay protection concepts. This is intentionally simplified for educational purposes.

**Production systems should use**:
- Redis or Memcached for distributed systems
- PostgreSQL, MongoDB, or similar databases
- Atomic operations to prevent race conditions
- Proper error handling and monitoring
- Secure key storage (HSM, key vaults)

The file-based approach demonstrates the *concept* without requiring external dependencies.

### DID (Decentralized Identifier)

Each agent has a unique DID in the format: `did:key:z6Mk...`

- The DID **IS** the public key (encoded with Multibase/Multicodec)
- No central registry or blockchain needed
- Perfect for edge devices and IoT scenarios

### JWS Tokens

Messages are signed using JWS (JSON Web Signature) format:
```
eyJhbGc...header.eyJtZXNz...payload.dBjftJ...signature
```

The token header includes the sender's DID in the `kid` field, enabling self-contained verification.

## Installation

### Prerequisites

- Python 3.8+
- Virtual environment (venv)
- Git with submodule support

### Setup

1. Clone the repository and initialize submodules:
```bash
cd /home/pi/dev-projects/secure-agent-comms
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Verify didlite is installed:
```bash
pip list | grep didlite
```

4. Install additional dependencies (already done):
```bash
pip install fastapi uvicorn pydantic
```

## Running the Application

### Start the Server

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Run the FastAPI server
python main.py
```

The server will start on http://localhost:8000

### Run the Interactive Demo

In a separate terminal, run the demo script to see all attack scenarios:

```bash
# Basic demo
python demo.py

# Verbose mode with detailed cryptographic operations
python demo.py --verbose
```

The verbose mode shows:
- Detailed token structure (header, payload, signature)
- Comparison of original vs. tampered messages
- Explanation of public key cryptography concepts
- Visual demonstration of signature validation failures
- Nonce file contents showing replay protection

**Key Demonstration**: The demo includes a nonce protection scenario that shows:
1. Instant replay attack SUCCESS (without nonces)
2. Enabling nonce tracking
3. Instant replay attack BLOCKED (with nonces)
4. Viewing the `nonces.json` file to see how it works

### API Documentation

Once running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### General

- `GET /` - API root with usage information
- `GET /health` - Health check endpoint

### Agent Management

- `GET /agents` - List all agents and their DIDs
- `GET /agents/{agent_name}/identity` - Get specific agent's DID

### Messaging

- `POST /agents/{agent_name}/send` - Send a signed message
- `POST /agents/{agent_name}/verify` - Verify a received message
- `GET /agents/{agent_name}/messages` - View message history

### Security Demonstrations

- `POST /agents/chris/attack` - Execute attack scenarios (educational)

### Nonce Protection (Application Layer)

- `POST /nonce/enable` - Enable nonce-based replay protection
- `POST /nonce/disable` - Disable nonce-based replay protection
- `GET /nonce/stats` - Get nonce tracking statistics

**Note**: Nonce protection is an application-layer feature, not part of didlite. This demonstrates how to build additional security on top of the cryptographic primitives.

## Usage Examples

### 1. List All Agents

```bash
curl http://localhost:8000/agents
```

Response:
```json
[
  {
    "name": "bob",
    "did": "did:key:z6Mkf5rGMoatrSj1f4CyvuHBeXJELe9RPdzo2rJqBrZRQ"
  },
  {
    "name": "alice",
    "did": "did:key:z6MkoTHsgNNrby8JzCNQ1iRLyW5QQ6R8Xuu6AA8igGrMV"
  },
  {
    "name": "chris",
    "did": "did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"
  }
]
```

### 2. Bob Sends a Message to Alice

```bash
curl -X POST http://localhost:8000/agents/bob/send \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "bob",
    "recipient": "alice",
    "content": "Hello Alice, this is a secure message from Bob!"
  }'
```

Response:
```json
{
  "token": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCIsImtpZCI6ImRpZDprZXk6ejZNa2Y1ckdNb2F0clNqMWY0Q3l2dUhCZVhKRUxlOVJQZHpvMnJKcUJyWlJRIn0.eyJtZXNzYWdlX2lkIjoiMTIzNDU2NzgtYWJjZC0xMjM0LTEyMzQtMTIzNDU2Nzg5MDEyIiwic2VuZGVyIjoiYm9iIiwicmVjaXBpZW50IjoiYWxpY2UiLCJjb250ZW50IjoiSGVsbG8gQWxpY2UsIHRoaXMgaXMgYSBzZWN1cmUgbWVzc2FnZSBmcm9tIEJvYiEiLCJ0aW1lc3RhbXAiOjE3MDM1NDMyMTAsImlhdCI6MTcwMzU0MzIxMCwiZXhwIjoxNzAzNTQzNTEwfQ.dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk",
  "sender_did": "did:key:z6Mkf5rGMoatrSj1f4CyvuHBeXJELe9RPdzo2rJqBrZRQ"
}
```

### 3. Alice Verifies Bob's Message

```bash
curl -X POST http://localhost:8000/agents/alice/verify \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGci...full_token_here"
  }'
```

Response:
```json
{
  "valid": true,
  "payload": {
    "message_id": "12345678-abcd-1234-1234-123456789012",
    "sender": "bob",
    "recipient": "alice",
    "content": "Hello Alice, this is a secure message from Bob!",
    "timestamp": 1703543210,
    "iat": 1703543210,
    "exp": 1703543510
  },
  "sender_did": "did:key:z6Mkf5rGMoatrSj1f4CyvuHBeXJELe9RPdzo2rJqBrZRQ",
  "error": null
}
```

### 4. View Message History

```bash
curl http://localhost:8000/agents/bob/messages
```

Response:
```json
{
  "agent": "bob",
  "sent": [
    {
      "message_id": "12345678-abcd-1234-1234-123456789012",
      "recipient": "alice",
      "content": "Hello Alice!",
      "timestamp": 1703543210,
      "token": "eyJhbGci..."
    }
  ],
  "received": []
}
```

## Attack Scenarios

Chris (the bad actor) can attempt various attacks to demonstrate the security properties of didlite.

### 1. Replay Attack

Chris tries to resend an old valid message:

```bash
curl -X POST http://localhost:8000/agents/chris/attack \
  -H "Content-Type: application/json" \
  -d '{
    "attack_type": "replay",
    "target_agent": "alice"
  }'
```

**Result**: Succeeds if token hasn't expired, fails otherwise.
**Defense**: Short expiration times (5 minutes) + nonce tracking.

### 2. Forgery Attack

Chris tries to create a message claiming to be Bob:

```bash
curl -X POST http://localhost:8000/agents/chris/attack \
  -H "Content-Type: application/json" \
  -d '{
    "attack_type": "forge"
  }'
```

**Result**: Token verifies, but DID reveals Chris as the signer, not Bob.
**Defense**: The DID in the token header proves the true sender.

### 3. No Private Key Attack

Chris tries to forge a signature using only Bob's public key/DID:

```bash
curl -X POST http://localhost:8000/agents/chris/attack \
  -H "Content-Type: application/json" \
  -d '{
    "attack_type": "no_private_key"
  }'
```

**Result**: Impossible - public keys can only verify signatures, not create them.
**Defense**: Asymmetric cryptography ensures only the private key holder can sign.

### 4. Intercept Attack

Chris intercepts and modifies a message in transit:

```bash
curl -X POST http://localhost:8000/agents/chris/attack \
  -H "Content-Type: application/json" \
  -d '{
    "attack_type": "intercept"
  }'
```

**Result**: Signature verification fails because payload was modified.
**Defense**: Cryptographic signature ensures message integrity.

### 5. Token Theft Attack

Chris steals and reuses a valid token:

```bash
curl -X POST http://localhost:8000/agents/chris/attack \
  -H "Content-Type: application/json" \
  -d '{
    "attack_type": "token_theft"
  }'
```

**Result**: Token is valid, but DID proves it came from the original sender.
**Defense**: Audience claims + context-specific validation.

## Security Features

### Built-in Protections (via didlite)

✅ **Authentication**: DID in token proves sender identity
✅ **Integrity**: Signature detects any tampering
✅ **Non-repudiation**: Sender cannot deny signing
✅ **Asymmetric Crypto**: Only private key holder can create signatures
✅ **Expiration**: Tokens expire after 5 seconds

### Additional Protections Needed

⚠️ **Replay Protection**: Implement nonce/message ID tracking
⚠️ **Context Binding**: Add audience claims to restrict token usage
⚠️ **Rate Limiting**: Prevent denial of service attacks
⚠️ **Secure Storage**: Protect private keys in production

## Technical Details

### How DIDs Work

1. **Generation**: Agent creates Ed25519 keypair
2. **Encoding**: Public key → Multicodec prefix (0xed01) → Base58btc → `did:key:z...`
3. **Resolution**: DID → Base58btc decode → Remove prefix → Public key

No network calls needed! The DID IS the public key.

### How Message Signing Works

1. **Create Payload**: Message data + timestamp + expiration
2. **Create Header**: Algorithm (EdDSA) + DID in `kid` field
3. **Sign**: Ed25519 signature over `base64(header).base64(payload)`
4. **Token**: `header.payload.signature`

### How Verification Works

1. **Parse Token**: Split into header.payload.signature
2. **Extract DID**: Get `kid` from header
3. **Resolve DID**: Extract public key from DID (no network!)
4. **Verify Signature**: Ed25519 verification
5. **Check Expiration**: Ensure token is still valid

## Development

### Project Structure

```
secure-agent-comms/
├── main.py              # FastAPI application
├── agents.py            # Agent management and identity
├── models.py            # Pydantic data models
├── README.md            # This file
├── requirements.txt     # Python dependencies
├── venv/                # Virtual environment
└── didlite-pkg/         # Git submodule (didlite library)
```

### Running Tests

```bash
# Run didlite tests
cd didlite-pkg
pytest -v

# Test the API manually using the interactive docs
# Visit http://localhost:8000/docs
```

### Adding New Agents

To add a new agent, modify `agents.py`:

```python
def __init__(self):
    # ... existing code ...
    self._create_agent("dave")  # New agent
```

## Use Cases

This architecture is ideal for:

- **Autonomous AI Agents**: Verifiable communication between AI systems
- **IoT Devices**: Lightweight identity for edge devices
- **Distributed Systems**: No central authority required
- **Agent Marketplaces**: Cryptographic proof of agent actions
- **Autonomous Commerce**: Secure payment authorizations (see AP2 plugin design)

## Future Enhancements

- [ ] Implement message nonce tracking to prevent replay attacks
- [ ] Add audience claims for context-specific tokens
- [ ] Integrate with didlite-ap2 plugin for payment mandates
- [ ] Add rate limiting and DOS protection
- [ ] Implement secure key storage (HSM, encrypted files)
- [ ] Add WebSocket support for real-time messaging
- [ ] Create agent-to-agent trust relationships
- [ ] Add group messaging with multi-signature support

## References

- [didlite Library](https://github.com/jondepalma/didlite-pkg)
- [W3C DID Specification](https://www.w3.org/TR/did-core/)
- [DID:Key Method Specification](https://w3c-ccg.github.io/did-method-key/)
- [JWS Specification (RFC 7515)](https://tools.ietf.org/html/rfc7515)
- [Ed25519 Signatures](https://ed25519.cr.yp.to/)

## License

This project is provided as-is for educational purposes.

## Author

Built with Claude Code as a demonstration of secure agent communication using didlite.
