"""Discord HTTP signatures cover the unmodified timestamp and body bytes."""

import pytest
from nacl.signing import SigningKey

from discord.ext.interaction.implementation.signature import InteractionSignatureVerifier


def test_signature_verifier_accepts_valid_raw_body_and_rejects_tampering():
    signing_key = SigningKey.generate()
    verifier = InteractionSignatureVerifier(signing_key.verify_key.encode().hex())
    body = b'{"type":1}'
    timestamp = "1700000000"
    signature = signing_key.sign(timestamp.encode() + body).signature.hex()
    assert verifier.verify(signature, timestamp, body)
    assert not verifier.verify(signature, timestamp, b'{"type":2}')
    assert not verifier.verify(signature, "1700000001", body)
    assert not verifier.verify("bad", timestamp, body)
    assert not verifier.verify(None, timestamp, body)


def test_signature_verifier_rejects_invalid_public_key():
    with pytest.raises(ValueError, match="public key"):
        InteractionSignatureVerifier("not-a-key")
