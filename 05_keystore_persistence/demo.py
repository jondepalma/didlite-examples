"""
Persistent Identity with KeyStore Backends

Demonstrates how agents can maintain their identity across restarts using
different KeyStore backends for different deployment scenarios.

Three scenarios:
1. MemoryKeyStore - Ephemeral identity (testing/temporary agents)
2. EnvKeyStore - Container-friendly identity (Docker/Kubernetes)
3. FileKeyStore - Edge device identity (Raspberry Pi/IoT devices)

⚠️  EDUCATIONAL DEMO DISCLAIMER

This example uses simplified security measures for educational clarity:
- Passwords are hardcoded (use env vars, HSM, or key vaults in production)
- File storage is local (use encrypted volumes in production)
- No audit logging or key rotation policies

Production deployments should use:
- Hardware Security Modules (HSM) for key storage
- Proper secret management (HashiCorp Vault, AWS KMS, Azure Key Vault)
- Audit trails and monitoring
- Regular key rotation policies
- Encrypted storage volumes
"""

import os
import time
from didlite import AgentIdentity, create_jws, verify_jws
from didlite.keystore import MemoryKeyStore, EnvKeyStore, FileKeyStore


def print_section(title):
    """Print a visual section separator"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def scenario_1_memory():
    """
    Scenario 1: MemoryKeyStore - Ephemeral Identity

    Use case: Testing, temporary agents, one-time operations
    Identity is lost when the process exits or keystore is destroyed.
    """
    print_section("SCENARIO 1: MemoryKeyStore (Ephemeral Identity)")

    print("\n📝 Use Case: Testing, temporary operations")
    print("   Identity stored in RAM - lost when process exits\n")

    # First run - create identity
    print("▶ First Run: Creating agent identity...")
    keystore1 = MemoryKeyStore()
    agent1 = AgentIdentity(keystore=keystore1, identifier="temp-agent")
    print(f"   Agent DID: {agent1.did}")

    # Create and sign a message
    message = {"action": "test", "timestamp": time.time()}
    token1 = create_jws(agent1, message)
    print(f"   Signed token: {token1[:50]}...")

    # Simulate application restart (new keystore instance)
    print("\n▶ Simulating Restart: Creating new keystore instance...")
    keystore2 = MemoryKeyStore()
    agent2 = AgentIdentity(keystore=keystore2, identifier="temp-agent")
    print(f"   Agent DID: {agent2.did}")

    # Compare identities
    print("\n📊 Result:")
    print(f"   First run DID:  {agent1.did[:40]}...")
    print(f"   After restart:  {agent2.did[:40]}...")
    print(f"   Identity preserved: {agent1.did == agent2.did}")

    if agent1.did != agent2.did:
        print("\n   ❌ Identity CHANGED - This is expected for MemoryKeyStore")
        print("      Each restart generates a new random identity")

    print("\n✅ MemoryKeyStore: Fast, secure, but ephemeral")
    print("   Perfect for: Testing, temporary agents, one-time operations")


def scenario_2_env():
    """
    Scenario 2: EnvKeyStore - Container-Friendly Identity

    Use case: Docker containers, Kubernetes pods, 12-factor apps
    Identity stored in environment variables (persists across container restarts).
    """
    print_section("SCENARIO 2: EnvKeyStore (Container-Friendly Identity)")

    print("\n📝 Use Case: Docker/Kubernetes deployments, cloud platforms")
    print("   Identity stored in environment variables\n")

    # First run - create identity
    print("▶ First Run: Creating agent identity...")
    keystore1 = EnvKeyStore(prefix="DEMO_AGENT_")
    agent1 = AgentIdentity(keystore=keystore1, identifier="sensor-001")
    print(f"   Agent DID: {agent1.did}")

    # Show that env var was created
    env_var_name = "DEMO_AGENT_SENSOR-001"
    env_value = os.environ.get(env_var_name, "NOT FOUND")
    print(f"   Environment variable: {env_var_name}")
    print(f"   Value (base64): {env_value[:30]}...")

    # Create and sign a message
    message = {"sensor_id": "sensor-001", "temp": 24.5, "timestamp": time.time()}
    token1 = create_jws(agent1, message, expires_in=60)
    print(f"   Signed token: {token1[:50]}...")

    # Simulate application restart (env var persists)
    print("\n▶ Simulating Restart: Creating new keystore instance...")
    print("   (Environment variables persist across restarts)")
    keystore2 = EnvKeyStore(prefix="DEMO_AGENT_")
    agent2 = AgentIdentity(keystore=keystore2, identifier="sensor-001")
    print(f"   Agent DID: {agent2.did}")

    # Verify old token with restored identity
    print("\n▶ Verifying Token: Can we verify the token from before restart?")
    try:
        _, payload = verify_jws(token1)
        print(f"   ✅ Token verified successfully!")
        print(f"   Payload: {payload}")
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")

    # Compare identities
    print("\n📊 Result:")
    print(f"   First run DID:  {agent1.did[:40]}...")
    print(f"   After restart:  {agent2.did[:40]}...")
    print(f"   Identity preserved: {agent1.did == agent2.did}")

    if agent1.did == agent2.did:
        print("\n   ✅ Identity PRESERVED - Environment variable persisted!")
        print("      Same DID after restart = same cryptographic identity")

    # Cleanup
    print("\n🧹 Cleanup: Removing demo environment variable...")
    keystore2.delete_seed("sensor-001")

    print("\n✅ EnvKeyStore: Cloud-native, follows 12-factor app principles")
    print("   Perfect for: Docker, Kubernetes, serverless, cloud deployments")


def scenario_3_file():
    """
    Scenario 3: FileKeyStore - Edge Device Identity

    Use case: IoT devices, edge computing, Raspberry Pi deployments
    Identity stored in encrypted files (persists across reboots).
    """
    print_section("SCENARIO 3: FileKeyStore (Edge Device Identity)")

    print("\n📝 Use Case: IoT devices, edge computing, local deployments")
    print("   Identity stored in encrypted files on disk\n")

    # First run - create identity
    print("▶ First Run: Creating agent identity...")
    keystore1 = FileKeyStore(
        storage_dir="./demo_keys",
        password="demo-password-use-secure-storage-in-production"
    )
    agent1 = AgentIdentity(keystore=keystore1, identifier="iot-device-001")
    print(f"   Agent DID: {agent1.did}")
    print(f"   Key file created: ./demo_keys/iot-device-001.enc")

    # Create and sign a message
    message = {
        "device_id": "iot-device-001",
        "sensor_reading": 42,
        "timestamp": time.time()
    }
    token1 = create_jws(agent1, message, expires_in=60)
    print(f"   Signed token: {token1[:50]}...")

    # Simulate device reboot (file persists on disk)
    print("\n▶ Simulating Reboot: Creating new keystore instance...")
    print("   (Encrypted file persists on disk)")
    keystore2 = FileKeyStore(
        storage_dir="./demo_keys",
        password="demo-password-use-secure-storage-in-production"
    )
    agent2 = AgentIdentity(keystore=keystore2, identifier="iot-device-001")
    print(f"   Agent DID: {agent2.did}")
    print(f"   Key file loaded from: ./demo_keys/iot-device-001.enc")

    # Verify old token with restored identity
    print("\n▶ Verifying Token: Can we verify the token from before reboot?")
    try:
        _, payload = verify_jws(token1)
        print(f"   ✅ Token verified successfully!")
        print(f"   Payload: {payload}")
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")

    # Compare identities
    print("\n📊 Result:")
    print(f"   First run DID:  {agent1.did[:40]}...")
    print(f"   After reboot:   {agent2.did[:40]}...")
    print(f"   Identity preserved: {agent1.did == agent2.did}")

    if agent1.did == agent2.did:
        print("\n   ✅ Identity PRESERVED - Encrypted file persisted!")
        print("      Same DID after reboot = device maintains reputation")

    # Show file encryption details
    print("\n🔐 Security Details:")
    print(f"   Encryption: Fernet (AES-128-CBC with HMAC)")
    print(f"   Key derivation: PBKDF2-SHA256 with 480,000 iterations")
    print(f"   File permissions: 0600 (owner read/write only)")

    # Cleanup
    print("\n🧹 Cleanup: Removing demo files...")
    keystore2.delete_seed("iot-device-001")
    import shutil
    if os.path.exists("./demo_keys"):
        shutil.rmtree("./demo_keys")
    print("   Removed: ./demo_keys/")

    print("\n✅ FileKeyStore: Encrypted local storage for edge devices")
    print("   Perfect for: IoT devices, Raspberry Pi, edge AI, offline systems")


def comparison_summary():
    """Print a comparison summary of all three KeyStore backends"""
    print_section("KEYSTORE COMPARISON SUMMARY")

    print("\n┌─────────────────┬──────────────────┬──────────────────┬──────────────────┐")
    print("│ Feature         │ MemoryKeyStore   │ EnvKeyStore      │ FileKeyStore     │")
    print("├─────────────────┼──────────────────┼──────────────────┼──────────────────┤")
    print("│ Persistence     │ No (RAM only)    │ Yes (env vars)   │ Yes (disk)       │")
    print("│ Encryption      │ N/A              │ Base64 only      │ Fernet (AES)     │")
    print("│ Speed           │ Fastest          │ Fast             │ Medium           │")
    print("│ Use Case        │ Testing          │ Containers       │ Edge devices     │")
    print("│ Best For        │ Temp agents      │ Cloud/K8s        │ IoT/Raspberry Pi │")
    print("└─────────────────┴──────────────────┴──────────────────┴──────────────────┘")

    print("\n💡 Choosing the Right KeyStore:")
    print("   • MemoryKeyStore: Testing, demos, temporary operations")
    print("   • EnvKeyStore: Docker, Kubernetes, AWS Lambda, cloud platforms")
    print("   • FileKeyStore: Raspberry Pi, IoT sensors, edge AI, offline systems")

    print("\n⚠️  Production Reminder:")
    print("   • Never hardcode passwords (use env vars or secret managers)")
    print("   • Use HSM/TPM for high-security deployments")
    print("   • Implement key rotation policies")
    print("   • Add audit logging for all key operations")
    print("   • Use encrypted volumes for FileKeyStore")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  didlite: Persistent Identity with KeyStore Backends")
    print("=" * 70)
    print("\nThis demo shows how agents maintain identity across restarts")
    print("using different storage backends for different deployment scenarios.\n")

    # Run all three scenarios
    scenario_1_memory()
    scenario_2_env()
    scenario_3_file()
    comparison_summary()

    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70)
    print("\n✅ All three KeyStore backends demonstrated")
    print("   Choose the right backend for your deployment scenario\n")
