import uvicorn
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from typing import Annotated, List
import didlite
import time
import base64
import json

app = FastAPI(title="Agentic CMS API")

# --- 1. The Gatekeeper (Middleware) ---
async def verify_publisher(authorization: Annotated[str | None, Header()] = None):
    """
    Validates that the request comes from a signed Agent.
    Replaces API Keys with Cryptographic Signatures.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Auth Header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid scheme")

        # VERIFY: Who signed this?
        payload = didlite.verify_jws(token)

        # Extract DID from token header
        header = json.loads(base64.urlsafe_b64decode(token.split('.')[0] + '=='))
        payload['kid'] = header.get('kid')

        return payload

    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Signature Rejected: {str(e)}")

# --- 2. The Content Endpoint ---
class BlogPost(BaseModel):
    title: str
    content: str
    tags: List[str]

@app.post("/publish")
async def publish_article(
    post: BlogPost,
    agent_claims: dict = Depends(verify_publisher)
):
    """
    Only publishes if the request is signed.
    """
    # Extract the Agent's DID from the token
    author_did = agent_claims.get("iss") or agent_claims.get("kid")

    print(f"📝 PUBLISHED: '{post.title}'")
    print(f"   └── By Author: {author_did}")

    return {
        "status": "published",
        "url": f"/blog/{post.title.lower().replace(' ', '-')}",
        "verified_author": author_did
    }

# --- 3. Client Simulation (The "Copywriter Agent") ---
if __name__ == "__main__":
    import threading
    import requests

    # Start Server
    def run_server(): uvicorn.run(app, port=8000, log_level="critical")
    threading.Thread(target=run_server, daemon=True).start()
    time.sleep(1)

    print("\n--- AGENT STARTING ---")

    # 1. Agent wakes up & generates Identity
    copywriter = didlite.AgentIdentity()
    print(f"🤖 Copywriter ID: {copywriter.did}")

    # 2. Agent drafts content
    draft = {
        "action": "publish",
        "title": "Why AI Agents Need Identity",
        "timestamp": time.time()
    }

    # 3. Agent SIGNS the draft (The 'didlite' magic)
    token = didlite.create_jws(copywriter, draft)

    # 4. Agent pushes to CMS
    print("🚀 Uploading to CMS...")
    response = requests.post(
        "http://localhost:8000/publish",
        json={
            "title": "Why AI Agents Need Identity",
            "content": "It is all about trust...",
            "tags": ["ai", "security"]
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"✅ CMS Response: {response.json()}")
