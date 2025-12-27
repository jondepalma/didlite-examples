# didlite Integration Examples

This repository demonstrates how to integrate `didlite` (Decentralized Identity for Agents) into major AI frameworks and applications. Each example showcases a different security pattern using W3C DID standards and JWS token signing.

## Overview

**didlite** provides lightweight, cryptographic identity for autonomous AI agents without requiring centralized servers, databases, or blockchain infrastructure. These examples show how to implement secure agent communication across different frameworks.

## Prerequisites

- Python 3.8+
- Git with submodule support
- Virtual environment recommended

## Installation

### 1. Clone the Repository

```bash
git clone --recurse-submodules <repo-url>
cd didlite-examples
```

Or if already cloned:

```bash
git submodule update --init --recursive
```

### 2. Set Up Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install didlite from Submodule

```bash
pip install -e ./didlite-pkg
```

### 4. Install All Dependencies

```bash
pip install -r requirements.txt
```

## Examples

### Example 1: FastAPI Gatekeeper

**Directory**: [01_fastapi_gatekeeper/](01_fastapi_gatekeeper/)
**Concept**: The Gatekeeper - Protecting API endpoints without API keys

Demonstrates how to secure FastAPI endpoints using DID-based authentication instead of traditional API keys. The `verify_agent` dependency validates JWS tokens cryptographically.

**Run**:
```bash
python 01_fastapi_gatekeeper/server.py
```

**Key Features**:
- FastAPI dependency injection for auth
- Bearer token validation
- Self-contained verification (no database lookups)

---

### Example 2: LangChain Secure Tool

**Directory**: [02_langchain_secure_tool/](02_langchain_secure_tool/)
**Concept**: The Secure Tool - Tool execution requires cryptographic signatures

Shows how to create LangChain tools that require cryptographically signed parameters to prevent LLM hallucination of permissions.

**Run**:
```bash
python 02_langchain_secure_tool/main.py
```

**Key Features**:
- Pre-authorization pattern
- Signature verification before execution
- Payload claim validation

---

### Example 3: AutoGen Handshake

**Directory**: [03_autogen_handshake/](03_autogen_handshake/)
**Concept**: The Handshake - Multi-agent message signing and verification

Demonstrates secure communication between autonomous agents in a multi-agent system, with tamper detection.

**Run**:
```bash
python 03_autogen_handshake/simulation.py
```

**Key Features**:
- Agent-to-agent authentication
- Message integrity verification
- Attack simulation (message tampering)

---

### Example 4: Secure Agent Communications

**Directory**: [04_secure_agent_comms/](04_secure_agent_comms/)
**Concept**: Full-featured secure agent communication system

A comprehensive FastAPI application demonstrating multiple attack scenarios and defenses including replay protection, forgery attempts, and message interception.

**Run**:
```bash
# Start the server
python 04_secure_agent_comms/main.py

# In another terminal, run the demo
python 04_secure_agent_comms/demo.py --verbose
```

**Key Features**:
- Complete API for agent messaging
- Attack scenario demonstrations
- Nonce-based replay protection
- Interactive API documentation at http://localhost:8000/docs

**Documentation**:
- [Full README](04_secure_agent_comms/README.md)
- [Quick Start Guide](04_secure_agent_comms/QUICKSTART.md)

## Key Concepts

### Identity is Local
No servers or databases required for identity verification. Each agent generates and manages their own cryptographic identity.

### DID = Public Key
The DID format `did:key:z6Mk...` contains the public key encoded with Multibase/Multicodec. No external resolution needed.

### JWS (JSON Web Signatures)
Standard transport envelope for signed messages:
- `didlite.create_jws(agent, payload)` - Sign a message
- `didlite.verify_jws(token)` - Verify signature and extract payload

## Project Structure

```
didlite-examples/
├── README.md                          # This file
├── CLAUDE.md                          # Development guide
├── requirements.txt                   # All dependencies
├── .gitignore                         # Excludes dev-design/
├── didlite-pkg/                       # Git submodule (v0.2.0)
├── dev-design/                        # Untracked context docs
├── 01_fastapi_gatekeeper/
│   └── server.py
├── 02_langchain_secure_tool/
│   └── main.py
├── 03_autogen_handshake/
│   └── simulation.py
└── 04_secure_agent_comms/
    ├── main.py
    ├── agents.py
    ├── models.py
    ├── nonce_tracker.py
    ├── demo.py
    ├── test_api.sh
    ├── README.md
    └── QUICKSTART.md
```

## Security Patterns Demonstrated

### 1. Signature Verification
All examples use `verify_jws()` to validate message authenticity without requiring a central authority.

### 2. Zero-Knowledge Architecture
Identity verification happens locally using only the DID and signature. No external calls needed.

### 3. Tamper Detection
Modified tokens are automatically rejected (see Example 3 attack simulation).

### 4. Intent Verification
Payload claims must match function arguments to prevent parameter manipulation (Example 2).

### 5. Replay Protection
Application-layer nonce tracking prevents reuse of valid tokens (Example 4).

## Use Cases

This architecture is ideal for:

- **Autonomous AI Agents**: Verifiable communication between AI systems
- **IoT Devices**: Lightweight identity for edge devices
- **Distributed Systems**: No central authority required
- **Agent Marketplaces**: Cryptographic proof of agent actions
- **Secure Tool Execution**: Prevent LLM permission hallucination

## didlite vs. Application Layer

**didlite provides**:
- ✅ DID generation and management
- ✅ JWS token signing
- ✅ Signature verification
- ✅ Cryptographic identity binding

**Your application handles**:
- 🔧 Nonce tracking for replay protection
- 🔧 Message expiration policies
- 🔧 Audience claims
- 🔧 Business logic and authorization rules

## Educational Disclaimer

These examples are for **educational and demonstration purposes**. For production systems:

- Use proper secret management (HSM, key vaults)
- Implement distributed nonce tracking (Redis, database)
- Add rate limiting and DOS protection
- Use secure communication channels (TLS)
- Follow security best practices for your deployment environment

## Troubleshooting

### didlite not found
Make sure you installed from the submodule:
```bash
pip install -e ./didlite-pkg
```

### Import errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Submodule not initialized
Initialize the submodule:
```bash
git submodule update --init --recursive
```

## References

- [didlite Repository](https://github.com/jondepalma/didlite-pkg) (private)
- [W3C DID Specification](https://www.w3.org/TR/did-core/)
- [DID:Key Method](https://w3c-ccg.github.io/did-method-key/)
- [JWS Specification (RFC 7515)](https://tools.ietf.org/html/rfc7515)
- [Ed25519 Signatures](https://ed25519.cr.yp.to/)

## Contributing

This is a demonstration repository. For issues or improvements to didlite itself, please contact the maintainer.

## License

Provided as-is for educational purposes.

## Author

Built with Claude Code to demonstrate secure agent communication patterns using didlite.
