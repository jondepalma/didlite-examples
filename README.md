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

---

### Example 5: Persistent Identity with KeyStore Backends (The "Reboot")

**Directory**: [05_keystore_persistence/](05_keystore_persistence/)
**Concept**: Maintaining agent identity across restarts using storage backends

Demonstrates three KeyStore backends for different deployment scenarios: MemoryKeyStore (ephemeral), EnvKeyStore (container-friendly), and FileKeyStore (edge devices).

**Run**:
```bash
python 05_keystore_persistence/demo.py
```

**Key Features**:
- Three storage backends: Memory, Environment Variables, Encrypted Files
- Identity persistence across simulated restarts
- Deployment strategy comparison
- Encrypted file storage with Fernet (AES-128-CBC)

**Documentation**:
- [Full README](05_keystore_persistence/README.md)

---

### Example 6: Key Backup, Export, and Recovery (The "Backup")

**Directory**: [06_key_backup/](06_key_backup/)
**Concept**: Exporting agent keys for backup, migration, and disaster recovery

Demonstrates key export/import using both JWK (JSON Web Key) and PEM formats for maximum interoperability with web APIs and OpenSSL tools.

**Run**:
```bash
python 06_key_backup/demo.py
```

**Key Features**:
- JWK export/import (web-friendly JSON format)
- PEM export/import (OpenSSL compatible)
- Public key sharing (verification only)
- Cross-system migration scenarios
- Disaster recovery demonstrations

**Documentation**:
- [Full README](06_key_backup/README.md)

---

### Example 7: Raw Signature Verification (The "Custom Protocol")

**Directory**: [07_raw_signatures/](07_raw_signatures/)
**Concept**: Signing arbitrary binary data without JWS wrapper

Demonstrates low-level signing operations for custom protocols, IoT sensors, file integrity checks, and scenarios where JWS overhead is unnecessary.

**Run**:
```bash
python 07_raw_signatures/demo.py
```

**Key Features**:
- Raw binary data signing (no JSON overhead)
- File integrity verification
- Custom binary protocol design
- Tamper detection demonstrations
- Overhead comparison: JWS vs Raw

**Documentation**:
- [Full README](07_raw_signatures/README.md)

---

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
├── didlite-pkg/                       # Git submodule (v0.2.1)
├── dev-design/                        # Untracked context docs
├── 01_fastapi_cms/
│   ├── cms_server.py
│   └── README.md
├── 02_langchain_brand_safety/
│   ├── main.py
│   └── README.md
├── 03_autogen_editorial/
│   ├── workflow.py
│   └── README.md
├── 04_secure_agent_comms/
│   ├── main.py
│   ├── agents.py
│   ├── models.py
│   ├── nonce_tracker.py
│   ├── demo.py
│   ├── test_api.sh
│   ├── README.md
│   └── QUICKSTART.md
├── 05_keystore_persistence/
│   ├── demo.py
│   └── README.md
├── 06_key_backup/
│   ├── demo.py
│   └── README.md
└── 07_raw_signatures/
    ├── demo.py
    └── README.md
```

## Security Patterns Demonstrated

### 1. Signature Verification
All examples use `verify_jws()` or raw signature verification to validate message authenticity without requiring a central authority.

### 2. Zero-Knowledge Architecture
Identity verification happens locally using only the DID and signature. No external calls needed.

### 3. Tamper Detection
Modified tokens are automatically rejected (Examples 3, 7 attack simulations).

### 4. Intent Verification
Payload claims must match function arguments to prevent parameter manipulation (Example 2).

### 5. Replay Protection
Application-layer nonce tracking prevents reuse of valid tokens (Example 4).

### 6. Persistent Identity
KeyStore backends enable agents to maintain identity across restarts for reputation and auditability (Example 5).

### 7. Disaster Recovery
Key export/import in standard formats (JWK, PEM) enables backup and recovery (Example 6).

### 8. Custom Protocols
Raw signature operations enable minimal-overhead signing for IoT and embedded systems (Example 7).

## Use Cases

This architecture is ideal for:

### Content & Marketing (Examples 1-3)
- **Marketing Automation**: Prevent rogue AI agents from damaging brand reputation
- **Content Management**: Cryptographic proof of authorship for all published content
- **Social Media Management**: Brand safety controls for autonomous posting agents
- **Editorial Workflows**: Chain of custody for content creation and review

### Agent Infrastructure (Examples 4-5)
- **Agent Marketplaces**: Cryptographic proof of agent actions
- **Secure Tool Execution**: Prevent LLM permission hallucination
- **Multi-Agent Systems**: Secure communication between autonomous agents
- **Cloud Deployments**: Container-friendly identity with EnvKeyStore
- **Edge Computing**: Persistent identity for Raspberry Pi and IoT devices

### Enterprise & Compliance (Example 6)
- **Disaster Recovery**: Backup and restore critical agent identities
- **Key Migration**: Move agents between dev/staging/production environments
- **Audit Trails**: Verify historical signatures years after creation
- **OpenSSL Integration**: Enterprise PKI and certificate workflows

### IoT & Embedded Systems (Examples 5, 7)
- **IoT Sensor Networks**: Minimal bandwidth signature verification
- **Firmware Signing**: Verify software updates before installation
- **File Integrity**: Detect tampering in data archives
- **Custom Protocols**: Binary message signing for embedded systems

## didlite vs. Application Layer

**didlite provides**:
- ✅ DID generation and management
- ✅ JWS token signing and verification
- ✅ Raw signature operations (binary data)
- ✅ Cryptographic identity binding
- ✅ KeyStore backends (Memory, Environment, File)
- ✅ Key export/import (JWK, PEM formats)
- ✅ DID resolution (local, no network)

**Your application handles**:
- 🔧 Nonce tracking for replay protection
- 🔧 Message expiration policies
- 🔧 Audience claims and access control
- 🔧 Business logic and authorization rules
- 🔧 Key rotation and lifecycle management
- 🔧 Audit logging and monitoring

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
