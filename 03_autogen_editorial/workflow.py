import didlite

# --- 1. Identities ---
copywriter_id = didlite.AgentIdentity()
editor_id = didlite.AgentIdentity()

print(f"✍️  Copywriter: {copywriter_id.did}")
print(f"🧐 Editor:     {editor_id.did}")

# --- 2. The Protocol ---
def wrap_draft(sender_id: didlite.AgentIdentity, draft_text: str) -> str:
    """Wraps the draft in a JWS envelope"""
    payload = {"draft": draft_text, "version": 1}
    return didlite.create_jws(sender_id, payload)

def review_draft(token: str) -> str:
    """Editor logic: Unwraps and verifies"""
    try:
        header, payload = didlite.verify_jws(token)

        # Extract sender DID from token header (now directly available)
        sender = header.get('kid')

        draft = payload.get("draft")

        # Identity Check (Allow List)
        if sender != copywriter_id.did:
            return "⛔ ACCESS DENIED: I do not recognize this author."

        return f"✅ DRAFT ACCEPTED from {sender[:10]}...\n   Content: '{draft}'"

    except Exception as e:
        return f"⚠️  SECURITY ALERT: Signature Invalid. {str(e)}"

# --- 3. Simulation (The Workflow) ---
if __name__ == "__main__":

    # Round 1: Legitimate Flow
    print("\n--- ROUND 1: Legitimate Submission ---")
    draft_msg = wrap_draft(copywriter_id, "Buy our new product, it's great!")
    print(f"Transmitting JWS: {draft_msg[:30]}...")

    response = review_draft(draft_msg)
    print(response)

    # Round 2: Imposter Flow
    print("\n--- ROUND 2: Imposter Submission ---")
    hacker_id = didlite.AgentIdentity() # Unknown ID
    fake_msg = wrap_draft(hacker_id, "Click this phishing link!")

    response = review_draft(fake_msg)
    print(response)

    # Round 3: Tampering Flow
    print("\n--- ROUND 3: Tampering Attempt ---")
    # Man in the middle modifies the string
    tampered_msg = draft_msg[:-5] + "ABCDE"

    response = review_draft(tampered_msg)
    print(response)
