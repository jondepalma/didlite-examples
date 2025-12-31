# CLAUDE.md - didlite-examples Project Guide

## Project Overview
This repository demonstrates how to integrate `didlite` (Decentralized Identity for Agents) into major AI frameworks. It contains eight example applications showing different use cases for agent identity and cryptographic verification.

## Architecture

### Repository Structure
```
didlite-examples/
├── README.md
├── CLAUDE.md                       # This file
├── TESTING.md                      # Testing guide
├── requirements.txt
├── didlite-pkg/                    # Git submodule (private repo)
├── 01_fastapi_cms/
│   └── cms_server.py
├── 02_langchain_brand_safety/
│   └── main.py
├── 03_autogen_editorial/
│   └── workflow.py
├── 04_secure_agent_comms/
│   ├── main.py
│   ├── agents.py
│   └── demo.py
├── 05_keystore_persistence/
│   ├── demo.py
│   └── README.md
├── 06_key_backup/
│   ├── demo.py
│   └── README.md
├── 07_raw_signatures/
│   ├── demo.py
│   └── README.md
└── 08_fast_routing/
    ├── server.py
    ├── demo.py
    └── README.md
```

### didlite Package Management
- **Source**: Private GitHub repository at `git@github.com:jondepalma/didlite-pkg.git`
- **Version**: v0.2.3 (main branch)
- **Installation**: Added as git submodule, installed locally as editable package
- **Strategy**: Single submodule supports all eight example applications (no duplication)

## Examples

### 1. FastAPI CMS (`01_fastapi_cms/`)
**Concept**: The Headless CMS - Cryptographically verified content publishing
- Uses `didlite.verify_jws()` as a FastAPI dependency
- Validates `Authorization: Bearer <token>` headers
- Demonstrates: Cryptographic identity verification replacing traditional API keys
- Key Function: `verify_agent()` dependency
- Run: `python 01_fastapi_cms/cms_server.py`

### 2. LangChain Brand Safety (`02_langchain_brand_safety/`)
**Concept**: The Brand Guardian - Preventing unauthorized social media posts
- LangChain tool that validates signed tokens before executing sensitive operations
- Prevents LLM hallucination of permissions
- Demonstrates: Pre-authorization pattern with signature verification
- Key Functions: `publish_tweet()`, brand safety controls
- Run: `python 02_langchain_brand_safety/main.py`

### 3. AutoGen Editorial Workflow (`03_autogen_editorial/`)
**Concept**: The Chain of Custody - Multi-agent workflow with identity verification
- Editor Agent verifies copywriter identity before reviewing drafts
- Demonstrates message tampering detection and imposter rejection
- Key Functions: `create_signed_message()`, `verify_incoming_message()`
- Run: `python 03_autogen_editorial/workflow.py`

### 4. Secure Agent Communications (`04_secure_agent_comms/`)
**Concept**: Full-featured secure agent communication system
- Complete FastAPI application with multiple attack scenario demonstrations
- Nonce-based replay protection, forgery attempts, message interception
- Interactive API documentation
- Run: `python 04_secure_agent_comms/main.py` (server), `python 04_secure_agent_comms/demo.py` (demo)

### 5. KeyStore Persistence (`05_keystore_persistence/`)
**Concept**: The Reboot - Maintaining agent identity across restarts
- Demonstrates three KeyStore backends: Memory, Environment Variables, Encrypted Files
- Shows identity persistence strategies for different deployment scenarios
- Deployment strategy comparison for testing, containers, and edge devices
- Run: `python 05_keystore_persistence/demo.py`

### 6. Key Backup and Recovery (`06_key_backup/`)
**Concept**: The Backup - Exporting agent keys for disaster recovery
- Key export/import in JWK (web-friendly) and PEM (OpenSSL-compatible) formats
- Public key sharing for verification-only scenarios
- Cross-system migration demonstrations
- Run: `python 06_key_backup/demo.py`

### 7. Raw Signature Verification (`07_raw_signatures/`)
**Concept**: The Custom Protocol - Signing binary data without JWS overhead
- Low-level signing operations for IoT sensors, file integrity, custom protocols
- Demonstrates tamper detection and minimal-overhead signing
- Overhead comparison: JWS vs Raw signatures
- Run: `python 07_raw_signatures/demo.py`

### 8. Fast Routing with extract_signer_did() (`08_fast_routing/`)
**Concept**: The Performance Optimizer - Fast DID extraction for rate limiting and routing
- Uses `extract_signer_did()` for ~2x faster DID extraction without full verification
- Rate limiting by agent tier before expensive signature verification
- Request routing, audit logging, and DDoS protection
- Performance benchmarking shows ~50% CPU savings on rejected requests
- Run: `python 08_fast_routing/server.py` (server), `python 08_fast_routing/demo.py` (demo)

## Key Concepts

### Identity is Local
- No servers or databases required for identity verification
- Self-sovereign identity model

### DID = Public Key
- Format: `did:key:z6Mk...`
- The DID itself contains the cryptographic material needed for verification
- Based on W3C Decentralized Identifiers standard

### JWS (JSON Web Signatures)
- Standard transport envelope for signed messages
- Functions: `didlite.create_jws()`, `didlite.verify_jws()`
- Payload verification without external lookups

## Development Setup

### Initial Setup
```bash
# Clone with submodule
git clone --recurse-submodules <repo-url>

# Or if already cloned
git submodule update --init --recursive

# Create and activate virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install didlite as editable
pip install -e ./didlite-pkg

# Install all dependencies
pip install -r requirements.txt
```

### Running Examples
Each example is self-contained and can be run directly:
```bash
python 01_fastapi_cms/cms_server.py
python 02_langchain_brand_safety/main.py
python 03_autogen_editorial/workflow.py
python 04_secure_agent_comms/main.py  # Server (then run demo.py in another terminal)
python 05_keystore_persistence/demo.py
python 06_key_backup/demo.py
python 07_raw_signatures/demo.py
python 08_fast_routing/server.py  # Server (then run demo.py in another terminal)
```

## Dependencies
- **didlite**: v0.2.3+ (installed from submodule)
- **fastapi**: Web framework for Examples 1, 4, 8
- **uvicorn**: ASGI server for FastAPI
- **langchain**: LLM framework for Example 2
- **langchain-openai**: OpenAI integration (dummy key mode)
- **pyautogen**: Multi-agent framework for Example 3
- **requests**: HTTP client for API testing
- **cryptography**: For FileKeyStore encryption (Example 5)

## Environment Notes
- This is a **demonstration/educational environment**
- No actual API keys required (dummy keys used where needed)
- Examples are self-contained simulations
- Focus is on cryptographic identity patterns, not production deployment

## Git Workflow
- Main branch: `main`
- Development branch: `dev`
- didlite submodule tracks: `main` branch at v0.2.3
- dev-design folder: Untracked (for context management)

## Testing Strategy
See [TESTING.md](TESTING.md) for complete testing guide covering all 8 examples.

Quick test all examples:
```bash
# Activate venv
source venv/bin/activate

# Test standalone examples (1-3, 5-7)
python 01_fastapi_cms/cms_server.py
python 02_langchain_brand_safety/main.py
python 03_autogen_editorial/workflow.py
python 05_keystore_persistence/demo.py
python 06_key_backup/demo.py
python 07_raw_signatures/demo.py

# Test client-server examples (4, 8)
# Terminal 1: python 04_secure_agent_comms/main.py
# Terminal 2: python 04_secure_agent_comms/demo.py

# Terminal 1: python 08_fast_routing/server.py
# Terminal 2: python 08_fast_routing/demo.py
```

## Security Patterns Demonstrated
1. **Signature Verification**: All examples use `verify_jws()` or raw signatures to validate authenticity
2. **Zero-Knowledge Architecture**: No central authority or database required
3. **Tamper Detection**: Modified tokens are rejected (Examples 2, 3, 7)
4. **Intent Verification**: Payload claims must match function arguments (Example 2)
5. **Replay Protection**: Nonce tracking prevents token reuse (Example 4)
6. **Persistent Identity**: KeyStore backends maintain identity across restarts (Example 5)
7. **Disaster Recovery**: Key backup/restore in standard formats (Example 6)
8. **Custom Protocols**: Raw signatures for minimal-overhead use cases (Example 7)
9. **Performance Optimization**: Fast DID extraction for rate limiting and routing (Example 8)

## Key Features by Example

| Example | Feature | Pattern |
|---------|---------|---------|
| 1 | CMS Publishing | API Authentication |
| 2 | Brand Safety | Pre-authorization |
| 3 | Editorial Workflow | Chain of Custody |
| 4 | Secure Messaging | Replay Protection |
| 5 | Identity Persistence | Deployment Strategies |
| 6 | Key Backup | Disaster Recovery |
| 7 | Raw Signatures | Custom Protocols |
| 8 | Fast Routing | Performance Optimization |
