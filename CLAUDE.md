# CLAUDE.md - didlite-examples Project Guide

## Project Overview
This repository demonstrates how to integrate `didlite` (Decentralized Identity for Agents) into major AI frameworks. It contains four example applications showing different use cases for agent identity and cryptographic verification.

## Architecture

### Repository Structure
```
didlite-examples/
├── README.md
├── requirements.txt
├── didlite-pkg/                    # Git submodule (private repo)
├── 01_fastapi_gatekeeper/
│   └── server.py
├── 02_langchain_secure_tool/
│   └── main.py
├── 03_autogen_handshake/
│   └── simulation.py
└── 04_secure_agent_comms/
    └── [migrated from separate repo]
```

### didlite Package Management
- **Source**: Private GitHub repository at `git@github.com:jondepalma/didlite-pkg.git`
- **Version**: v0.2.0 (main branch)
- **Installation**: Added as git submodule, installed locally as editable package
- **Strategy**: Single submodule supports all four example applications (no duplication)

## Examples

### 1. FastAPI Gatekeeper (`01_fastapi_gatekeeper/`)
**Concept**: The Gatekeeper - Protecting API endpoints without API keys
- Uses `didlite.verify_jws()` as a FastAPI dependency
- Validates `Authorization: Bearer <token>` headers
- Demonstrates: Cryptographic identity verification replacing traditional API keys
- Key Function: `verify_agent()` dependency

### 2. LangChain Secure Tool (`02_langchain_secure_tool/`)
**Concept**: The Secure Tool - Tool execution requires cryptographic signatures
- LangChain tool that validates signed tokens before executing sensitive operations
- Prevents LLM hallucination of permissions
- Demonstrates: Pre-authorization pattern with signature verification
- Key Functions: `execute_secure_payment()`, `sign_and_execute()`

### 3. AutoGen Handshake (`03_autogen_handshake/`)
**Concept**: The Handshake - Multi-agent message signing and verification
- Two autonomous agents exchange cryptographically signed messages
- Demonstrates message tampering detection
- Key Functions: `create_signed_message()`, `verify_incoming_message()`

### 4. Secure Agent Communications (`04_secure_agent_comms/`)
**Concept**: Secure agent communication simulation
- Migrated from existing repository: `git@github.com:jondepalma/secure-agent-comms.git`
- Uses shared didlite submodule (no duplication)
- [Details to be documented after migration]

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

# Note: didlite has an undeclared dependency on cryptography
# If you get "ModuleNotFoundError: No module named 'cryptography'", install it:
pip install cryptography

# Install all dependencies
pip install -r requirements.txt
```

### Known Issues
- **Missing cryptography dependency**: The didlite package imports `cryptography` but doesn't declare it in `setup.py`. Install manually with `pip install cryptography` if needed.

### Running Examples
Each example is self-contained and can be run directly:
```bash
python 01_fastapi_gatekeeper/server.py
python 02_langchain_secure_tool/main.py
python 03_autogen_handshake/simulation.py
python 04_secure_agent_comms/[main_file].py
```

## Dependencies
- **didlite**: v0.2.0+ (installed from submodule)
- **fastapi**: Web framework for Example 1
- **uvicorn**: ASGI server for FastAPI
- **langchain**: LLM framework for Example 2
- **langchain-openai**: OpenAI integration (dummy key mode)
- **pyautogen**: Multi-agent framework for Example 3
- **requests**: HTTP client for API testing

## Environment Notes
- This is a **demonstration/educational environment**
- No actual API keys required (dummy keys used where needed)
- Examples are self-contained simulations
- Focus is on cryptographic identity patterns, not production deployment

## Git Workflow
- Main branch: `main`
- didlite submodule tracks: `main` branch at v0.2.0
- dev-design folder: Untracked (for context management)

## Testing Strategy
1. Set up project structure and migrate Example 4 first
2. Validate didlite package installation works correctly
3. Build and test Examples 1-3 incrementally

## Security Patterns Demonstrated
1. **Signature Verification**: All examples use `verify_jws()` to validate authenticity
2. **Zero-Knowledge Architecture**: No central authority or database
3. **Tamper Detection**: Modified tokens are rejected (see Example 3)
4. **Intent Verification**: Payload claims must match function arguments (see Example 2)

## Future Enhancements
- Additional framework integrations
- Production deployment examples
- Performance benchmarking
- Integration testing suite
