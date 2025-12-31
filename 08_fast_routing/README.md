# Example 8: Fast Routing with extract_signer_did()

**Concept**: Performance optimization using fast DID extraction without full signature verification

This example demonstrates the **new `extract_signer_did()` function** introduced in didlite v0.2.3, which extracts the signer's DID from a JWS token **~2x faster** than full signature verification.

## What You'll Learn

### 1. Performance-Optimized Request Processing
- Extract DID **before** expensive signature verification
- Save ~50% CPU on rate-limited or rejected requests
- Optimize the "happy path" vs "rejection path"

### 2. Rate Limiting by Agent Identity
- Check request quotas using DID
- Enforce tier-based limits (free/standard/premium)
- Block abuse **before** crypto operations

### 3. Request Routing by Agent Tier
- Route to different handlers based on agent tier
- Priority queuing for premium agents
- Load distribution before verification

### 4. Comprehensive Audit Logging
- Log **all** requests (even invalid ones)
- Security monitoring and abuse detection
- Track DID even for malformed tokens

## Key Function: extract_signer_did()

```python
from didlite import extract_signer_did, verify_jws

# Fast DID extraction (no signature verification)
try:
    signer_did = extract_signer_did(token)
    # ~2x faster than verify_jws()
    # Use for: routing, rate limiting, logging
except Exception:
    # Invalid token format
    pass

# Full signature verification (expensive)
try:
    header, payload = verify_jws(token)
    # Use for: authentication, authorization
except Exception:
    # Invalid signature
    pass
```

## When to Use extract_signer_did()

### ✅ Good Use Cases (Fast Filtering)
- **Rate Limiting**: Check quota before verification
- **Request Routing**: Route to handler before verification
- **Audit Logging**: Log all attempts (even failures)
- **DDoS Protection**: Block known bad actors early
- **Cost Optimization**: Save CPU on rejected requests

### ⚠️ Never Use Alone For (Always Verify After)
- Authentication decisions
- Authorization checks
- Content integrity verification
- Security-critical operations

## Performance Benefits

```
Scenario: API handling 1000 requests/second, 70% are rate-limited

WITHOUT extract_signer_did():
- All 1000 requests: Full signature verification
- CPU cost: 1000 × verify_jws() = HIGH

WITH extract_signer_did():
- 700 rate-limited: extract_signer_did() only (fast)
- 300 legitimate: extract_signer_did() + verify_jws()
- CPU savings: ~50% on rate-limited requests
```

## Architecture

```
Request Flow (Optimized):

1. [FAST] extract_signer_did(token)
   ↓ (~2x faster than verify)
2. [FAST] Audit log (security monitoring)
   ↓
3. [FAST] Check rate limit
   ↓ (if exceeded → reject, save 50% CPU)
4. [FAST] Route to handler (tier-based)
   ↓
5. [SLOW] verify_jws(token)
   ↓ (only for legitimate requests)
6. [PROCESS] Handle request
```

## Running the Example

### 1. Start the Server

```bash
python 08_fast_routing/server.py
```

The server will start on `http://0.0.0.0:8000` (accessible from external IPs)

### 2. Run the Demo (in another terminal)

```bash
python 08_fast_routing/demo.py
```

The demo will:
1. Test rate limiting for free tier (3 requests/min)
2. Demonstrate request routing by tier
3. Show audit logging of all requests
4. Benchmark performance difference

### 3. Explore the API

Visit the interactive API docs at: `http://localhost:8000/docs` (or use your server's IP address)

## API Endpoints

### Publishing
- `POST /publish` - Publish article (rate limited by tier)

### Admin (Demo Only)
- `POST /admin/set-tier/{did}/{tier}` - Set agent tier
- `GET /admin/audit-log` - View audit log
- `GET /admin/rate-limits` - View rate limit status
- `DELETE /admin/reset` - Reset demo state

## Rate Limits by Tier

| Tier     | Requests/Minute | Use Case                    |
|----------|-----------------|----------------------------|
| Free     | 3               | Best effort, public agents |
| Standard | 10              | Regular users              |
| Premium  | 100             | Priority processing        |

## Example Scenarios

### Scenario 1: Rate Limiting (CPU Savings)

```python
# Free tier agent makes 5 requests (limit: 3)
free_agent = didlite.AgentIdentity()
token = didlite.create_jws(free_agent, {"content": "article"})

# Requests 1-3: Pass rate limit, full verification
# Requests 4-5: Blocked at rate limit (no verification)
# Result: 40% CPU saved on requests 4-5
```

### Scenario 2: Request Routing

```python
# Different tiers routed to different handlers
premium_agent → "Low Latency SSD Queue"
standard_agent → "Balanced Queue"
free_agent → "Best Effort Queue"

# Routing decision made BEFORE expensive verification
```

### Scenario 3: Audit Logging (Structured JSON)

```json
// ALL requests logged in structured JSON format (even invalid ones)
{"timestamp": "2025-01-30T10:15:23Z", "event_type": "REQUEST", "status": "RECEIVED", "endpoint": "/publish", "did": "did:key:z6Mk...", "message": "Article: Breaking News"}
{"timestamp": "2025-01-30T10:15:23Z", "event_type": "VERIFY", "status": "SUCCESS", "endpoint": "/publish", "did": "did:key:z6Mk...", "message": "Signature valid"}
{"timestamp": "2025-01-30T10:15:24Z", "event_type": "EXTRACT_DID", "status": "FAILED", "endpoint": "/publish", "did": "unknown", "message": "Invalid token format"}
{"timestamp": "2025-01-30T10:15:25Z", "event_type": "RATE_LIMIT", "status": "BLOCKED", "endpoint": "/publish", "did": "did:key:z6Mk...", "message": "Tier: free"}
```

## Educational Disclaimer

⚠️ **This example is for educational purposes.**

Production implementations should use:
- **Distributed rate limiting**: Redis, Memcached (not in-memory)
- **Structured logging**: Ship JSON logs to ELK stack, CloudWatch, Datadog
- **Database-backed audit**: PostgreSQL, MongoDB (not file-based)
- **Proper DDoS protection**: WAF, CDN, infrastructure-level
- **Monitoring & alerting**: Prometheus, Grafana, PagerDuty

This demo uses:
- In-memory rate limiting (resets on restart)
- **Structured JSON logging** to local file (production: ship to log aggregator)
- Mock agent tiers (should be database-backed)
- **HTTP 429 status codes** for rate limiting (industry standard)

## Key Takeaways

1. **Performance Rule**: Fast filter first, verify second
   - `extract_signer_did()` for filtering (rate limits, routing)
   - `verify_jws()` for security decisions

2. **CPU Optimization**: Save resources on rejected requests
   - Rate-limited requests: ~50% CPU savings
   - Invalid format requests: ~100% crypto savings

3. **Security**: Structured JSON audit logging
   - Track abuse patterns
   - Monitor attack attempts
   - Log even before verification
   - Easy to parse and analyze

4. **Scalability**: Tier-based routing and proper HTTP status codes
   - Premium agents get priority
   - Load distribution
   - Fair resource allocation
   - **HTTP 429** (Too Many Requests) for rate limiting
   - **HTTP 403** (Forbidden) for invalid signatures

## Production Considerations

### Rate Limiting
```python
# Demo (in-memory)
rate_limit_tracker = defaultdict(list)

# Production (distributed)
import redis
r = redis.Redis()
r.incr(f"rate_limit:{did}", ex=60)
```

### Audit Logging
```python
# Demo (structured JSON to file)
import json
log_entry = {
    "timestamp": datetime.utcnow().isoformat(),
    "event_type": event_type,
    "status": status,
    "endpoint": endpoint,
    "did": did,
    "message": message
}
with open("audit.log", "a") as f:
    f.write(json.dumps(log_entry) + "\n")

# Production (ship to log aggregator)
import logging
import json_logging
logger = logging.getLogger()
logger.info("request", extra={
    "did": did,
    "endpoint": endpoint,
    "status": status
})
# Ship to: ELK, CloudWatch, Datadog, Splunk, etc.
```

### Request Routing
```python
# Demo (mock handlers)
handler = get_handler_for_tier(tier)

# Production (microservices)
if tier == "premium":
    route_to_service("premium-api.internal:8080")
elif tier == "standard":
    route_to_service("standard-api.internal:8080")
```

## See Also

- [didlite on PyPI](https://pypi.org/project/didlite/) - extract_signer_did() introduced in v0.2.3
- [Example 1](../01_fastapi_cms/) - Basic FastAPI authentication
- [Example 4](../04_secure_agent_comms/) - Full agent communication system

## References

- [RFC 7519 - JWT](https://tools.ietf.org/html/rfc7519) - JSON Web Tokens
- [Rate Limiting Patterns](https://en.wikipedia.org/wiki/Rate_limiting)
- [Token Bucket Algorithm](https://en.wikipedia.org/wiki/Token_bucket)
