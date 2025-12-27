"""
Secure Agent Communication API

A FastAPI application demonstrating cryptographically secure communication between
AI agents using didlite (DID-based identity and JWS signing).

Agents:
- Bob (good actor): Honest agent who sends legitimate messages
- Alice (good actor): Honest agent who sends legitimate messages
- Chris (bad actor): Malicious agent who attempts various attacks

Each message is cryptographically signed with the sender's DID, ensuring:
- Authentication: The recipient can verify who sent the message
- Integrity: Any tampering with the message invalidates the signature
- Non-repudiation: The sender cannot deny sending the message
"""

from fastapi import FastAPI, HTTPException, Path, Body
from fastapi.responses import JSONResponse
from typing import Optional
import uvicorn

from models import (
    Message,
    SignedMessage,
    VerifyRequest,
    VerifyResponse,
    AgentIdentity,
    MessageHistory,
    AttackScenario
)
from agents import agent_manager


# Initialize FastAPI app
app = FastAPI(
    title="Secure Agent Communication API",
    description="Cryptographically secure messaging between AI agents using didlite",
    version="1.0.0"
)


@app.get("/", tags=["General"])
async def root():
    """API root endpoint with usage information."""
    return {
        "message": "Secure Agent Communication API",
        "agents": agent_manager.list_agents(),
        "endpoints": {
            "identities": "GET /agents - List all agents and their DIDs",
            "send_message": "POST /agents/{agent_name}/send - Send a signed message",
            "verify_message": "POST /agents/{agent_name}/verify - Verify a received message",
            "message_history": "GET /agents/{agent_name}/messages - View message history",
            "attacks": "POST /agents/chris/attack - Execute attack scenarios (Chris only)"
        },
        "example_flow": [
            "1. GET /agents - See all agent DIDs",
            "2. POST /agents/bob/send - Bob sends a message to Alice",
            "3. POST /agents/alice/verify - Alice verifies Bob's message",
            "4. POST /agents/chris/attack - Chris attempts various attacks"
        ]
    }


@app.get("/agents", response_model=list[AgentIdentity], tags=["Agents"])
async def list_agents():
    """List all agents and their DIDs."""
    agents = []
    for name in agent_manager.list_agents():
        did = agent_manager.get_did(name)
        agents.append(AgentIdentity(name=name, did=did))
    return agents


@app.get("/agents/{agent_name}/identity", response_model=AgentIdentity, tags=["Agents"])
async def get_agent_identity(
    agent_name: str = Path(..., description="Agent name (bob, alice, chris)")
):
    """Get a specific agent's identity information."""
    did = agent_manager.get_did(agent_name)
    if not did:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    return AgentIdentity(name=agent_name.lower(), did=did)


@app.post("/agents/{agent_name}/send", response_model=SignedMessage, tags=["Messaging"])
async def send_message(
    agent_name: str = Path(..., description="Sender agent name"),
    message: Message = Body(..., description="Message to send")
):
    """
    Send a cryptographically signed message from one agent to another.

    The message is signed using the sender's private key, creating a JWS token
    that includes the sender's DID in the token header. This ensures:
    - The recipient can verify the sender's identity
    - The message cannot be tampered with
    - The sender cannot deny sending the message
    """
    try:
        result = agent_manager.send_message(
            sender=agent_name,
            recipient=message.recipient,
            content=message.content,
            expires_in=5  # 5 second expiration
        )

        return SignedMessage(
            token=result["token"],
            sender_did=result["sender_did"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@app.post("/agents/{agent_name}/verify", response_model=VerifyResponse, tags=["Messaging"])
async def verify_message(
    agent_name: str = Path(..., description="Agent verifying the message"),
    request: VerifyRequest = Body(..., description="Message to verify")
):
    """
    Verify a received message.

    This endpoint:
    1. Extracts the sender's DID from the token header
    2. Resolves the DID to the sender's public key (no network calls needed!)
    3. Verifies the cryptographic signature
    4. Checks token expiration
    5. Returns the verified payload

    If verification fails, it returns details about why (e.g., invalid signature,
    expired token, tampered payload).
    """
    result = agent_manager.verify_message(request.token)

    return VerifyResponse(
        valid=result["valid"],
        payload=result["payload"],
        sender_did=result["sender_did"],
        error=result["error"]
    )


@app.get("/agents/{agent_name}/messages", response_model=MessageHistory, tags=["Messaging"])
async def get_message_history(
    agent_name: str = Path(..., description="Agent name")
):
    """Get message history for an agent (sent and received)."""
    try:
        history = agent_manager.get_message_history(agent_name)
        return MessageHistory(**history)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/agents/chris/attack", tags=["Security Demonstrations"])
async def execute_attack(
    scenario: AttackScenario = Body(..., description="Attack scenario to execute")
):
    """
    Execute an attack scenario (for educational purposes).

    Chris (the bad actor) attempts various attacks:
    - **replay**: Resend an old valid message (succeeds if not expired)
    - **forge**: Try to impersonate another agent (fails - DID reveals true sender)
    - **no_private_key**: Try to sign using only public key (impossible - demonstrates asymmetric crypto)
    - **intercept**: Modify a message in transit (fails - signature becomes invalid)
    - **token_theft**: Reuse a stolen token (succeeds, but DID reveals original sender)

    These demonstrations show how didlite's cryptographic signatures protect against
    common attacks, and where additional protections (like nonce tracking) are needed.
    """
    try:
        result = agent_manager.execute_attack(
            attacker="chris",
            attack_type=scenario.attack_type,
            target_agent=scenario.target_agent,
            stolen_token=scenario.stolen_token
        )

        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attack failed: {str(e)}")


@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agents": len(agent_manager.list_agents())}


@app.post("/nonce/enable", tags=["Nonce Protection"])
async def enable_nonce_protection():
    """
    Enable nonce-based replay protection (application-layer security).

    ⚠️  EDUCATIONAL DEMO: This uses a simple file-based nonce tracker.
    Production systems should use Redis, a database, or similar.
    """
    agent_manager.enable_nonce_tracking()
    return {
        "message": "Nonce protection enabled",
        "note": "All new messages will include nonces, and replays will be detected",
        "stats": agent_manager.get_nonce_stats()
    }


@app.post("/nonce/disable", tags=["Nonce Protection"])
async def disable_nonce_protection():
    """Disable nonce-based replay protection."""
    agent_manager.disable_nonce_tracking()
    return {
        "message": "Nonce protection disabled",
        "note": "Messages sent without nonces (expiration-only protection)",
        "stats": agent_manager.get_nonce_stats()
    }


@app.get("/nonce/stats", tags=["Nonce Protection"])
async def get_nonce_stats():
    """Get nonce tracking statistics."""
    return agent_manager.get_nonce_stats()


if __name__ == "__main__":
    # Run the server
    print("\n" + "="*60)
    print("Secure Agent Communication API")
    print("="*60)
    print("\nStarting server...")
    print("API Documentation: http://127.0.0.1:8000/docs")
    print("API Root: http://127.0.0.1:8000/")
    print("\nAgents initialized:")
    for name in agent_manager.list_agents():
        did = agent_manager.get_did(name)
        print(f"  - {name.upper()}: {did}")
    print("\n" + "="*60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
