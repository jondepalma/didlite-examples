import os
from langchain.tools import tool
import didlite
import base64
import json

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-demo-purposes"

# --- 1. The Brand Manager Identity ---
BRAND_IDENTITY = didlite.AgentIdentity()

# --- 2. The Secured Tool ---
@tool
def publish_tweet(content: str, signed_token: str) -> str:
    """
    Publishes a tweet.
    CRITICAL: You must provide a 'signed_token' verifying the content.
    """
    try:
        # VERIFY: Did the Brand Identity actually sign this text?
        payload = didlite.verify_jws(signed_token)

        # CHECK: Integrity Check
        if payload.get("content") != content:
            return "❌ SAFETY BLOCK: Token content does not match tweet text."

        # Extract signer DID from token header
        header = json.loads(base64.urlsafe_b64decode(signed_token.split('.')[0] + '=='))
        signer = header.get('kid')

        return f"✅ TWEET LIVE: '{content}' (Authorized by {signer[:15]}...)"

    except Exception as e:
        return f"❌ REJECTED: Invalid Signature. {str(e)}"

# --- 3. The Helper (The "Signer") ---
def create_signed_tweet(content):
    """
    This function represents the 'System' logic that wraps the LLM.
    It signs the intent so the Tool can verify it.
    """
    payload = {"content": content}
    token = didlite.create_jws(BRAND_IDENTITY, payload)
    return token

# --- 4. Simulation ---
if __name__ == "__main__":
    print(f"🔐 Brand Identity: {BRAND_IDENTITY.did}")

    tweet_text = "Hello World! #AI"

    print(f"\n1. System is signing tweet: '{tweet_text}'")
    token = create_signed_tweet(tweet_text)

    # We simulate the LangChain Agent calling the tool
    print("\n2. Agent invoking publish_tweet...")
    result = publish_tweet.invoke({
        "content": tweet_text,
        "signed_token": token
    })

    print(f"\n{result}")

    print("\n3. Simulating an Attack (Modified Content)...")
    result_attack = publish_tweet.invoke({
        "content": "I hate this brand!", # Malicious content
        "signed_token": token        # Reusing the old valid token
    })
    print(f"{result_attack}")
