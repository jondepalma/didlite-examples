"""
Demo script for Example 8: Fast Routing with extract_signer_did()

Demonstrates:
1. Rate limiting by agent tier (free/standard/premium)
2. Request routing based on DID
3. Audit logging of all requests
4. Performance benefits of extract_signer_did()
"""

import requests
import didlite
import time
import json
from typing import List

# Start server first:
# python 08_fast_routing/server.py

BASE_URL = "http://127.0.0.1:8000"

def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def create_agent_and_token(content: str) -> tuple[didlite.AgentIdentity, str]:
    """Create agent and sign a token"""
    agent = didlite.AgentIdentity()
    payload = {"content": content}
    token = didlite.create_jws(agent, payload)
    return agent, token

def publish_article(token: str, title: str, content: str) -> dict:
    """Publish article with signed token"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"title": title, "content": content}

    try:
        response = requests.post(f"{BASE_URL}/publish", headers=headers, json=data)
        return {
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "data": response.json() if response.status_code == 200 else response.text
        }
    except Exception as e:
        return {"status_code": 0, "success": False, "error": str(e)}

def set_tier(did: str, tier: str):
    """Set agent tier (admin endpoint)"""
    response = requests.post(f"{BASE_URL}/admin/set-tier/{did}/{tier}")
    return response.json()

def get_rate_limits():
    """Get current rate limit status"""
    response = requests.get(f"{BASE_URL}/admin/rate-limits")
    return response.json()

def get_audit_log(limit: int = 20):
    """Get audit log entries"""
    response = requests.get(f"{BASE_URL}/admin/audit-log?limit={limit}")
    return response.json()

def reset_demo():
    """Reset demo state"""
    response = requests.delete(f"{BASE_URL}/admin/reset")
    return response.json()

def main():
    print("\n" + "=" * 70)
    print("  Example 8: Fast Routing with extract_signer_did() - Demo")
    print("=" * 70)
    print("\n⚡ This demo shows how extract_signer_did() enables:")
    print("   • Rate limiting BEFORE signature verification (saves CPU)")
    print("   • Request routing by agent tier")
    print("   • Audit logging of all requests (even failures)")

    # Reset state
    print("\n🧹 Resetting demo state...")
    reset_demo()

    # --- SCENARIO 1: Free Tier Rate Limiting ---
    print_section("SCENARIO 1: Free Tier Rate Limiting (3 requests/min)")

    print("\n📝 Concept: extract_signer_did() allows checking rate limits")
    print("   BEFORE expensive signature verification, saving ~50% CPU")
    print("   on rate-limited requests.\n")

    # Create free tier agent
    free_agent, free_token = create_agent_and_token("free tier content")
    print(f"▶ Created Free Tier Agent: {free_agent.did[:40]}...")

    # Make 5 requests (limit is 3)
    print(f"\n▶ Making 5 requests (limit is 3)...")
    for i in range(5):
        result = publish_article(free_token, f"Article {i+1}", f"Content from free agent - request {i+1}")

        if result["success"]:
            data = result["data"]
            print(f"   Request {i+1}: ✅ SUCCESS (Remaining: {data['rate_limit_remaining']})")
        else:
            print(f"   Request {i+1}: ❌ RATE LIMITED (as expected)")

    print("\n💡 Performance Benefit:")
    print("   • Requests 1-3: Full signature verification")
    print("   • Requests 4-5: Rejected at rate limit check (no crypto)")
    print("   • ~50% CPU saved on rejected requests!")

    # --- SCENARIO 2: Tiered Request Routing ---
    print_section("SCENARIO 2: Request Routing by Agent Tier")

    print("\n📝 Concept: extract_signer_did() enables routing requests to")
    print("   different handlers based on agent tier, BEFORE verification.\n")

    # Create agents for each tier
    agents = {}
    for tier in ["free", "standard", "premium"]:
        agent, token = create_agent_and_token(f"{tier} content")
        agents[tier] = {"agent": agent, "token": token}
        set_tier(agent.did, tier)
        print(f"▶ Created {tier.capitalize()} Agent: {agent.did[:40]}...")

    # Make requests from each tier
    print("\n▶ Publishing from different tiers...")
    for tier in ["free", "standard", "premium"]:
        result = publish_article(
            agents[tier]["token"],
            f"{tier.capitalize()} Article",
            f"Content from {tier} tier agent"
        )

        if result["success"]:
            data = result["data"]
            print(f"\n   {tier.capitalize()} Tier:")
            print(f"   • Handler: {data['handler']}")
            print(f"   • Rate Limit: {data['rate_limit_remaining']} remaining")
            print(f"   • Status: {data['status']}")

    print("\n💡 Routing Benefit:")
    print("   • Premium agents → Low latency queue")
    print("   • Standard agents → Balanced queue")
    print("   • Free agents → Best effort queue")
    print("   • Routing decision made BEFORE expensive verification")

    # --- SCENARIO 3: Audit Logging (Security Monitoring) ---
    print_section("SCENARIO 3: Audit Logging (Security Monitoring)")

    print("\n📝 Concept: extract_signer_did() allows logging ALL requests")
    print("   (even invalid ones) for security monitoring.\n")

    # Make some valid and invalid requests
    print("▶ Making various requests...")

    # Valid request
    valid_agent, valid_token = create_agent_and_token("valid content")
    publish_article(valid_token, "Valid Article", "Valid content")
    print("   1. Valid request: ✅")

    # Invalid token format
    try:
        publish_article("invalid-token", "Bad Article", "Bad content")
    except:
        pass
    print("   2. Invalid token format: ❌ (logged)")

    # Rate limited request (using free agent)
    for i in range(4):
        publish_article(free_token, f"Spam {i}", "Spam content")
    print("   3-6. Rate limited requests: ❌ (all logged)")

    # Get audit log (now in JSON format)
    print("\n▶ Recent Audit Log Entries (Structured JSON):")
    log_data = get_audit_log(limit=10)
    for entry in log_data["entries"][-10:]:
        # Pretty print JSON log entry
        timestamp = entry.get("timestamp", "")
        event = entry.get("event_type", "")
        status = entry.get("status", "")
        endpoint = entry.get("endpoint", "")
        did = entry.get("did", "unknown")[:20]
        message = entry.get("message", "")
        print(f"   [{timestamp}] {event} | {status} | {endpoint} | {did}... | {message}")

    print("\n💡 Security Benefit:")
    print("   • ALL requests logged (even before verification)")
    print("   • Track attack attempts and abuse patterns")
    print("   • Monitor rate limit violations")
    print("   • No performance penalty (fast DID extraction)")

    # --- SCENARIO 4: Performance Comparison ---
    print_section("SCENARIO 4: Performance Comparison")

    print("\n📝 Concept: Measure the performance difference between:")
    print("   • extract_signer_did() - Fast DID extraction (~2x faster)")
    print("   • verify_jws() - Full signature verification\n")

    test_agent, test_token = create_agent_and_token("test content")

    # Measure extract_signer_did()
    iterations = 100
    start = time.time()
    for _ in range(iterations):
        did = didlite.extract_signer_did(test_token)
    extract_time = time.time() - start

    # Measure verify_jws()
    start = time.time()
    for _ in range(iterations):
        header, payload = didlite.verify_jws(test_token)
    verify_time = time.time() - start

    print(f"▶ Performance Test ({iterations} iterations):\n")
    print(f"   extract_signer_did(): {extract_time:.4f}s ({extract_time/iterations*1000:.2f}ms each)")
    print(f"   verify_jws():         {verify_time:.4f}s ({verify_time/iterations*1000:.2f}ms each)")
    print(f"\n   Speedup: {verify_time/extract_time:.2f}x faster")
    print(f"   Time saved per request: {(verify_time-extract_time)/iterations*1000:.2f}ms")

    print("\n💡 Impact on Rate-Limited Requests:")
    if verify_time > extract_time:
        savings = ((verify_time - extract_time) / verify_time) * 100
        print(f"   • CPU savings on rejected requests: ~{savings:.0f}%")
        print(f"   • For 1000 rate-limited requests/sec:")
        print(f"     - Without extract_signer_did(): {verify_time*1000/iterations:.0f}ms CPU")
        print(f"     - With extract_signer_did():    {extract_time*1000/iterations:.0f}ms CPU")
        print(f"     - CPU time saved: {(verify_time-extract_time)*1000/iterations:.0f}ms per request")

    # --- Summary ---
    print_section("SUMMARY: When to Use extract_signer_did()")

    print("\n✅ USE extract_signer_did() for:")
    print("   • Rate limiting (check quota before verification)")
    print("   • Request routing (route to handler before verification)")
    print("   • Audit logging (log all attempts, even failures)")
    print("   • DDoS protection (block bad actors early)")
    print("   • Cost optimization (save CPU on rejected requests)")

    print("\n⚠️  ALWAYS follow with verify_jws() for:")
    print("   • Authentication decisions")
    print("   • Authorization checks")
    print("   • Content integrity verification")
    print("   • Any security-critical operations")

    print("\n⚡ Performance Rule:")
    print("   1. extract_signer_did() - Fast filtering (rate limits, routing)")
    print("   2. verify_jws() - Cryptographic verification (only if passed filters)")
    print("   3. Process request - Business logic")

    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70)
    print("\n💡 View the audit log at: GET /admin/audit-log")
    print("💡 View rate limits at: GET /admin/rate-limits")
    print("💡 API docs at: http://127.0.0.1:8000/docs\n")

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(BASE_URL)
        if response.status_code != 200:
            print("❌ Server not responding correctly. Please start the server first:")
            print("   python 08_fast_routing/server.py")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server first:")
        print("   python 08_fast_routing/server.py")
        exit(1)

    main()
