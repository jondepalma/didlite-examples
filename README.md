# didlite: Marketing Agent Examples 📢

This repository demonstrates how to use `didlite` to secure autonomous marketing workflows. By giving each agent a **Cryptographic Identity**, we prevent "hallucinations" from hitting production and ensure a strict Chain of Custody for content.

## Overview

**didlite** provides lightweight, cryptographic identity for autonomous AI agents without requiring centralized servers, databases, or blockchain infrastructure. These examples show real-world marketing and content workflows where agent identity verification prevents unauthorized or malicious content from being published.

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

### Example 1: FastAPI CMS (The "Headless CMS")

**Directory**: [01_fastapi_cms/](01_fastapi_cms/)
**Concept**: Cryptographically verified content publishing

A "Headless CMS" API that only accepts blog posts signed by authorized Copywriter Agents. This prevents rogue posts and provides cryptographic proof of which agent wrote what content.

**Run**:
```bash
python 01_fastapi_cms/cms_server.py
```

**Key Features**:
- FastAPI dependency validates publisher signatures
- Replaces API keys with cryptographic identity
- Self-contained simulation with copywriter agent
- Tracks verified author DID for each published article

---

### Example 2: LangChain Brand Safety (The "Brand Guardian")

**Directory**: [02_langchain_brand_safety/](02_langchain_brand_safety/)
**Concept**: Brand Safety - Preventing unauthorized social media posts

A LangChain tool that validates a cryptographic signature before publishing tweets. This prevents the LLM from hallucinating permissions or posting unauthorized content that could damage brand reputation.

**Run**:
```bash
python 02_langchain_brand_safety/main.py
```

**Key Features**:
- Secure tool requiring signed content tokens
- Pre-authorization pattern with brand identity
- Payload integrity checks prevent content manipulation
- Attack simulation shows security blocking malicious rewrites

---

### Example 3: AutoGen Editorial Workflow (The "Chain of Custody")

**Directory**: [03_autogen_editorial/](03_autogen_editorial/)
**Concept**: Multi-agent workflow with identity verification

An Editor Agent that verifies the author of drafts before spending cycles reviewing them. This establishes a strict Chain of Custody for content, ensuring only known copywriters can submit for editorial review.

**Run**:
```bash
python 03_autogen_editorial/workflow.py
```

**Key Features**:
- Allow-list based authorization (only known copywriters accepted)
- Three security scenarios: legitimate, imposter, and tampering
- Demonstrates signature validation failures
- Chain of custody enforcement

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
├── 01_fastapi_cms/
│   └── cms_server.py
├── 02_langchain_brand_safety/
│   └── main.py
├── 03_autogen_editorial/
│   └── workflow.py
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

- **Marketing Automation**: Prevent rogue AI agents from damaging brand reputation
- **Content Management**: Cryptographic proof of authorship for all published content
- **Social Media Management**: Brand safety controls for autonomous posting agents
- **Editorial Workflows**: Chain of custody for content creation and review
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
