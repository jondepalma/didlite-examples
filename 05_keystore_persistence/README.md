# Example 5: Persistent Identity with KeyStore Backends

## The Concept: "The Reboot"

What happens when an agent restarts? Does it lose its identity and reputation? This example demonstrates how agents maintain their cryptographic identity across restarts using different storage backends.

## The Problem

Without persistent identity:
- An IoT sensor loses its reputation every time it reboots
- A containerized agent gets a new identity on every deployment
- No way to track which agent signed which messages over time

## The Solution: KeyStore Backends

`didlite` provides three storage backends for different deployment scenarios:

### 1. MemoryKeyStore (Ephemeral)
- **Storage:** RAM only
- **Persistence:** None - identity lost on restart
- **Use Case:** Testing, temporary agents, one-time operations
- **Security:** Fast but ephemeral

### 2. EnvKeyStore (Container-Friendly)
- **Storage:** Environment variables
- **Persistence:** Yes - survives container restarts
- **Use Case:** Docker, Kubernetes, cloud platforms, 12-factor apps
- **Security:** Base64 encoded, accessible to process

### 3. FileKeyStore (Edge Device)
- **Storage:** Encrypted files on disk
- **Persistence:** Yes - survives reboots
- **Use Case:** IoT devices, Raspberry Pi, edge AI, offline systems
- **Security:** Fernet encryption (AES-128-CBC + HMAC)

## Running the Example

```bash
python 05_keystore_persistence/demo.py
```

## What You'll See

The demo runs three scenarios:

1. **MemoryKeyStore** - Shows identity changing on restart
2. **EnvKeyStore** - Shows identity persisting via environment variables
3. **FileKeyStore** - Shows identity persisting via encrypted files

Each scenario:
- Creates an agent identity
- Signs a message
- Simulates a restart
- Verifies the identity is preserved (or not)
- Shows verification of old tokens with restored identity

## Key Takeaways

### Why This Matters
- **Reputation:** Agents build reputation over time with stable identities
- **Auditability:** Track which agent signed which messages historically
- **Trust:** Verifiers can build allow-lists of trusted agent DIDs
- **Recovery:** Agents can be restored after crashes or upgrades

### Choosing the Right Backend

| Scenario | Backend | Why |
|----------|---------|-----|
| Unit testing | MemoryKeyStore | Fast, no cleanup needed |
| AWS Lambda | EnvKeyStore | Fits serverless model |
| Kubernetes | EnvKeyStore | ConfigMaps/Secrets integration |
| Raspberry Pi | FileKeyStore | Local encrypted storage |
| IoT sensor | FileKeyStore | No external dependencies |
| Temporary task | MemoryKeyStore | Doesn't need persistence |

## Code Highlights

### Creating Persistent Identity
```python
from didlite import AgentIdentity
from didlite.keystore import FileKeyStore

# First boot
keystore = FileKeyStore(storage_dir="./keys", password="secure-password")
agent = AgentIdentity(keystore=keystore, identifier="sensor-001")
print(f"DID: {agent.did}")  # did:key:z6Mk...

# After reboot (same keystore config)
keystore2 = FileKeyStore(storage_dir="./keys", password="secure-password")
agent2 = AgentIdentity(keystore=keystore2, identifier="sensor-001")
print(f"DID: {agent2.did}")  # SAME did:key:z6Mk...
```

### How It Works
1. On first run, `AgentIdentity` generates a new Ed25519 seed
2. The seed is saved to the KeyStore (encrypted for FileKeyStore)
3. On subsequent runs, the same seed is loaded
4. Same seed → same private key → same DID
5. Old tokens can still be verified with the restored identity

## Security Notes

### Educational Demo Disclaimer
This example uses simplified security for educational clarity:
- Passwords are hardcoded (use env vars or HSMs in production)
- No key rotation policies
- No audit logging
- File permissions may vary by OS

### Production Best Practices
- **Never hardcode passwords** - use environment variables, Vault, or KMS
- **Use HSM/TPM** for high-security deployments (banks, healthcare)
- **Implement key rotation** - rotate keys periodically
- **Add audit logging** - log all key operations
- **Encrypt volumes** - use encrypted filesystems for FileKeyStore
- **Restrict access** - use file permissions, SELinux, or container policies

## When NOT to Use Persistent Identity

Some scenarios benefit from ephemeral identities:
- **Throwaway test agents** - use MemoryKeyStore
- **Privacy-focused agents** - generate new identity per session
- **Load testing** - generate many temporary identities
- **Anonymous operations** - new identity prevents tracking

## Related Examples

- **Example 6:** Key backup and recovery (JWK/PEM export)
- **Example 4:** Secure agent communications (uses deterministic seeds)
- **Example 9:** IoT fleet management (FileKeyStore at scale)

## Files Created

The demo creates temporary files in:
- `./demo_keys/` - Encrypted key files (cleaned up automatically)
- Environment variables: `DEMO_AGENT_SENSOR-001` (cleaned up automatically)

All demo artifacts are cleaned up at the end of the script.
