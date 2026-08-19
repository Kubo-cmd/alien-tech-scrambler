"""
Device scrambler using AES-256-GCM for symmetric encryption.
Provides encrypt and decrypt functions for protecting device identifiers,
phone numbers, or other sensitive strings.
"""

from __future__ import annotations

import os
import base64
from typing import Tuple

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    _HAS_CRYPTO = True
except Exception:  # pragma: no cover
    _HAS_CRYPTO = False
    AESGCM = None  # type: ignore


def _get_key() -> bytes:
    """
    Return a 32‑byte key. In production this should come from a secure vault
    or environment variable. For demo we derive from a fixed secret; replace
    with proper key management.
    """
    # TODO: load from secure source (e.g., OS keychain, Vault, .env)
    secret = b"alien-tech-scrambler-demo-key-32bytes!!"
    # Ensure exactly 32 bytes
    if len(secret) < 32:
        secret = secret.ljust(32, b'\0')
    elif len(secret) > 32:
        secret = secret[:32]
    return secret


def encrypt(plaintext: str) -> Tuple[bytes, bytes, bytes]:
    """
    Encrypt a UTF‑8 string using AES-256-GCM.

    Returns (ciphertext, nonce, tag) where nonce is 12 bytes and tag is 16 bytes.
    If cryptography is not available, raises RuntimeError.
    """
    if not _HAS_CRYPTO:
        raise RuntimeError("cryptography library not installed; install with `pip install cryptography`")

    aesgcm = AESGCM(_get_key())
    nonce = os.urandom(12)  # GCM recommended nonce size
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    # In AESGCM, tag is appended to ciphertext; split for clarity
    # Actually encrypt returns ciphertext||tag
    tag_len = 16
    ciphertext_only = ciphertext[:-tag_len]
    tag = ciphertext[-tag_len:]
    return ciphertext_only, nonce, tag


def decrypt(ciphertext: bytes, nonce: bytes, tag: bytes) -> str:
    """
    Decrypt data produced by encrypt.

    Raises cryptography.exceptions.InvalidTag if authentication fails.
    """
    if not _HAS_CRYPTO:
        raise RuntimeError("cryptography library not installed; install with `pip install cryptography`")

    aesgcm = AESGCM(_get_key())
    # recombine ciphertext and tag
    full = ciphertext + tag
    plaintext_bytes = aesgcm.decrypt(nonce, full, None)
    return plaintext_bytes.decode('utf-8')


def scramble_phone(phone: str) -> str:
    """
    Example usage: encrypt a phone number and return base64url-safe string
   包含 nonce + ciphertext + tag for simplicity.
    """
    ciphertext, nonce, tag = encrypt(phone)
    package = base64.urlsafe_b64encode(nonce + ciphertext + tag).decode('ascii')
    return package


def unscramble_phone(token: str) -> str:
    data = base64.urlsafe_b64decode(token.encode('ascii'))
    nonce = data[:12]
    # Assuming tag is last 16 bytes
    tag = data[-16:]
    ciphertext = data[12:-16]
    return decrypt(ciphertext, nonce, tag)


if __name__ == "__main__":  # pragma: no cover
    # Demo
    test = "555-123-4567"
    enc = scramble_phone(test)
    print(f"Encrypted: {enc}")
    print(f"Decrypted: {unscramble_phone(enc)}")