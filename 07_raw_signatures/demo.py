"""
Raw Signature Verification (Non-JWS)

Demonstrates using didlite for signing and verifying arbitrary binary data
without the JWS (JSON Web Signature) wrapper. This is useful for:
- Custom protocols where JWS overhead is unnecessary
- Binary data signing (sensor readings, images, files)
- Low-level cryptographic operations
- Integration with existing signature schemes

Key concepts:
- agent.sign(bytes) - Sign raw binary data
- resolve_did_to_key(did) - Extract public key from DID
- verify_key.verify(data, signature) - Manual verification

⚠️  EDUCATIONAL DEMO DISCLAIMER

This example demonstrates low-level signature operations for educational purposes.

When to use raw signatures vs JWS:
- Use JWS: Web APIs, tokens, structured payloads, standard interoperability
- Use Raw: Custom protocols, binary data, minimal overhead, embedded systems

Production considerations:
- Add metadata (timestamps, nonces) to prevent replay attacks
- Include payload type identifier to prevent cross-protocol attacks
- Use domain separation (different prefixes) for different contexts
- Implement proper error handling and logging
"""

import time
import struct
from didlite import AgentIdentity, resolve_did_to_key
from nacl.exceptions import BadSignatureError


def print_section(title):
    """Print a visual section separator"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def scenario_1_basic_signing():
    """
    Scenario 1: Basic Raw Data Signing

    Sign arbitrary binary data and verify the signature manually
    without using the JWS wrapper.
    """
    print_section("SCENARIO 1: Basic Raw Data Signing")

    print("\n📝 Use Case: Sign binary sensor data, custom protocols")
    print("   No JWS overhead - just raw Ed25519 signatures\n")

    # Step 1: Create IoT sensor identity
    print("▶ Step 1: Creating IoT sensor identity...")
    sensor = AgentIdentity()
    print(f"   Sensor DID: {sensor.did}")

    # Step 2: Create raw binary telemetry data
    print("\n▶ Step 2: Creating raw telemetry data...")
    # Example: Temperature reading 24.5°C encoded as 4 bytes
    temperature = 24.5
    telemetry = struct.pack('>f', temperature)  # Big-endian float
    print(f"   Temperature: {temperature}°C")
    print(f"   Binary data (hex): {telemetry.hex()}")
    print(f"   Data size: {len(telemetry)} bytes")

    # Step 3: Sign the raw data
    print("\n▶ Step 3: Signing raw data...")
    signature = sensor.sign(telemetry)
    print(f"   Signature (hex): {signature.hex()}")
    print(f"   Signature size: {len(signature)} bytes (Ed25519 = 64 bytes)")

    # Step 4: Manual verification
    print("\n▶ Step 4: Manual verification (without JWS)...")
    verify_key = resolve_did_to_key(sensor.did)
    print(f"   Resolved public key from DID")

    try:
        verify_key.verify(telemetry, signature)
        print(f"   ✅ Signature VALID - Data integrity confirmed!")
        print(f"   Temperature reading is authentic: {temperature}°C")
    except BadSignatureError:
        print(f"   ❌ Signature INVALID - Data tampered or wrong signer")

    print("\n💡 Key Advantage:")
    print("   No JSON/Base64 overhead - minimal bandwidth for IoT devices")
    print(f"   JWS token would be ~{len(telemetry) * 8}+ bytes")
    print(f"   Raw signature is only {len(signature)} bytes + {len(telemetry)} bytes data")


def scenario_2_tampering_detection():
    """
    Scenario 2: Tamper Detection

    Demonstrate that modifying signed data invalidates the signature.
    """
    print_section("SCENARIO 2: Tamper Detection")

    print("\n📝 Use Case: Detect data manipulation in transit")
    print("   Signature verification fails if data is modified\n")

    # Step 1: Create sensor and sign data
    print("▶ Step 1: Sensor creates and signs temperature reading...")
    sensor = AgentIdentity()
    original_temp = 24.5
    original_data = struct.pack('>f', original_temp)
    signature = sensor.sign(original_data)

    print(f"   Sensor DID: {sensor.did[:30]}...")
    print(f"   Original temp: {original_temp}°C")
    print(f"   Data (hex): {original_data.hex()}")
    print(f"   Signature (hex): {signature.hex()[:40]}...")

    # Step 2: Attacker modifies data in transit
    print("\n▶ Step 2: Attacker intercepts and modifies data...")
    tampered_temp = 99.9  # Attacker changes temperature!
    tampered_data = struct.pack('>f', tampered_temp)

    print(f"   ⚠️  ATTACK: Temperature changed to {tampered_temp}°C")
    print(f"   Original data: {original_data.hex()}")
    print(f"   Tampered data: {tampered_data.hex()}")

    # Step 3: Verifier checks signature
    print("\n▶ Step 3: Verifier checks signature...")
    verify_key = resolve_did_to_key(sensor.did)

    print("\n   Verifying ORIGINAL data:")
    try:
        verify_key.verify(original_data, signature)
        print(f"   ✅ Signature VALID - Original data is authentic")
    except BadSignatureError:
        print(f"   ❌ Signature INVALID")

    print("\n   Verifying TAMPERED data:")
    try:
        verify_key.verify(tampered_data, signature)
        print(f"   ✅ Signature VALID - This should NOT happen!")
    except BadSignatureError:
        print(f"   ❌ TAMPER DETECTED - Signature invalid for modified data")
        print(f"   🛡️  Attack blocked! Original signature doesn't match")

    print("\n💡 Security Property:")
    print("   Cryptographic signatures are computationally infeasible to forge")
    print("   Even a single bit change invalidates the signature")


def scenario_3_file_signing():
    """
    Scenario 3: File Integrity Verification

    Sign an entire file and verify its integrity.
    """
    print_section("SCENARIO 3: File Integrity Verification")

    print("\n📝 Use Case: Verify file integrity, software updates, data archives")
    print("   Sign arbitrary files with agent identity\n")

    # Step 1: Create a test file
    print("▶ Step 1: Creating test file...")
    test_file = "sensor_config.bin"
    config_data = b"SENSOR_ID=001\nREPORT_INTERVAL=60\nTHRESHOLD=25.0\n"

    with open(test_file, "wb") as f:
        f.write(config_data)

    print(f"   File: {test_file}")
    print(f"   Size: {len(config_data)} bytes")
    print(f"   Content:\n{config_data.decode()}")

    # Step 2: Sign the file
    print("▶ Step 2: Signing file...")
    admin = AgentIdentity()
    print(f"   Admin DID: {admin.did[:30]}...")

    signature = admin.sign(config_data)
    signature_file = test_file + ".sig"

    # Save signature to separate file (common pattern)
    with open(signature_file, "wb") as f:
        f.write(signature)

    print(f"   Signature saved to: {signature_file}")
    print(f"   Signature (hex): {signature.hex()[:40]}...")

    # Step 3: Verify file integrity
    print("\n▶ Step 3: Verifying file integrity...")

    # Load file and signature
    with open(test_file, "rb") as f:
        loaded_data = f.read()
    with open(signature_file, "rb") as f:
        loaded_sig = f.read()

    # Verify
    verify_key = resolve_did_to_key(admin.did)
    try:
        verify_key.verify(loaded_data, loaded_sig)
        print(f"   ✅ File signature VALID")
        print(f"   File integrity confirmed - signed by {admin.did[:20]}...")
    except BadSignatureError:
        print(f"   ❌ File signature INVALID - file may be corrupted or tampered")

    # Step 4: Demonstrate corruption detection
    print("\n▶ Step 4: Simulating file corruption...")
    corrupted_data = config_data[:10] + b"HACKED" + config_data[16:]

    try:
        verify_key.verify(corrupted_data, loaded_sig)
        print(f"   ✅ Signature VALID - Should not happen!")
    except BadSignatureError:
        print(f"   ❌ CORRUPTION DETECTED - Signature invalid for modified file")
        print(f"   🛡️  File integrity check failed - do not use this file!")

    # Cleanup
    import os
    os.remove(test_file)
    os.remove(signature_file)
    print("\n🧹 Cleanup: Test files removed")

    print("\n💡 File Signing Pattern:")
    print("   1. Create .sig file alongside original file")
    print("   2. Verifier loads both files")
    print("   3. Signature verification proves file authenticity")
    print("   Use case: Software updates, firmware signing, data archives")


def scenario_4_custom_protocol():
    """
    Scenario 4: Custom Message Protocol

    Design a custom binary protocol with signature verification.
    """
    print_section("SCENARIO 4: Custom Binary Protocol")

    print("\n📝 Use Case: Embedded systems, custom protocols, minimal overhead")
    print("   Design your own message format with signature protection\n")

    # Define custom protocol
    print("▶ Custom Protocol Format:")
    print("   [Version:1][Type:1][Timestamp:4][Payload:N][Signature:64]")
    print("   Total overhead: 70 bytes + payload\n")

    def create_message(agent: AgentIdentity, msg_type: int, payload: bytes) -> bytes:
        """Create a signed message in custom format"""
        version = 1
        timestamp = int(time.time())

        # Build message without signature
        header = struct.pack('>BB', version, msg_type)  # Version, Type
        ts_bytes = struct.pack('>I', timestamp)  # Timestamp (4 bytes)
        unsigned_msg = header + ts_bytes + payload

        # Sign the unsigned message
        signature = agent.sign(unsigned_msg)

        # Combine into final message
        return unsigned_msg + signature

    def verify_message(did: str, message: bytes) -> tuple:
        """Verify a message in custom format"""
        if len(message) < 70:
            raise ValueError("Message too short")

        # Split message
        unsigned_msg = message[:-64]
        signature = message[-64:]

        # Parse header
        version, msg_type = struct.unpack('>BB', unsigned_msg[0:2])
        timestamp = struct.unpack('>I', unsigned_msg[2:6])[0]
        payload = unsigned_msg[6:]

        # Verify signature
        verify_key = resolve_did_to_key(did)
        verify_key.verify(unsigned_msg, signature)

        return version, msg_type, timestamp, payload

    # Step 1: Create device and send message
    print("▶ Step 1: IoT device sends telemetry...")
    device = AgentIdentity()
    print(f"   Device DID: {device.did[:30]}...")

    # Message type 1 = telemetry
    payload = struct.pack('>ffff', 24.5, 60.2, 1013.25, 45.0)  # temp, humidity, pressure, battery
    message = create_message(device, msg_type=1, payload=payload)

    print(f"   Payload: temp, humidity, pressure, battery")
    print(f"   Message size: {len(message)} bytes")
    print(f"   Message (hex): {message.hex()[:60]}...")

    # Step 2: Gateway receives and verifies
    print("\n▶ Step 2: Gateway receives and verifies...")
    try:
        version, msg_type, timestamp, recv_payload = verify_message(device.did, message)
        temp, humidity, pressure, battery = struct.unpack('>ffff', recv_payload)

        print(f"   ✅ Message signature VALID")
        print(f"   Protocol version: {version}")
        print(f"   Message type: {msg_type} (telemetry)")
        print(f"   Timestamp: {timestamp}")
        print(f"   Temperature: {temp}°C")
        print(f"   Humidity: {humidity}%")
        print(f"   Pressure: {pressure} hPa")
        print(f"   Battery: {battery}%")
    except BadSignatureError:
        print(f"   ❌ Invalid signature - reject message")
    except Exception as e:
        print(f"   ❌ Parse error: {e}")

    print("\n💡 Custom Protocol Benefits:")
    print("   • Minimal overhead for constrained devices")
    print("   • Full control over message format")
    print("   • Can include metadata (version, type, timestamp)")
    print("   • Still cryptographically secure")


def comparison_summary():
    """Compare JWS vs Raw signatures"""
    print_section("JWS vs RAW SIGNATURES COMPARISON")

    print("\n┌──────────────────────┬─────────────────────┬──────────────────────┐")
    print("│ Feature              │ JWS (Web Standard)  │ Raw Signatures       │")
    print("├──────────────────────┼─────────────────────┼──────────────────────┤")
    print("│ Format               │ JSON + Base64       │ Raw bytes            │")
    print("│ Overhead             │ ~300+ bytes         │ 64 bytes (signature) │")
    print("│ Payload Type         │ JSON objects        │ Any binary data      │")
    print("│ Standard             │ RFC 7515 (JWS)      │ Raw Ed25519          │")
    print("│ Metadata             │ Built-in (headers)  │ Custom (your design) │")
    print("│ Interoperability     │ Excellent (web)     │ Custom protocols     │")
    print("│ Use Case             │ APIs, tokens, web   │ IoT, binary, custom  │")
    print("│ Expiration           │ Built-in (exp)      │ Manual (add to data) │")
    print("│ Ease of Use          │ High (standardized) │ Medium (DIY)         │")
    print("└──────────────────────┴─────────────────────┴──────────────────────┘")

    print("\n💡 When to Use Each Approach:")
    print("\n   Use JWS when:")
    print("   • Building web APIs or REST services")
    print("   • Need standard token format (JWT compatibility)")
    print("   • Want built-in expiration and metadata")
    print("   • Interoperability with existing JWT tools")
    print("   • Payload is JSON-serializable")

    print("\n   Use Raw Signatures when:")
    print("   • Working with binary data (images, sensor readings, files)")
    print("   • Minimal bandwidth critical (IoT, embedded systems)")
    print("   • Custom protocol design needed")
    print("   • Already have metadata layer (timestamps, nonces)")
    print("   • Maximum performance required (no JSON parsing)")

    print("\n🔐 Security Considerations:")
    print("   Both approaches are cryptographically equivalent")
    print("   • Same Ed25519 security (128-bit security level)")
    print("   • Same tamper detection capability")
    print("   • Same DID-based identity binding")
    print("   Difference is in format and overhead, not security")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  didlite: Raw Signature Verification (Non-JWS)")
    print("=" * 70)
    print("\nDemonstrates signing and verifying arbitrary binary data")
    print("without the JWS wrapper for custom protocols and minimal overhead.\n")

    # Run all scenarios
    scenario_1_basic_signing()
    scenario_2_tampering_detection()
    scenario_3_file_signing()
    scenario_4_custom_protocol()
    comparison_summary()

    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70)
    print("\n✅ Raw signature operations demonstrated")
    print("   Choose JWS for web standards, raw for custom protocols\n")
