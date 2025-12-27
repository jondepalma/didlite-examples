#!/usr/bin/env python3
"""
Interactive demo script for Secure Agent Communication.

This script demonstrates the full workflow:
1. Bob sends a message to Alice
2. Alice verifies the message
3. Chris attempts various attacks

Usage:
    python demo.py           # Normal mode
    python demo.py --verbose # Verbose mode with detailed cryptographic information
"""

import requests
import json
import time
import sys
import base64
from typing import Dict

BASE_URL = "http://localhost:8000"
VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv


def print_section(title: str):
    """Print a section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_json(data: Dict):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2))


def decode_token(token: str) -> tuple:
    """Decode a JWS token to show header and payload."""
    parts = token.split('.')
    if len(parts) != 3:
        return None, None, None

    header_segment, payload_segment, signature_segment = parts

    # Decode header
    padding = (4 - len(header_segment) % 4) % 4
    header_data = base64.urlsafe_b64decode(header_segment + '=' * padding)
    header = json.loads(header_data)

    # Decode payload
    padding = (4 - len(payload_segment) % 4) % 4
    payload_data = base64.urlsafe_b64decode(payload_segment + '=' * padding)
    payload = json.loads(payload_data)

    return header, payload, signature_segment


def print_token_details(token: str, label: str = "Token"):
    """Print detailed token information in verbose mode."""
    if not VERBOSE:
        return

    print(f"\n{'─' * 70}")
    print(f"  📋 {label} Details")
    print(f"{'─' * 70}")

    header, payload, signature = decode_token(token)

    if header:
        print("\n  HEADER:")
        print(f"    Algorithm: {header.get('alg', 'N/A')}")
        print(f"    Type: {header.get('typ', 'N/A')}")
        print(f"    Key ID (DID): {header.get('kid', 'N/A')[:60]}...")

    if payload:
        print("\n  PAYLOAD:")
        for key, value in payload.items():
            if isinstance(value, str) and len(value) > 60:
                print(f"    {key}: {value[:60]}...")
            else:
                print(f"    {key}: {value}")

    print(f"\n  SIGNATURE (truncated): {signature[:60]}...")
    print(f"{'─' * 70}\n")


def check_server():
    """Check if the server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


def main():
    print("\n" + "🔐 " * 20)
    if VERBOSE:
        print("  SECURE AGENT COMMUNICATION DEMO (VERBOSE MODE)")
    else:
        print("  SECURE AGENT COMMUNICATION DEMO")
    print("🔐 " * 20)

    if VERBOSE:
        print("\n💡 Verbose mode enabled - showing detailed cryptographic operations")
        print("   Run without --verbose flag for simpler output")

    # Check server
    if not check_server():
        print("\n❌ Error: Server is not running!")
        print("Please start the server with: python main.py")
        return

    # 1. List agents
    print_section("1. Agent Identities")
    print("Listing all agents and their DIDs...\n")

    response = requests.get(f"{BASE_URL}/agents")
    agents = response.json()

    for agent in agents:
        role = "Good Actor" if agent["name"] in ["bob", "alice"] else "Bad Actor"
        print(f"  {agent['name'].upper()} ({role})")
        print(f"  DID: {agent['did']}\n")

    # 2. Bob sends message to Alice
    print_section("2. Bob Sends Message to Alice")
    print("Bob creates and signs a message...\n")

    message_data = {
        "sender": "bob",
        "recipient": "alice",
        "content": "Hello Alice! This is a secure message from Bob. Let's discuss the project."
    }

    response = requests.post(f"{BASE_URL}/agents/bob/send", json=message_data)
    signed_message = response.json()

    print("✅ Message signed successfully!")
    if not VERBOSE:
        print(f"  Token (truncated): {signed_message['token'][:80]}...")
        print(f"  Sender DID: {signed_message['sender_did']}\n")
    else:
        print(f"  Sender DID: {signed_message['sender_did']}")

    bob_token = signed_message['token']
    print_token_details(bob_token, "Bob's Signed Message")

    # 3. Alice verifies Bob's message
    print_section("3. Alice Verifies Bob's Message")
    print("Alice receives and verifies the signature...\n")

    verify_data = {"token": bob_token}
    response = requests.post(f"{BASE_URL}/agents/alice/verify", json=verify_data)
    verify_result = response.json()

    if verify_result['valid']:
        print("✅ Signature VALID!")
        print("\nVerified Payload:")
        print(f"  From: {verify_result['payload']['sender']}")
        print(f"  To: {verify_result['payload']['recipient']}")
        print(f"  Content: {verify_result['payload']['content']}")
        print(f"  Timestamp: {verify_result['payload']['timestamp']}")
        print(f"  Expires: {verify_result['payload']['exp']}")
        print(f"  Sender DID: {verify_result['sender_did']}\n")
    else:
        print(f"❌ Signature INVALID: {verify_result['error']}\n")

    # 4. Attack Scenario 1: Replay Attack
    print_section("4. Attack Scenario 1: Replay Attack")
    print("Chris tries to replay Bob's old message...\n")
    print("Simulating real-world delay (tokens expire in 5 seconds)...")

    # Countdown timer to show token expiration
    for i in range(10, 0, -1):
        print(f"  Waiting {i} seconds before replay attack...", end='\r')
        time.sleep(1)
    print(" " * 50, end='\r')  # Clear the countdown line
    print("Executing replay attack now!\n")

    attack_data = {"attack_type": "replay", "target_agent": "alice"}
    response = requests.post(f"{BASE_URL}/agents/chris/attack", json=attack_data)
    attack_result = response.json()

    print(f"Attack Type: {attack_result['attack_type']}")
    print(f"Description: {attack_result['description']}")
    print(f"Success: {attack_result['success']}")
    print(f"\n{attack_result['note']}\n")

    if attack_result['success']:
        print("⚠️  Replay attack SUCCEEDED (token not expired yet)")
    else:
        print("✅ Replay attack FAILED (token expired)")

    # 4b. Nonce Protection Demonstration
    print_section("4b. Nonce Protection: Instant Replay Attack")
    print("Demonstrating application-layer replay protection using nonces...\n")

    print("⚠️  EDUCATIONAL DEMO: Using simple file-based nonce tracking")
    print("   Production should use Redis/database for distributed systems\n")

    # First, send a fresh message from Bob to Alice (no nonce)
    print("Step 1: Bob sends a new message (WITHOUT nonce protection)...")
    message_data = {
        "sender": "bob",
        "recipient": "alice",
        "content": "Transfer $1000 to account 12345"
    }
    response = requests.post(f"{BASE_URL}/agents/bob/send", json=message_data)
    signed_message = response.json()
    transfer_token = signed_message['token']
    print("  ✅ Message sent\n")

    # Try instant replay (should succeed - no nonce)
    print("Step 2: Chris intercepts and IMMEDIATELY replays the message...")
    verify_data = {"token": transfer_token}
    response = requests.post(f"{BASE_URL}/agents/alice/verify", json=verify_data)
    result1 = response.json()
    print(f"  First verification: {'✅ VALID' if result1['valid'] else '❌ INVALID'}")

    response = requests.post(f"{BASE_URL}/agents/alice/verify", json=verify_data)
    result2 = response.json()
    print(f"  Second verification (replay): {'⚠️  VALID (replay succeeded!)' if result2['valid'] else '✅ INVALID (replay blocked)'}")

    if result2['valid']:
        print("\n  💸 DANGER: Without nonces, Chris can replay instantly!")
        print("     Result: $1000 transferred twice = $2000 stolen!\n")

    # Now enable nonce protection
    print("\nStep 3: Enabling nonce-based replay protection...")
    response = requests.post(f"{BASE_URL}/nonce/enable")
    nonce_status = response.json()
    print(f"  ✅ {nonce_status['message']}")
    print(f"  {nonce_status['note']}\n")

    # Send new message with nonce
    print("Step 4: Bob sends another message (WITH nonce protection)...")
    message_data = {
        "sender": "bob",
        "recipient": "alice",
        "content": "Transfer $1000 to account 67890"
    }
    response = requests.post(f"{BASE_URL}/agents/bob/send", json=message_data)
    signed_message = response.json()
    nonce_token = signed_message['token']
    print("  ✅ Message sent with nonce\n")

    if VERBOSE:
        header, payload, sig = decode_token(nonce_token)
        print(f"  Nonce in payload: {payload.get('nonce', 'N/A')[:40]}...\n")

    # Try instant replay with nonce (should fail)
    print("Step 5: Chris tries to replay THIS message instantly...")
    verify_data = {"token": nonce_token}
    response = requests.post(f"{BASE_URL}/agents/alice/verify", json=verify_data)
    result3 = response.json()
    print(f"  First verification: {'✅ VALID' if result3['valid'] else '❌ INVALID'}")

    response = requests.post(f"{BASE_URL}/agents/alice/verify", json=verify_data)
    result4 = response.json()
    print(f"  Second verification (replay): {'⚠️  VALID (replay succeeded!)' if result4['valid'] else '✅ BLOCKED! ' + result4.get('error', '')}")

    if not result4['valid']:
        print("\n  🛡️  SUCCESS: Nonce protection blocked the instant replay!")
        print("     The same token cannot be used twice, even instantly.\n")

    # Show nonce file contents
    if VERBOSE:
        print("\nStep 6: Examining the nonce tracking file...")
        try:
            with open("nonces.json", "r") as f:
                nonces_content = json.load(f)
                print(f"\n  Contents of nonces.json:")
                print(f"  {json.dumps(nonces_content, indent=4)}")
                print(f"\n  📊 Total nonces stored: {len(nonces_content)}")
                print(f"  💡 Each nonce can only be used once!")
                print(f"  💡 Nonces expire after 5 minutes to free memory\n")
        except Exception as e:
            print(f"\n  Could not read nonce file: {e}\n")

    # Get nonce stats
    response = requests.get(f"{BASE_URL}/nonce/stats")
    stats = response.json()
    print(f"\nNonce Protection Stats:")
    print(f"  Status: {'ENABLED ✅' if stats['nonce_enabled'] else 'DISABLED'}")
    print(f"  Active nonces: {stats['active_nonces']}")
    print(f"  Storage: {stats['file_path']}")

    # Disable nonce for remaining demos
    print("\nStep 7: Disabling nonce protection for remaining demos...")
    response = requests.post(f"{BASE_URL}/nonce/disable")
    print("  ✅ Nonce protection disabled\n")

    # 5. Attack Scenario 2: Forgery Attack
    print_section("5. Attack Scenario 2: Forgery Attack")
    print("Chris tries to forge a message claiming to be Bob...\n")

    time.sleep(1)

    attack_data = {"attack_type": "forge"}
    response = requests.post(f"{BASE_URL}/agents/chris/attack", json=attack_data)
    attack_result = response.json()

    print(f"Attack Type: {attack_result['attack_type']}")
    print(f"Description: {attack_result['description']}")
    print(f"\nDID Comparison:")
    print(f"  Chris's DID:  {attack_result['chris_did']}")
    print(f"  Bob's DID:    {attack_result['bob_did']}")
    print(f"  DIDs Match:   {attack_result['did_matches']}")
    print(f"\nAttack Success: {attack_result['success']}")
    print(f"\n{attack_result['note']}\n")

    if VERBOSE:
        print_token_details(attack_result['forged_token'], "Chris's Forged Token (claiming to be Bob)")
        print("\n💡 Notice: The token HEADER contains Chris's DID, not Bob's!")
        print("   Even though the payload says 'sender: bob', the cryptographic")
        print("   signature proves it was signed by Chris's private key.\n")

    # 5b. Attack Scenario: Private Key Required
    print_section("5b. Attack Scenario 2b: No Private Key = No Signature")
    print("Chris tries to create a signature using only Bob's public DID...\n")

    time.sleep(1)

    attack_data = {"attack_type": "no_private_key"}
    response = requests.post(f"{BASE_URL}/agents/chris/attack", json=attack_data)
    attack_result = response.json()

    print(f"Attack Type: {attack_result['attack_type']}")
    print(f"Description: {attack_result['description']}")
    print(f"\nWhat Chris knows:")
    print(f"  Bob's DID (public): {attack_result['bob_did'][:60]}...")
    print(f"  Bob's public key: Available in the DID")
    print(f"\nWhat Chris doesn't have:")
    print(f"  Bob's private key: 🔒 SECRET (required for signing)")
    print(f"\nCan Chris create a valid signature? {attack_result['can_sign']}")
    print(f"\nAttack Success: {attack_result['success']}")
    print(f"\n{attack_result['note']}\n")

    if VERBOSE:
        print("─" * 70)
        print("  🔑 Public Key Cryptography Explained")
        print("─" * 70)
        print("\n  PUBLIC KEY (in DID):")
        print("    - Derived from the private key")
        print("    - Freely shared with everyone")
        print("    - Used to VERIFY signatures")
        print("    - Cannot be used to CREATE signatures")
        print("\n  PRIVATE KEY:")
        print("    - Kept secret by the owner")
        print("    - Used to CREATE signatures")
        print("    - Cannot be derived from the public key")
        print("    - Required for signing messages")
        print("\n  💡 This is why Chris can't forge Bob's signature even")
        print("     though he knows Bob's public DID/key!")
        print("─" * 70 + "\n")

    # 6. Attack Scenario 3: Intercept Attack
    print_section("6. Attack Scenario 3: Man-in-the-Middle")
    print("Chris intercepts and tries to modify Bob's message...\n")

    time.sleep(1)

    attack_data = {"attack_type": "intercept"}
    response = requests.post(f"{BASE_URL}/agents/chris/attack", json=attack_data)
    attack_result = response.json()

    print(f"Attack Type: {attack_result['attack_type']}")
    print(f"Description: {attack_result['description']}")

    if VERBOSE:
        print("\n" + "─" * 70)
        print("  🔍 Detailed Comparison")
        print("─" * 70)

        # Show original token
        original_token = attack_result['original_token']
        tampered_token = attack_result['tampered_token']

        print("\n  ORIGINAL MESSAGE (from Bob):")
        orig_header, orig_payload, orig_sig = decode_token(original_token)
        print(f"    Content: {orig_payload.get('content')}")
        print(f"    Signature: {orig_sig[:60]}...")

        print("\n  TAMPERED MESSAGE (modified by Chris):")
        tamp_header, tamp_payload, tamp_sig = decode_token(tampered_token)
        print(f"    Content: {tamp_payload.get('content')}")
        print(f"    Signature: {tamp_sig[:60]}... (SAME as original)")

        print("\n  ⚠️  Chris changed the payload but kept Bob's original signature!")
        print("      The signature only validates the ORIGINAL payload.")
        print("      Any modification breaks the cryptographic binding.")
        print("─" * 70)

    print(f"\nVerification Result: {attack_result['verification_result']['valid']}")

    if not attack_result['verification_result']['valid']:
        print(f"Error: {attack_result['verification_result']['error']}")

    print(f"\nAttack Success: {attack_result['success']}")
    print(f"\n{attack_result['note']}\n")

    # 7. Alice sends message to Bob
    print_section("7. Alice Responds to Bob")
    print("Alice sends a signed response back to Bob...\n")

    message_data = {
        "sender": "alice",
        "recipient": "bob",
        "content": "Hi Bob! I received your message. The cryptographic signature verified successfully!"
    }

    response = requests.post(f"{BASE_URL}/agents/alice/send", json=message_data)
    signed_message = response.json()

    print("✅ Alice's message signed successfully!")
    print(f"  Token (truncated): {signed_message['token'][:80]}...\n")

    alice_token = signed_message['token']

    # 8. Attack Scenario 4: Token Theft
    print_section("8. Attack Scenario 4: Token Theft")
    print("Chris steals Alice's token and tries to reuse it...\n")

    time.sleep(1)

    attack_data = {"attack_type": "token_theft", "stolen_token": alice_token}
    response = requests.post(f"{BASE_URL}/agents/chris/attack", json=attack_data)
    attack_result = response.json()

    print(f"Attack Type: {attack_result['attack_type']}")
    print(f"Description: {attack_result['description']}")
    print(f"\nToken Valid: {attack_result['success']}")
    print(f"Actual Signer: {attack_result['alice_did']}")
    print(f"\n{attack_result['note']}\n")

    # 9. Message History
    print_section("9. Message History")
    print("Viewing message history for all agents...\n")

    for agent_name in ["bob", "alice"]:
        response = requests.get(f"{BASE_URL}/agents/{agent_name}/messages")
        history = response.json()

        print(f"{agent_name.upper()}:")
        print(f"  Sent: {len(history['sent'])} messages")
        print(f"  Received: {len(history['received'])} messages\n")

    # Summary
    print_section("Summary")
    print("\n✅ didlite provides strong cryptographic protections:")
    print("   - Authentication: DIDs prove sender identity")
    print("   - Integrity: Signatures detect tampering")
    print("   - Non-repudiation: Senders can't deny signing")
    print("   - Asymmetric crypto: Private key required for signing\n")

    print("⚠️  Additional protections needed in production:")
    print("   - Nonce tracking to prevent replay attacks")
    print("   - Audience claims for context-specific tokens")
    print("   - Rate limiting and DoS protection")
    print("   - Secure key storage (HSM, encrypted files)\n")

    print("🎓 Educational Value:")
    print("   This demo shows both the strengths and limitations of")
    print("   cryptographic signatures for agent communication.")
    if not VERBOSE:
        print("\n💡 Tip: Run with --verbose flag to see detailed cryptographic operations!")
    print()

    print("="*70)
    print("  Demo Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Demo interrupted by user\n")
    except Exception as e:
        print(f"\n\n❌ Error: {e}\n")
