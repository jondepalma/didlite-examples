# Example 6: Key Backup, Export, and Recovery

## The Concept: "The Backup"

What happens if your agent's identity is lost due to hardware failure, accidental deletion, or system migration? This example demonstrates how to backup, export, and restore agent identities using standard cryptographic key formats.

## The Problem

Without key backup capabilities:
- Hardware failure destroys agent identity permanently
- Cannot migrate agents between systems
- No disaster recovery plan for critical agents
- Cannot share public keys with verifiers
- Agent reputation lost on system rebuild

## The Solution: Key Import/Export

`didlite` supports two industry-standard key formats:

### 1. JWK (JSON Web Key)
- **Format:** JSON
- **Standard:** RFC 7517
- **Use Case:** Modern web APIs, microservices, cloud platforms
- **Benefits:** Web-friendly, easy to parse, compact

### 2. PEM (Privacy Enhanced Mail)
- **Format:** Base64-encoded DER with headers
- **Standard:** RFC 7468
- **Use Case:** OpenSSL, enterprise tools, traditional infrastructure
- **Benefits:** Industry standard, OpenSSL compatible

## Running the Example

```bash
python 06_key_backup/demo.py
```

## What You'll See

The demo runs four scenarios:

1. **JWK Roundtrip** - Export to JWK, save to file, restore, verify old tokens still work
2. **PEM Roundtrip** - Export to PEM, save to file, restore, show OpenSSL compatibility
3. **Public Key Sharing** - Export public key only (safe to share)
4. **Cross-System Migration** - Migrate agent identity from dev to prod

Each scenario demonstrates:
- Key export in the format
- Saving to file (backup)
- Restoring from file (recovery)
- Verifying old tokens with restored identity

## Key Takeaways

### Why Backup Matters
- **Disaster Recovery:** Restore agent identity after system failure
- **Migration:** Move agents between environments (dev → staging → prod)
- **Compliance:** Some regulations require key archival
- **Business Continuity:** Critical agents can be recovered
- **Interoperability:** Share public keys with external verifiers

### JWK vs PEM: When to Use Each

| Scenario | Format | Why |
|----------|--------|-----|
| REST API backup | JWK | JSON integrates with web services |
| AWS KMS storage | JWK | Cloud key vaults prefer JSON |
| OpenSSL integration | PEM | Native OpenSSL format |
| SSH-like workflow | PEM | Similar to SSH key management |
| Enterprise PKI | PEM | Standard for enterprise systems |
| Maximum compatibility | Both | Export in both formats |

## Code Highlights

### JWK Export/Import
```python
from didlite import AgentIdentity
import json

# Export
agent = AgentIdentity()
jwk_data = agent.to_jwk(include_private=True)
with open("backup.jwk", "w") as f:
    json.dump(jwk_data, f)

# Import
with open("backup.jwk", "r") as f:
    jwk = json.load(f)
restored = AgentIdentity.from_jwk(jwk)

# Same identity!
assert agent.did == restored.did
```

### PEM Export/Import
```python
# Export
pem_private = agent.to_pem(include_private=True)
with open("backup.pem", "w") as f:
    f.write(pem_private)

# Import
with open("backup.pem", "r") as f:
    pem_data = f.read()
restored = AgentIdentity.from_pem(pem_data)

# Same identity!
assert agent.did == restored.did
```

### Public Key Only (Safe to Share)
```python
# Export public key only
public_jwk = agent.to_jwk(include_private=False)
public_pem = agent.to_pem(include_private=False)

# Can be shared publicly - cannot create signatures
# Only used for verification
```

## How It Works

### Asymmetric Cryptography Refresher
- **Private Key:** Can sign messages (must be kept secret)
- **Public Key:** Can verify signatures (safe to share)
- **Same Key Pair:** Export/import preserves the cryptographic relationship

### Key Format Internals

**JWK Structure:**
```json
{
  "kty": "OKP",           // Key Type: Octet Key Pair
  "crv": "Ed25519",       // Curve: Ed25519
  "x": "base64url(...)",  // Public key (32 bytes)
  "d": "base64url(...)"   // Private key (32 bytes, only in private export)
}
```

**PEM Structure:**
```
-----BEGIN PRIVATE KEY-----
MIGEAgEAMBAGByqGSM49AgEGBS...  (Base64-encoded DER)
-----END PRIVATE KEY-----
```

## Security Notes

### Educational Demo Disclaimer
This example demonstrates key export/import mechanics for educational purposes.

### Production Best Practices

**DO:**
- ✅ Encrypt backups before storing (GPG, age, or enterprise key vault)
- ✅ Use access controls on backup files (file permissions, ACLs)
- ✅ Store backups in secure locations (encrypted volumes, HSM)
- ✅ Implement audit logging for all key operations
- ✅ Use multi-party authorization for critical key access
- ✅ Test restore procedures regularly

**DON'T:**
- ❌ Store private keys in git repositories
- ❌ Email private keys (even encrypted)
- ❌ Store backups in cloud storage without encryption
- ❌ Log private key material
- ❌ Include private keys in error messages
- ❌ Store long-term in environment variables

### Encryption Recommendations

Before storing backups:

```bash
# GPG encryption
gpg --symmetric --cipher-algo AES256 backup.jwk

# age encryption (modern alternative)
age -p backup.jwk > backup.jwk.age

# OpenSSL encryption
openssl enc -aes-256-cbc -salt -in backup.jwk -out backup.jwk.enc
```

## Use Cases

### 1. Disaster Recovery
Agent's system crashes → Restore from encrypted backup → Agent resumes operation with same identity and reputation

### 2. Environment Migration
Dev agent tested → Export key → Import to staging → Import to production → Same identity across all environments

### 3. Key Archival
Regulatory compliance requires → Export keys when decommissioning agent → Store in compliance archive → Can verify old signatures years later

### 4. Public Key Distribution
Agent publishes public key → Verifiers download public JWK → Can verify agent's signatures without private key

### 5. OpenSSL Integration
Export to PEM → Use with OpenSSL tools → Generate CSRs, integrate with PKI → Enterprise certificate workflows

## OpenSSL Compatibility

The PEM files are compatible with standard OpenSSL commands:

```bash
# Inspect private key
openssl pkey -in agent_private.pem -text -noout

# Inspect public key
openssl pkey -pubin -in agent_public.pem -text -noout

# Extract public key from private key
openssl pkey -in agent_private.pem -pubout -out extracted_public.pem
```

## Related Examples

- **Example 5:** KeyStore persistence (automated key storage)
- **Example 7:** Raw signatures (using exported keys directly)
- **Example 4:** Secure communications (using persistent identities)

## Files Created

The demo creates temporary files to demonstrate the backup/restore process:
- `agent_backup.jwk` - JWK format backup (cleaned up automatically)
- `agent_private.pem` - Private key in PEM format (cleaned up)
- `agent_public.pem` - Public key in PEM format (cleaned up)
- `agent_public.jwk` - Public JWK (cleaned up)
- `agent_migration.json` - Migration package (cleaned up)

All demo artifacts are cleaned up at the end of each scenario.

## When to Use This Example

Use key export/import when you need:
- **Disaster recovery planning** for critical agents
- **Cross-environment migration** (dev/staging/prod)
- **Compliance archival** of cryptographic keys
- **Public key distribution** to external verifiers
- **OpenSSL integration** with enterprise PKI
- **Key backup automation** in deployment pipelines
