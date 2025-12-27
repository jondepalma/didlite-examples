"""
Agent identity management and message storage.
"""
import uuid
import time
from typing import Dict, List, Optional
from didlite import AgentIdentity, create_jws, verify_jws
from nonce_tracker import nonce_tracker


class AgentManager:
    """Manages agent identities and message history."""

    def __init__(self):
        """Initialize agent manager with three agents: Bob, Alice, and Chris."""
        self.agents: Dict[str, AgentIdentity] = {}
        self.message_history: Dict[str, Dict[str, List]] = {}
        self.nonce_enabled = False  # Toggle for nonce protection (educational)

        # Create identities for Bob (good), Alice (good), and Chris (bad)
        self._create_agent("bob")
        self._create_agent("alice")
        self._create_agent("chris")

    def _create_agent(self, name: str):
        """Create an agent with a persistent identity."""
        # Use a deterministic seed based on name for demo purposes
        # In production, these would be loaded from secure storage
        seed = name.encode().ljust(32, b'\x00')  # Simple deterministic seed
        self.agents[name] = AgentIdentity(seed=seed)
        self.message_history[name] = {"sent": [], "received": []}

    def get_agent(self, name: str) -> Optional[AgentIdentity]:
        """Get agent identity by name."""
        return self.agents.get(name.lower())

    def get_did(self, name: str) -> Optional[str]:
        """Get agent's DID by name."""
        agent = self.get_agent(name)
        return agent.did if agent else None

    def list_agents(self) -> List[str]:
        """List all agent names."""
        return list(self.agents.keys())

    def send_message(self, sender: str, recipient: str, content: str, expires_in: int = 5) -> dict:
        """
        Create and sign a message from sender to recipient.

        Args:
            sender: Sender agent name
            recipient: Recipient agent name
            content: Message content
            expires_in: Token expiration time in seconds (default: 5 seconds)

        Returns:
            Dictionary containing the signed token and metadata
        """
        sender_agent = self.get_agent(sender)
        if not sender_agent:
            raise ValueError(f"Agent '{sender}' not found")

        if recipient.lower() not in self.agents:
            raise ValueError(f"Recipient agent '{recipient}' not found")

        # Create message payload
        message_id = str(uuid.uuid4())
        timestamp = int(time.time())

        payload = {
            "message_id": message_id,
            "sender": sender.lower(),
            "recipient": recipient.lower(),
            "content": content,
            "timestamp": timestamp
        }

        # Add nonce if enabled (application-layer replay protection)
        if self.nonce_enabled:
            payload["nonce"] = nonce_tracker.generate_nonce()

        # Sign the message
        token = create_jws(sender_agent, payload, expires_in=expires_in)

        # Record in history
        message_record = {
            "message_id": message_id,
            "recipient": recipient.lower(),
            "content": content,
            "timestamp": timestamp,
            "token": token
        }
        self.message_history[sender.lower()]["sent"].append(message_record)

        return {
            "token": token,
            "sender_did": sender_agent.did,
            "message_id": message_id,
            "timestamp": timestamp
        }

    def verify_message(self, token: str) -> dict:
        """
        Verify a signed message.

        Args:
            token: JWS token to verify

        Returns:
            Dictionary containing verification result
        """
        try:
            # Verify the signature and extract payload
            payload = verify_jws(token)

            # Check nonce if enabled (application-layer replay protection)
            if self.nonce_enabled:
                nonce = payload.get('nonce')
                if not nonce:
                    return {
                        "valid": False,
                        "payload": None,
                        "sender_did": None,
                        "error": "Message missing nonce (required when nonce protection is enabled)"
                    }

                if not nonce_tracker.is_valid(nonce):
                    return {
                        "valid": False,
                        "payload": None,
                        "sender_did": None,
                        "error": "Replay attack detected! This nonce was already used."
                    }

            # Extract sender DID from token header
            import base64
            import json
            header_segment = token.split('.')[0]
            padding_needed = (4 - len(header_segment) % 4) % 4
            padded_header = header_segment + ('=' * padding_needed)
            header_data = base64.urlsafe_b64decode(padded_header)
            header = json.loads(header_data)
            sender_did = header.get('kid')

            # Record in recipient's history if recipient exists
            recipient = payload.get('recipient')
            if recipient and recipient in self.message_history:
                message_record = {
                    "message_id": payload.get('message_id'),
                    "sender": payload.get('sender'),
                    "content": payload.get('content'),
                    "timestamp": payload.get('timestamp'),
                    "verified_at": int(time.time()),
                    "sender_did": sender_did
                }
                self.message_history[recipient]["received"].append(message_record)

            return {
                "valid": True,
                "payload": payload,
                "sender_did": sender_did,
                "error": None
            }
        except Exception as e:
            return {
                "valid": False,
                "payload": None,
                "sender_did": None,
                "error": str(e)
            }

    def get_message_history(self, agent_name: str) -> dict:
        """Get message history for an agent."""
        if agent_name.lower() not in self.message_history:
            raise ValueError(f"Agent '{agent_name}' not found")

        return {
            "agent": agent_name.lower(),
            "sent": self.message_history[agent_name.lower()]["sent"],
            "received": self.message_history[agent_name.lower()]["received"]
        }

    def execute_attack(self, attacker: str, attack_type: str, target_agent: str = None, stolen_token: str = None) -> dict:
        """
        Execute an attack scenario (for demonstration purposes).

        Args:
            attacker: Name of the attacking agent (usually 'chris')
            attack_type: Type of attack to execute
            target_agent: Target agent for the attack (optional)
            stolen_token: Stolen token for token_theft attack (optional)

        Returns:
            Dictionary containing attack result
        """
        if attacker.lower() != "chris":
            return {
                "success": False,
                "error": "Only 'chris' can execute attacks in this simulation"
            }

        if attack_type == "replay":
            # Replay attack: Resend an old message
            kwargs = {}
            if target_agent:
                kwargs['target_agent'] = target_agent
            return self._attack_replay(**kwargs)
        elif attack_type == "forge":
            # Forgery attempt: Try to create a message as another agent
            kwargs = {}
            if target_agent:
                kwargs['target_agent'] = target_agent
            return self._attack_forge(**kwargs)
        elif attack_type == "intercept":
            # Man-in-the-middle: Intercept and try to modify
            return self._attack_intercept()
        elif attack_type == "token_theft":
            # Token theft: Try to reuse a stolen token
            kwargs = {}
            if stolen_token:
                kwargs['stolen_token'] = stolen_token
            return self._attack_token_theft(**kwargs)
        elif attack_type == "no_private_key":
            # Demonstrate that public key alone cannot create signatures
            return self._attack_no_private_key()
        else:
            return {
                "success": False,
                "error": f"Unknown attack type: {attack_type}"
            }

    def _attack_replay(self, target_agent: str = "alice") -> dict:
        """Replay attack: Resend an old valid message."""
        # Get Bob's last sent message
        bob_sent = self.message_history["bob"]["sent"]
        if not bob_sent:
            return {
                "success": False,
                "error": "No messages to replay",
                "attack_type": "replay"
            }

        # Take the last message Bob sent
        old_message = bob_sent[-1]
        old_token = old_message["token"]

        # Chris tries to replay it
        result = self.verify_message(old_token)

        return {
            "success": result["valid"],
            "attack_type": "replay",
            "description": "Replayed Bob's old message",
            "token": old_token,
            "verification_result": result,
            "note": "This attack succeeds if the token hasn't expired. Defense: use short expiration times and nonce tracking."
        }

    def _attack_forge(self, impersonate: str = "bob", target_agent: str = "alice") -> dict:
        """Forgery attack: Try to create a message impersonating another agent."""
        # Chris tries to create a message claiming to be Bob
        chris_agent = self.get_agent("chris")

        payload = {
            "message_id": str(uuid.uuid4()),
            "sender": impersonate.lower(),  # Chris claims to be Bob
            "recipient": target_agent.lower(),
            "content": "I am definitely Bob, trust me!",
            "timestamp": int(time.time())
        }

        # Chris signs with his own key
        forged_token = create_jws(chris_agent, payload, expires_in=5)

        # Try to verify (will succeed, but DID won't match Bob's)
        result = self.verify_message(forged_token)

        # Check if the DID matches Bob's
        bob_did = self.get_did("bob")
        did_matches = result.get("sender_did") == bob_did

        return {
            "success": False,  # Attack fails because DID doesn't match
            "attack_type": "forge",
            "description": f"Chris tried to impersonate {impersonate}",
            "forged_token": forged_token,
            "chris_did": chris_agent.did,
            "bob_did": bob_did,
            "did_matches": did_matches,
            "verification_result": result,
            "note": "This attack fails because the DID in the token reveals Chris as the signer, not Bob."
        }

    def _attack_intercept(self, **kwargs) -> dict:
        """Intercept attack: Try to modify a message in transit."""
        # Get Bob's last message
        bob_sent = self.message_history["bob"]["sent"]
        if not bob_sent:
            return {
                "success": False,
                "error": "No messages to intercept",
                "attack_type": "intercept"
            }

        original_token = bob_sent[-1]["token"]

        # Chris tries to modify the payload
        import base64
        import json

        segments = original_token.split('.')
        header_segment, payload_segment, signature_segment = segments

        # Decode and modify payload
        padding_needed = (4 - len(payload_segment) % 4) % 4
        padded_payload = payload_segment + ('=' * padding_needed)
        payload_data = base64.urlsafe_b64decode(padded_payload)
        payload = json.loads(payload_data)

        # Modify the content
        payload["content"] = "MODIFIED BY CHRIS"

        # Re-encode the modified payload
        modified_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()

        # Create tampered token (with original signature)
        tampered_token = f"{header_segment}.{modified_payload}.{signature_segment}"

        # Try to verify the tampered token
        result = self.verify_message(tampered_token)

        return {
            "success": False,  # Attack fails because signature won't match
            "attack_type": "intercept",
            "description": "Chris intercepted and modified Bob's message",
            "original_token": original_token,
            "tampered_token": tampered_token,
            "verification_result": result,
            "note": "This attack fails because modifying the payload invalidates the signature."
        }

    def _attack_token_theft(self, stolen_token: str = None) -> dict:
        """Token theft: Try to reuse a stolen valid token."""
        if not stolen_token:
            # Steal Alice's last sent message
            alice_sent = self.message_history["alice"]["sent"]
            if not alice_sent:
                return {
                    "success": False,
                    "error": "No tokens to steal",
                    "attack_type": "token_theft"
                }
            stolen_token = alice_sent[-1]["token"]

        # Chris tries to use Alice's token
        result = self.verify_message(stolen_token)

        # The token will verify successfully, but the DID reveals it's from Alice
        alice_did = self.get_did("alice")

        return {
            "success": result["valid"],  # Token is valid
            "attack_type": "token_theft",
            "description": "Chris stole and reused Alice's token",
            "stolen_token": stolen_token,
            "alice_did": alice_did,
            "verification_result": result,
            "note": "The token is valid, but the DID proves it's from Alice, not Chris. Defense: implement audience claims and nonce tracking."
        }

    def _attack_no_private_key(self) -> dict:
        """Demonstrate that knowing the public key (DID) is not enough to create signatures."""
        bob_did = self.get_did("bob")

        return {
            "success": False,
            "attack_type": "no_private_key",
            "description": "Chris knows Bob's public DID but cannot create signatures without the private key",
            "bob_did": bob_did,
            "can_sign": False,
            "note": "Public key cryptography is asymmetric: the public key can only VERIFY signatures, not CREATE them. Only the holder of the private key can sign messages. This is the foundation of digital identity - Chris cannot impersonate Bob even with full knowledge of Bob's public information."
        }

    def enable_nonce_tracking(self):
        """Enable nonce-based replay protection."""
        self.nonce_enabled = True
        nonce_tracker.clear_all()  # Clear old nonces when enabling

    def disable_nonce_tracking(self):
        """Disable nonce-based replay protection."""
        self.nonce_enabled = False

    def get_nonce_stats(self) -> dict:
        """Get statistics about nonce tracking."""
        stats = nonce_tracker.get_stats()
        stats["nonce_enabled"] = self.nonce_enabled
        return stats


# Global agent manager instance
agent_manager = AgentManager()
