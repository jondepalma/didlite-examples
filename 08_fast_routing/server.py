"""
Example 8: Fast Routing with extract_signer_did()

Demonstrates the performance benefits of extract_signer_did() for:
1. Rate Limiting - Check quota before expensive signature verification
2. Request Routing - Route to different handlers based on agent tier
3. Audit Logging - Log all requests (even invalid ones) for security monitoring

⚠️  EDUCATIONAL DEMO DISCLAIMER

This example demonstrates extract_signer_did() for educational purposes.

Production implementations should use:
- Distributed rate limiting (Redis, Memcached)
- Structured logging (JSON logs, ELK stack, CloudWatch)
- Database-backed audit trails
- Proper error monitoring and alerting
- DDoS protection at infrastructure level

This demo uses:
- In-memory rate limiting (resets on restart)
- Simple file-based logging (not production-ready)
- Mock agent tiers (normally from database)
"""

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import Annotated
import didlite
from didlite import extract_signer_did, verify_jws
import time
from datetime import datetime
from collections import defaultdict
import os
import json

app = FastAPI(title="Fast Routing API - extract_signer_did() Demo")

# --- Configuration ---
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMITS = {
    "premium": 100,   # 100 requests per minute
    "standard": 10,   # 10 requests per minute
    "free": 3         # 3 requests per minute
}

# --- In-Memory Storage (Educational - Use Redis/DB in Production) ---
rate_limit_tracker = defaultdict(list)  # DID -> list of timestamps
agent_tiers = {}  # DID -> tier (premium/standard/free)
audit_log_file = "audit.log"

# --- Helper: Audit Logging ---
def audit_log(event_type: str, did: str, endpoint: str, status: str, message: str = ""):
    """
    Log all requests for security monitoring using structured JSON format.
    Uses extract_signer_did() to log even BEFORE verification.

    Production: Send to ELK, CloudWatch, Datadog, etc.
    """
    timestamp = datetime.utcnow().isoformat()

    # Structured JSON log entry
    log_entry = {
        "timestamp": timestamp,
        "event_type": event_type,
        "status": status,
        "endpoint": endpoint,
        "did": did,
        "message": message
    }

    # Write as JSON (one entry per line for easy parsing)
    with open(audit_log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Console output (human-readable)
    print(f"📋 AUDIT: {event_type} | {status} | {did[:20]}...")

# --- Helper: Rate Limiting ---
def check_rate_limit(did: str) -> tuple[bool, str, int]:
    """
    Check if DID has exceeded rate limit.
    Returns (is_allowed, tier, remaining_quota)

    Production: Use Redis with sliding window or token bucket algorithm
    """
    # Determine tier (default to free for unknown agents)
    tier = agent_tiers.get(did, "free")
    limit = RATE_LIMITS[tier]

    # Clean old timestamps outside the window
    current_time = time.time()
    rate_limit_tracker[did] = [
        ts for ts in rate_limit_tracker[did]
        if current_time - ts < RATE_LIMIT_WINDOW
    ]

    # Check limit
    request_count = len(rate_limit_tracker[did])
    remaining = limit - request_count

    if request_count >= limit:
        return False, tier, 0

    # Record this request
    rate_limit_tracker[did].append(current_time)
    return True, tier, remaining - 1

# --- Helper: Request Routing ---
def get_handler_for_tier(tier: str) -> str:
    """
    Route requests to different handlers based on agent tier.
    Premium agents get priority processing.

    Production: Route to different microservices, regions, or priority queues
    """
    handlers = {
        "premium": "Premium Handler (Low Latency SSD Queue)",
        "standard": "Standard Handler (Balanced Queue)",
        "free": "Free Tier Handler (Best Effort Queue)"
    }
    return handlers.get(tier, handlers["free"])

# --- API Models ---
class Article(BaseModel):
    title: str
    content: str

class PublishResponse(BaseModel):
    status: str
    message: str
    author_did: str
    tier: str
    handler: str
    rate_limit_remaining: int

# --- The Optimized Endpoint ---
@app.post("/publish", response_model=PublishResponse)
async def publish_article(
    article: Article,
    authorization: Annotated[str | None, Header()] = None
):
    """
    Publish an article with optimized request processing:

    1. FAST: Extract DID without verification (extract_signer_did)
    2. FAST: Audit log the attempt
    3. FAST: Check rate limit (before expensive crypto)
    4. FAST: Route to appropriate handler
    5. SLOW: Verify signature (only after passing fast checks)
    6. PROCESS: Handle the request

    This ordering saves ~50% CPU on rate-limited requests!
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization format")

    # --- STEP 1: Fast DID Extraction (No Verification) ---
    # ~2x faster than verify_jws() - useful for early filtering
    try:
        signer_did = extract_signer_did(token)
    except Exception as e:
        audit_log("EXTRACT_DID", "unknown", "/publish", "FAILED", f"Invalid token format: {e}")
        raise HTTPException(status_code=400, detail="Invalid token format")

    # --- STEP 2: Audit Logging (Early - Even if Request Fails Later) ---
    audit_log("REQUEST", signer_did, "/publish", "RECEIVED", f"Article: {article.title[:30]}...")

    # --- STEP 3: Rate Limiting (Before Expensive Verification) ---
    # If rate limited, we save ~50% CPU by not doing signature verification!
    is_allowed, tier, remaining = check_rate_limit(signer_did)

    if not is_allowed:
        audit_log("RATE_LIMIT", signer_did, "/publish", "BLOCKED", f"Tier: {tier}")
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for {tier} tier. Try again in {RATE_LIMIT_WINDOW}s"
        )

    # --- STEP 4: Request Routing (Determine Handler) ---
    handler = get_handler_for_tier(tier)
    audit_log("ROUTING", signer_did, "/publish", "ROUTED", f"Handler: {handler}, Tier: {tier}")

    # --- STEP 5: Signature Verification (Expensive - But Only After Passing Checks) ---
    # Now we do the expensive crypto operation on legitimate requests only
    try:
        header, payload = verify_jws(token)
    except Exception as e:
        audit_log("VERIFY", signer_did, "/publish", "FAILED", f"Invalid signature: {e}")
        raise HTTPException(status_code=403, detail=f"Invalid signature: {e}")

    # Verify the DID from header matches what we extracted
    if header.get('kid') != signer_did:
        audit_log("VERIFY", signer_did, "/publish", "MISMATCH", "DID mismatch")
        raise HTTPException(status_code=403, detail="DID mismatch")

    audit_log("VERIFY", signer_did, "/publish", "SUCCESS", "Signature valid")

    # --- STEP 6: Process Request ---
    # In production: Queue to appropriate handler, database write, etc.
    audit_log("PUBLISH", signer_did, "/publish", "SUCCESS", f"Article published: {article.title}")

    return PublishResponse(
        status="published",
        message=f"Article '{article.title}' published successfully",
        author_did=signer_did,
        tier=tier,
        handler=handler,
        rate_limit_remaining=remaining
    )

# --- Admin Endpoints (For Demo) ---
@app.post("/admin/set-tier/{did}/{tier}")
async def set_agent_tier(did: str, tier: str):
    """Set agent tier (admin only - for demo purposes)"""
    if tier not in RATE_LIMITS:
        raise HTTPException(status_code=400, detail=f"Invalid tier. Must be: {list(RATE_LIMITS.keys())}")

    agent_tiers[did] = tier
    audit_log("ADMIN", did, "/admin/set-tier", "SUCCESS", f"Set tier to {tier}")
    return {"status": "success", "did": did, "tier": tier}

@app.get("/admin/audit-log")
async def get_audit_log(limit: int = 50):
    """Get recent audit log entries (structured JSON format)"""
    if not os.path.exists(audit_log_file):
        return {"entries": [], "total": 0}

    with open(audit_log_file, "r") as f:
        lines = f.readlines()

    # Parse JSON entries
    entries = []
    for line in lines:
        try:
            entries.append(json.loads(line.strip()))
        except json.JSONDecodeError:
            # Handle any malformed entries gracefully
            continue

    # Return most recent entries
    recent_entries = entries[-limit:] if limit > 0 else entries

    return {"entries": recent_entries, "total": len(entries)}

@app.get("/admin/rate-limits")
async def get_rate_limits():
    """View current rate limit status"""
    current_time = time.time()
    status = {}

    for did, timestamps in rate_limit_tracker.items():
        # Clean old timestamps
        active_requests = [ts for ts in timestamps if current_time - ts < RATE_LIMIT_WINDOW]
        tier = agent_tiers.get(did, "free")
        limit = RATE_LIMITS[tier]

        status[did[:20] + "..."] = {
            "tier": tier,
            "requests_in_window": len(active_requests),
            "limit": limit,
            "remaining": limit - len(active_requests)
        }

    return status

@app.delete("/admin/reset")
async def reset_demo():
    """Reset all demo state"""
    rate_limit_tracker.clear()
    agent_tiers.clear()

    if os.path.exists(audit_log_file):
        os.remove(audit_log_file)

    return {"status": "reset", "message": "All state cleared"}

@app.get("/")
async def root():
    return {
        "service": "Fast Routing API - extract_signer_did() Demo",
        "endpoints": {
            "publish": "POST /publish - Publish article with rate limiting and routing",
            "admin_tier": "POST /admin/set-tier/{did}/{tier} - Set agent tier",
            "admin_log": "GET /admin/audit-log - View audit log",
            "admin_limits": "GET /admin/rate-limits - View rate limit status",
            "admin_reset": "DELETE /admin/reset - Reset demo state"
        },
        "tiers": RATE_LIMITS
    }

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  Example 8: Fast Routing with extract_signer_did()")
    print("=" * 70)
    print("\n📝 This demo shows the performance benefits of extract_signer_did():")
    print("   1. Rate Limiting - Check quota BEFORE signature verification")
    print("   2. Request Routing - Route by tier BEFORE verification")
    print("   3. Audit Logging - Log all attempts (even failures)")
    print("\n⚡ Performance Benefit:")
    print("   - extract_signer_did() is ~2x faster than verify_jws()")
    print("   - Rate-limited requests save ~50% CPU (no crypto)")
    print("   - Audit logging happens even for invalid requests")
    print("\n🎯 Try the demo:")
    print("   python 08_fast_routing/demo.py")
    print("\n" + "=" * 70 + "\n")

    uvicorn.run(app, host="127.0.0.1", port=8000)
