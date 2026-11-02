"""Verify Discord's Ed25519 signature over timestamp and raw request bytes."""

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey


class InteractionSignatureVerifier:
    """A reusable public-key verifier for outgoing interaction webhooks."""

    def __init__(self, public_key: str):
        try:
            key = bytes.fromhex(public_key)
            if len(key) != 32:
                raise ValueError("public key must contain 32 bytes")
            self._key = VerifyKey(key)
        except (TypeError, ValueError) as error:
            raise ValueError("invalid Discord application public key") from error

    def verify(self, signature: str | None, timestamp: str | None, body: bytes) -> bool:
        if not signature or not timestamp or not isinstance(body, bytes):
            return False
        try:
            signature_bytes = bytes.fromhex(signature)
            if len(signature_bytes) != 64:
                return False
            self._key.verify(timestamp.encode("utf-8") + body, signature_bytes)
        except (ValueError, BadSignatureError, UnicodeEncodeError):
            return False
        return True
