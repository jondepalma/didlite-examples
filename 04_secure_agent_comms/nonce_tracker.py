"""
Simple file-based nonce tracker for educational purposes.

⚠️  DISCLAIMER: This is a simplified demonstration using a file as a database.
    In production, you should use:
    - A proper database (PostgreSQL, MongoDB, etc.)
    - Redis for distributed systems
    - Atomic operations to prevent race conditions
    - Proper error handling and logging

This implementation is intentionally simple to illustrate the concept of
nonce tracking for replay attack prevention.
"""

import json
import os
import time
import secrets
from typing import Optional


class SimpleNonceTracker:
    """
    Educational file-based nonce tracker.

    Stores used nonces in a JSON file with expiration timestamps.
    Automatically cleans up expired nonces to prevent unbounded growth.
    """

    def __init__(self, nonce_file: str = "nonces.json", expiry_seconds: int = 300):
        """
        Initialize the nonce tracker.

        Args:
            nonce_file: Path to JSON file for storing nonces
            expiry_seconds: How long to remember nonces (default: 5 minutes)
        """
        self.nonce_file = nonce_file
        self.expiry_seconds = expiry_seconds
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create the nonce file if it doesn't exist."""
        if not os.path.exists(self.nonce_file):
            self._save_nonces({})

    def _load_nonces(self) -> dict:
        """Load nonces from file."""
        try:
            with open(self.nonce_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_nonces(self, nonces: dict):
        """Save nonces to file."""
        with open(self.nonce_file, 'w') as f:
            json.dump(nonces, f, indent=2)

    def _cleanup_expired(self, nonces: dict, current_time: float) -> dict:
        """Remove expired nonces from the dictionary."""
        return {
            nonce: expiry
            for nonce, expiry in nonces.items()
            if expiry > current_time
        }

    def generate_nonce(self) -> str:
        """
        Generate a cryptographically secure random nonce.

        Returns:
            A URL-safe base64-encoded random string
        """
        return secrets.token_urlsafe(32)

    def is_valid(self, nonce: str) -> bool:
        """
        Check if a nonce is valid (not previously used).

        Args:
            nonce: The nonce to check

        Returns:
            True if nonce is valid (first use), False if it's a replay
        """
        current_time = time.time()

        # Load existing nonces
        nonces = self._load_nonces()

        # Clean up expired nonces
        nonces = self._cleanup_expired(nonces, current_time)

        # Check if nonce was already used
        if nonce in nonces:
            return False  # Replay detected!

        # Mark nonce as used with expiration timestamp
        nonces[nonce] = current_time + self.expiry_seconds

        # Save updated nonces
        self._save_nonces(nonces)

        return True

    def get_stats(self) -> dict:
        """
        Get statistics about stored nonces.

        Returns:
            Dictionary with nonce statistics
        """
        current_time = time.time()
        nonces = self._load_nonces()

        total = len(nonces)
        expired = sum(1 for expiry in nonces.values() if expiry <= current_time)
        active = total - expired

        return {
            "total_nonces": total,
            "active_nonces": active,
            "expired_nonces": expired,
            "file_path": self.nonce_file
        }

    def clear_all(self):
        """Clear all nonces (useful for demos/testing)."""
        self._save_nonces({})


# Global nonce tracker instance
nonce_tracker = SimpleNonceTracker(expiry_seconds=300)
