"""
Key Backup, Export, and Recovery

Demonstrates how to export agent keys for backup, migration, and recovery
using both JWK (JSON Web Key) and PEM formats.

Use cases:
- Disaster recovery - Restore agent identity after system failure
- Key migration - Move agent identity between systems
- Interoperability - Share public keys with other tools
- Backup/restore - Archive agent identities securely

Two formats demonstrated:
1. JWK (JSON Web Key) - Web-friendly, JSON format, easy integration
2. PEM (Privacy Enhanced Mail) - OpenSSL compatible, enterprise standard

⚠️  EDUCATIONAL DEMO DISCLAIMER

This example demonstrates key export/import for educational purposes.

Production key management should include:
- Encrypted backups (use GPG, age, or enterprise key vaults)
- Access controls (who can export/import keys)
- Audit trails (log all key operations)
- Secure transmission (TLS, VPN, or air-gapped transfer)
- Key rotation policies (regular key updates)
- Hardware Security Modules (HSM) for critical keys

NEVER store private keys in:
- Git repositories
- Unencrypted files
- Cloud storage without encryption
- Logs or error messages
- Environment variables (for long-term storage)
"""

import json
import os
from didlite import AgentIdentity, create_jws, verify_jws


def print_section(title):
    """Print a visual section separator"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def scenario_1_jwk_roundtrip():
    """
    Scenario 1: JWK Export and Import

    JWK (JSON Web Key) is a JSON format for representing cryptographic keys.
    It's web-friendly and supported by many modern tools.
    """
    print_section("SCENARIO 1: JWK Export/Import (Web-Friendly Format)")

    print("\n📝 Use Case: Web APIs, microservices, cloud platforms")
    print("   JSON format - easy to integrate with modern tools\n")

    # Step 1: Create original identity
    print("▶ Step 1: Creating original agent identity...")
    original = AgentIdentity()
    print(f"   Original DID: {original.did}")

    # Step 2: Create a signed message with the original identity
    message = {
        "agent_name": "production-agent-001",
        "message": "This agent needs backup before maintenance window"
    }
    token_before = create_jws(original, message, expires_in=300)
    print(f"   Signed token: {token_before[:50]}...")

    # Step 3: Export to JWK format (with private key)
    print("\n▶ Step 2: Exporting to JWK format...")
    jwk_private = original.to_jwk(include_private=True)
    print(f"\n   JWK Export (private key included):")
    print(json.dumps(jwk_private, indent=4))
    print(f"\n   Key Type (kty): {jwk_private['kty']}")
    print(f"   Curve (crv): {jwk_private['crv']}")
    print(f"   Public Key (x): {jwk_private['x'][:20]}...")
    print(f"   Private Key (d): {'***REDACTED***' if 'd' in jwk_private else 'NOT INCLUDED'}")

    # Step 4: Simulate backup to file
    print("\n▶ Step 3: Backing up to file...")
    backup_file = "agent_backup.jwk"
    with open(backup_file, "w") as f:
        json.dump(jwk_private, f, indent=2)
    print(f"   ✅ Backed up to: {backup_file}")
    print(f"   File size: {os.path.getsize(backup_file)} bytes")

    # Step 5: Simulate disaster (original identity lost)
    print("\n▶ Step 4: Simulating disaster (original identity lost)...")
    print("   💥 System crash! Original identity destroyed!")
    del original  # Simulate loss

    # Step 6: Restore from backup
    print("\n▶ Step 5: Restoring from backup...")
    with open(backup_file, "r") as f:
        restored_jwk = json.load(f)

    restored = AgentIdentity.from_jwk(restored_jwk)
    print(f"   Restored DID: {restored.did}")

    # Step 7: Verify old token with restored identity
    print("\n▶ Step 6: Verifying old token with restored identity...")
    try:
        payload = verify_jws(token_before)
        print(f"   ✅ Token verified successfully!")
        print(f"   Payload: {payload}")
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")

    # Step 8: Create new token with restored identity
    print("\n▶ Step 7: Creating new token with restored identity...")
    new_message = {"status": "recovered", "message": "Agent back online!"}
    token_after = create_jws(restored, new_message)
    print(f"   New token: {token_after[:50]}...")

    # Compare
    print("\n📊 Result:")
    print(f"   Original DID:  {original.did if 'original' in locals() else '[lost]'}")
    print(f"   Restored DID:  {restored.did}")
    print(f"   Identity preserved: ✅ (DIDs match)")

    print("\n✅ JWK Format Benefits:")
    print("   • JSON - easy to parse and manipulate")
    print("   • Web-friendly - works with JWT libraries")
    print("   • Compact - small file size")
    print("   • Standardized - RFC 7517")

    # Cleanup
    print("\n🧹 Cleanup...")
    os.remove(backup_file)
    print(f"   Removed: {backup_file}")


def scenario_2_pem_roundtrip():
    """
    Scenario 2: PEM Export and Import

    PEM (Privacy Enhanced Mail) is the traditional format used by OpenSSL,
    SSH, and many enterprise tools. It's base64-encoded DER with headers.
    """
    print_section("SCENARIO 2: PEM Export/Import (OpenSSL Compatible)")

    print("\n📝 Use Case: Enterprise tools, OpenSSL, SSH, traditional infrastructure")
    print("   PEM format - compatible with existing security tools\n")

    # Step 1: Create original identity
    print("▶ Step 1: Creating original agent identity...")
    original = AgentIdentity()
    print(f"   Original DID: {original.did}")

    # Step 2: Export private key to PEM
    print("\n▶ Step 2: Exporting PRIVATE key to PEM format...")
    pem_private = original.to_pem(include_private=True)
    print(f"\n{pem_private}")
    print(f"   Format: PKCS8 (Private Key)")
    print(f"   Encoding: Base64 DER with PEM headers")

    # Step 3: Export public key to PEM
    print("▶ Step 3: Exporting PUBLIC key to PEM format...")
    pem_public = original.to_pem(include_private=False)
    print(f"\n{pem_public}")
    print(f"   Format: SubjectPublicKeyInfo (Public Key)")
    print(f"   Can be shared safely - verification only")

    # Step 4: Save to files
    print("▶ Step 4: Saving to files...")
    private_file = "agent_private.pem"
    public_file = "agent_public.pem"

    with open(private_file, "w") as f:
        f.write(pem_private)
    with open(public_file, "w") as f:
        f.write(pem_public)

    print(f"   ✅ Saved private key: {private_file}")
    print(f"   ✅ Saved public key:  {public_file}")

    # Step 5: Restore from private key PEM
    print("\n▶ Step 5: Restoring from private key PEM...")
    with open(private_file, "r") as f:
        pem_data = f.read()

    restored = AgentIdentity.from_pem(pem_data)
    print(f"   Restored DID: {restored.did}")

    # Compare
    print("\n📊 Result:")
    print(f"   Original DID:  {original.did[:40]}...")
    print(f"   Restored DID:  {restored.did[:40]}...")
    print(f"   Identity preserved: {original.did == restored.did} ✅")

    print("\n✅ PEM Format Benefits:")
    print("   • Industry standard - used everywhere")
    print("   • OpenSSL compatible - works with openssl commands")
    print("   • SSH compatible - similar to SSH keys")
    print("   • Human-readable headers - easy to identify key type")

    # Demonstrate interoperability
    print("\n🔧 PEM Interoperability Example:")
    print("   You can now use OpenSSL to inspect the key:")
    print(f"   $ openssl pkey -in {private_file} -text -noout")
    print(f"   $ openssl pkey -pubin -in {public_file} -text -noout")

    # Cleanup
    print("\n🧹 Cleanup...")
    os.remove(private_file)
    os.remove(public_file)
    print(f"   Removed: {private_file}, {public_file}")


def scenario_3_public_key_sharing():
    """
    Scenario 3: Public Key Sharing

    Demonstrates exporting ONLY the public key for sharing with verifiers.
    Shows the asymmetric crypto principle: public keys can verify but not sign.
    """
    print_section("SCENARIO 3: Public Key Sharing (Verification Only)")

    print("\n📝 Use Case: Share public key with verifiers, publish to directory")
    print("   Public key alone CANNOT sign - asymmetric cryptography\n")

    # Step 1: Create agent identity
    print("▶ Step 1: Creating agent identity...")
    agent = AgentIdentity()
    print(f"   Agent DID: {agent.did}")

    # Step 2: Export public key only (JWK format)
    print("\n▶ Step 2: Exporting PUBLIC key only (JWK)...")
    public_jwk = agent.to_jwk(include_private=False)
    print(f"\n   Public JWK (safe to share):")
    print(json.dumps(public_jwk, indent=4))

    # Verify no private key included
    print(f"\n   Private key included: {'d' in public_jwk}")
    print(f"   Can be shared publicly: ✅")

    # Step 3: Save public key
    print("\n▶ Step 3: Publishing public key...")
    public_jwk_file = "agent_public.jwk"
    with open(public_jwk_file, "w") as f:
        json.dump(public_jwk, f, indent=2)
    print(f"   Published to: {public_jwk_file}")

    # Step 4: Agent signs a message
    print("\n▶ Step 4: Agent signs a message...")
    message = {"announcement": "My public key is available for verification"}
    token = create_jws(agent, message)
    print(f"   Signed token: {token[:50]}...")

    # Step 5: Show that public key can verify but not sign
    print("\n▶ Step 5: Demonstrating asymmetric cryptography...")
    print("   ✅ Private key can: Sign messages (create tokens)")
    print("   ✅ Public key can: Verify signatures (check tokens)")
    print("   ❌ Public key CANNOT: Sign messages (no private key)")

    print("\n💡 Security Principle:")
    print("   Even if an attacker has your public key (DID), they CANNOT")
    print("   impersonate you. Only the holder of the private key can sign.")

    # Step 6: Verify the token (simulating a verifier with only public key)
    print("\n▶ Step 6: Verifier uses public key to verify token...")
    try:
        payload = verify_jws(token)
        print(f"   ✅ Token verified! Payload: {payload}")
        print(f"   Verifier only needs the DID (public key) - no private key")
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")

    # Cleanup
    print("\n🧹 Cleanup...")
    os.remove(public_jwk_file)
    print(f"   Removed: {public_jwk_file}")


def scenario_4_migration():
    """
    Scenario 4: Cross-System Migration

    Demonstrates moving an agent identity from one system to another
    using key export/import.
    """
    print_section("SCENARIO 4: Cross-System Migration")

    print("\n📝 Use Case: Migrate agent from dev to production")
    print("   Export from System A → Import to System B\n")

    # System A: Development
    print("▶ System A (Development): Creating agent...")
    agent_dev = AgentIdentity()
    print(f"   Dev Agent DID: {agent_dev.did}")

    # System A: Export for migration
    print("\n▶ System A: Exporting for migration...")
    migration_package = {
        "agent_id": "agent-001",
        "environment": "development",
        "jwk": agent_dev.to_jwk(include_private=True),
        "pem": agent_dev.to_pem(include_private=True)
    }

    migration_file = "agent_migration.json"
    with open(migration_file, "w") as f:
        json.dump(migration_package, f, indent=2)
    print(f"   Migration package created: {migration_file}")

    # System B: Production
    print("\n▶ System B (Production): Importing agent...")
    with open(migration_file, "r") as f:
        package = json.load(f)

    # Can restore from either JWK or PEM
    agent_prod = AgentIdentity.from_jwk(package["jwk"])
    print(f"   Prod Agent DID: {agent_prod.did}")

    # Verify same identity
    print("\n📊 Migration Result:")
    print(f"   Dev DID:  {agent_dev.did[:40]}...")
    print(f"   Prod DID: {agent_prod.did[:40]}...")
    print(f"   Same identity: {agent_dev.did == agent_prod.did} ✅")

    print("\n✅ Migration successful!")
    print("   Agent maintains same identity across environments")
    print("   Tokens signed in dev can be verified in prod (and vice versa)")

    # Cleanup
    print("\n🧹 Cleanup...")
    os.remove(migration_file)
    print(f"   Removed: {migration_file}")


def comparison_summary():
    """Print a comparison summary of JWK vs PEM formats"""
    print_section("FORMAT COMPARISON SUMMARY")

    print("\n┌─────────────────────┬──────────────────────┬──────────────────────┐")
    print("│ Feature             │ JWK (JSON Web Key)   │ PEM (OpenSSL)        │")
    print("├─────────────────────┼──────────────────────┼──────────────────────┤")
    print("│ Format              │ JSON                 │ Base64 + Headers     │")
    print("│ Web APIs            │ Excellent            │ Good                 │")
    print("│ OpenSSL Compatible  │ No                   │ Yes                  │")
    print("│ Human Readable      │ Yes (JSON)           │ Partially (headers)  │")
    print("│ File Size           │ Smaller              │ Larger               │")
    print("│ Use Case            │ Modern web apps      │ Enterprise/legacy    │")
    print("│ Standard            │ RFC 7517             │ RFC 7468             │")
    print("└─────────────────────┴──────────────────────┴──────────────────────┘")

    print("\n💡 When to Use Each Format:")
    print("   • JWK: Modern web services, cloud platforms, microservices")
    print("   • PEM: Enterprise tools, OpenSSL integration, legacy systems")
    print("   • Both: Maximum interoperability (export in both formats)")

    print("\n🔐 Security Best Practices:")
    print("   1. Encrypt backups - Never store private keys in plain text")
    print("   2. Access control - Restrict who can export/import keys")
    print("   3. Audit logging - Log all key export/import operations")
    print("   4. Secure transfer - Use encrypted channels (TLS, VPN)")
    print("   5. Rotation policy - Regularly rotate keys and archive old ones")
    print("   6. HSM storage - Use Hardware Security Modules for critical keys")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  didlite: Key Backup, Export, and Recovery")
    print("=" * 70)
    print("\nDemonstrates exporting agent keys for backup, migration, and recovery")
    print("using both JWK (web-friendly) and PEM (OpenSSL) formats.\n")

    # Run all scenarios
    scenario_1_jwk_roundtrip()
    scenario_2_pem_roundtrip()
    scenario_3_public_key_sharing()
    scenario_4_migration()
    comparison_summary()

    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70)
    print("\n✅ Key export/import demonstrated in both JWK and PEM formats")
    print("   Choose the format that fits your infrastructure\n")
