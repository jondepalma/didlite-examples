# Example 7: Raw Signature Verification (Non-JWS)

## The Concept: "The Custom Protocol"

JWS (JSON Web Signatures) are great for web APIs, but what about signing binary sensor data, images, or custom protocols? This example demonstrates using didlite's low-level signing capabilities for scenarios where JWS overhead is unnecessary.

## The Problem

JWS tokens are powerful but come with overhead:
- JSON encoding adds ~300+ bytes minimum
- Base64 encoding increases size by ~33%
- Parsing JSON is computationally expensive
- Binary data must be encoded to fit JSON

For resource-constrained devices (IoT sensors, embedded systems), this overhead can be significant.

## The Solution: Raw Signatures

`didlite` provides direct access to Ed25519 signature operations:

```python
# Sign raw bytes
signature = agent.sign(data)  # Returns 64-byte signature

# Verify manually
verify_key = resolve_did_to_key(agent.did)
verify_key.verify(data, signature)  # Raises exception if invalid
```

## Running the Example

```bash
python 07_raw_signatures/demo.py
```

## What You'll See

The demo runs four scenarios:

1. **Basic Raw Signing** - Sign binary sensor data without JWS wrapper
2. **Tamper Detection** - Show signature invalidation when data is modified
3. **File Integrity** - Sign and verify entire files
4. **Custom Protocol** - Design a binary protocol with signature verification

Each scenario demonstrates:
- Signing arbitrary binary data
- Manual signature verification using `resolve_did_to_key()`
- Tamper detection capabilities
- Overhead comparison with JWS

## Key Takeaways

### When to Use Raw Signatures

| Scenario | Use Raw Signatures? | Why |
|----------|-------------------|-----|
| IoT sensor telemetry | ✅ Yes | Minimal bandwidth, binary data |
| File integrity checks | ✅ Yes | Large files, no JSON needed |
| Firmware signing | ✅ Yes | Binary format, embedded systems |
| Custom protocols | ✅ Yes | Full control over message format |
| Web API tokens | ❌ No | JWS is standard, interoperable |
| User authentication | ❌ No | JWS provides expiration, metadata |

### Overhead Comparison

**Example: 4-byte temperature reading**

| Method | Data | Signature | Metadata | Total | Overhead |
|--------|------|-----------|----------|-------|----------|
| Raw | 4 bytes | 64 bytes | Custom | 68+ bytes | 64 bytes (16x) |
| JWS | 4 bytes | 64 bytes | ~300 bytes | ~370 bytes | ~366 bytes (91x) |

For tiny payloads, raw signatures have less overhead than JWS tokens.

## Code Highlights

### Basic Raw Signing
```python
from didlite import AgentIdentity, resolve_did_to_key

# Sender: Sign binary data
sensor = AgentIdentity()
data = b"\x00\x18\x05\x02"  # 4 bytes of binary telemetry
signature = sensor.sign(data)

# Receiver: Verify signature
verify_key = resolve_did_to_key(sensor.did)
verify_key.verify(data, signature)  # Raises BadSignatureError if invalid
```

### File Signing Pattern
```python
# Sign a file
with open("firmware.bin", "rb") as f:
    file_data = f.read()

signature = agent.sign(file_data)

# Save signature alongside file
with open("firmware.bin.sig", "wb") as f:
    f.write(signature)

# Verify later
with open("firmware.bin", "rb") as f:
    data = f.read()
with open("firmware.bin.sig", "rb") as f:
    sig = f.read()

verify_key = resolve_did_to_key(agent.did)
verify_key.verify(data, sig)  # Confirms file integrity
```

### Custom Binary Protocol
```python
import struct

# Design your protocol
# [Version:1][Type:1][Timestamp:4][Payload:N][Signature:64]

def create_message(agent, msg_type, payload):
    header = struct.pack('>BB', 1, msg_type)  # Version, Type
    timestamp = struct.pack('>I', int(time.time()))
    unsigned = header + timestamp + payload
    signature = agent.sign(unsigned)
    return unsigned + signature

def verify_message(did, message):
    unsigned = message[:-64]
    signature = message[-64:]
    verify_key = resolve_did_to_key(did)
    verify_key.verify(unsigned, signature)
    return unsigned  # Parse header/payload
```

## How It Works

### Ed25519 Signature Mechanics
1. **Signing:** `signature = private_key.sign(message)`
   - Produces 64-byte signature
   - Deterministic (same message + key = same signature)
   - Fast (~50,000 signatures/second on Raspberry Pi)

2. **Verification:** `public_key.verify(message, signature)`
   - Returns silently if valid
   - Raises `BadSignatureError` if invalid
   - Fast (~20,000 verifications/second)

3. **Security:** 128-bit security level (equivalent to AES-128)

### DID Resolution
```python
# DID contains the public key
did = "did:key:z6Mk..."

# Extract public key (no network calls!)
verify_key = resolve_did_to_key(did)

# Use for verification
verify_key.verify(data, signature)
```

The `did:key` method encodes the public key directly in the DID string, so resolution is purely local (no database or network required).

## Security Notes

### Educational Demo Disclaimer
This example demonstrates raw signature mechanics for educational purposes.

### Production Considerations

When designing custom protocols with raw signatures:

**DO:**
- ✅ Include timestamps to prevent replay attacks
- ✅ Add nonces for one-time-use messages
- ✅ Use domain separation (different prefixes for different contexts)
- ✅ Include version numbers for protocol evolution
- ✅ Document your protocol specification
- ✅ Add message type identifiers

**DON'T:**
- ❌ Sign the same data in multiple contexts (use domain separation)
- ❌ Reuse signatures across different protocols
- ❌ Forget to include metadata (timestamps, sequence numbers)
- ❌ Skip input validation before verification
- ❌ Log or expose signature bytes unnecessarily

### Replay Attack Prevention
```python
# Bad: Just sign the payload
signature = agent.sign(payload)

# Good: Include timestamp and nonce
import struct, time, secrets
timestamp = int(time.time())
nonce = secrets.token_bytes(16)
message = struct.pack('>I', timestamp) + nonce + payload
signature = agent.sign(message)
```

### Domain Separation
```python
# Prevent cross-protocol attacks
PROTOCOL_PREFIX = b"SENSOR_V1:"
message = PROTOCOL_PREFIX + payload
signature = agent.sign(message)
```

## Use Cases

### 1. IoT Sensor Networks
- Sensors: 100,000 temperature sensors
- Bandwidth: Cellular (limited)
- Frequency: Every 60 seconds
- **Solution:** Raw signatures minimize data usage

### 2. Firmware Signing
- Format: Binary firmware images
- Size: 1-100 MB
- Verification: Bootloader (embedded)
- **Solution:** Sign firmware, verify before flashing

### 3. Video Surveillance
- Format: H.264 video frames
- Authenticity: Prove frame not tampered
- Storage: Long-term archive
- **Solution:** Sign frame hash, store signature

### 4. Industrial Control
- Format: Binary control commands
- Latency: < 10ms critical
- Security: Prevent unauthorized commands
- **Solution:** Sign commands, reject invalid

## JWS vs Raw: Decision Matrix

Use **JWS** when:
- ✅ Building web APIs (REST, GraphQL)
- ✅ Need standard JWT compatibility
- ✅ Want built-in expiration (`exp` claim)
- ✅ Payload is JSON-serializable
- ✅ Interoperability with auth libraries

Use **Raw** when:
- ✅ Working with binary data (images, sensors, files)
- ✅ Bandwidth is critical (IoT, satellite)
- ✅ Custom protocol design needed
- ✅ Embedded systems (limited CPU/memory)
- ✅ Maximum performance required

**Both are equally secure** - Ed25519 provides 128-bit security in both cases.

## Performance Characteristics

**Raspberry Pi 5 (2.4GHz ARM64):**
- Signing: ~50,000 operations/second
- Verification: ~20,000 operations/second
- Signature size: 64 bytes (fixed)
- No network calls for DID resolution

**Bandwidth Savings:**
| Payload | JWS Token | Raw Signature | Savings |
|---------|-----------|---------------|---------|
| 4 bytes | ~370 bytes | 68 bytes | 81% |
| 100 bytes | ~466 bytes | 164 bytes | 65% |
| 1 KB | ~2.4 KB | 1.06 KB | 56% |

## Related Examples

- **Example 1:** FastAPI Gatekeeper (JWS-based authentication)
- **Example 4:** Secure Agent Communications (JWS tokens)
- **Example 6:** Key export/import (for signing key backup)

## Files Created

The demo creates temporary test files:
- `sensor_config.bin` - Example configuration file (cleaned up)
- `sensor_config.bin.sig` - Signature file (cleaned up)

All demo artifacts are cleaned up automatically.

## When to Avoid Raw Signatures

Don't use raw signatures when:
- You need built-in expiration (use JWS with `exp` claim)
- You want standard interoperability (JWS is RFC 7515)
- Your payload is already JSON (JWS is natural fit)
- You're building a web API (JWS is expected)
- Team is unfamiliar with low-level crypto (JWS is safer)

## Additional Resources

- [Ed25519 High-Speed Signatures](https://ed25519.cr.yp.to/)
- [PyNaCl Documentation](https://pynacl.readthedocs.io/)
- [RFC 7515 (JWS Spec)](https://tools.ietf.org/html/rfc7515)
