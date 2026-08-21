"""
Core device / phone scrambler.
Hybrid: AES-256-GCM (NIST standard) + chaotic XOR layer (real chaos crypto).
Generic key handling. No hard-coded personal secrets.
Provides encrypt, decrypt, scramble for phones and device data.
"""

from __future__ import annotations

import os
import base64
import hashlib
from typing import Tuple, Optional

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    _HAS_CRYPTO = True
except Exception:  # pragma: no cover
    _HAS_CRYPTO = False
    AESGCM = None  # type: ignore

from . import chaotic



def _derive_key(secret: Optional[str] = None, use_keyring: bool = False) -> bytes:
    """
    Hardened key derivation.
    - Prefers OS keyring if use_keyring=True.
    - Tries Argon2id if argon2-cffi installed (recommended for prod).
    - Falls back to PBKDF2-HMAC-SHA256 with high iterations.
    - AES-256-GCM is the crypto boundary; this is for key stretching only.
    """
    if secret is None:
        if use_keyring:
            try:
                import keyring
                secret = keyring.get_password("alien-tech-scrambler", "default") or ""
            except:
                pass
        if not secret:
            secret = os.environ.get("SCRAMBLER_KEY", "DEMO-REPLACE-WITH-SECURE-32BYTE-KEY-OR-ENV!!")

    try:
        from argon2.low_level import Type, hash_secret_raw

        # Deterministic KDF: fixed salt + raw hash so encrypt() and decrypt()
        # always derive the SAME key. PasswordHasher().hash() salts randomly
        # per call and must never be used for key derivation.
        salt = b"alien-tech-fixd"  # exactly 16 bytes
        key = hash_secret_raw(
            secret.encode("utf-8"),
            salt=salt,
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            type=Type.ID,
        )
        return key
    except ImportError:
        pass

    # Fallback PBKDF2
    import hashlib
    salt = b"alien-tech-fixed-salt-do-not-use-in-prod"
    key = hashlib.pbkdf2_hmac("sha256", secret.encode(), salt, 600000, dklen=32)
    return key
    if secret is None:
        secret = os.environ.get("SCRAMBLER_KEY", "DEMO-REPLACE-WITH-SECURE-32BYTE-KEY-OR-ENV!!")
    # Hash to exactly 32 bytes
    return hashlib.sha256(secret.encode("utf-8")).digest()


def encrypt(plaintext: str, secret: Optional[str] = None) -> Tuple[bytes, bytes, bytes]:
    """
    Encrypt using AES-256-GCM.
    Returns (ciphertext, nonce, tag).
    """
    if not _HAS_CRYPTO:
        raise RuntimeError("cryptography library not installed; pip install -r requirements.txt")

    key = _derive_key(secret)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    tag_len = 16
    ciphertext_only = ct[:-tag_len]
    tag = ct[-tag_len:]
    return ciphertext_only, nonce, tag


def decrypt(ciphertext: bytes, nonce: bytes, tag: bytes, secret: Optional[str] = None) -> str:
    """
    Decrypt. Raises on auth fail.
    """
    if not _HAS_CRYPTO:
        raise RuntimeError("cryptography library not installed; pip install -r requirements.txt")

    key = _derive_key(secret)
    aesgcm = AESGCM(key)
    full = ciphertext + tag
    pt = aesgcm.decrypt(nonce, full, None)
    return pt.decode("utf-8")


def hybrid_scramble(plaintext: str, secret: Optional[str] = None, chaos_seed: float = 0.42) -> str:
    """
    Hybrid alien-tech: AES-GCM then XOR chaotic layer.
    Returns base64 package.
    """
    ct, nonce, tag = encrypt(plaintext, secret)
    # Apply chaotic on the ct for extra layer
    chaotic_layer = chaotic.xor_scramble(ct, chaos_seed)
    package = base64.urlsafe_b64encode(nonce + chaotic_layer + tag).decode("ascii")
    return package


def hybrid_unscramble(token: str, secret: Optional[str] = None, chaos_seed: float = 0.42) -> str:
    data = base64.urlsafe_b64decode(token.encode("ascii"))
    nonce = data[:12]
    tag = data[-16:]
    chaotic_ct = data[12:-16]
    ct = chaotic.xor_unscramble(chaotic_ct, chaos_seed)
    return decrypt(ct, nonce, tag, secret)


# Back compat + phone specific
def scramble_phone(phone: str, secret: Optional[str] = None) -> str:
    """Encrypt phone with hybrid."""
    return hybrid_scramble(phone, secret)


def unscramble_phone(token: str, secret: Optional[str] = None) -> str:
    return hybrid_unscramble(token, secret)


if __name__ == "__main__":  # pragma: no cover
    test = "555-123-4567"
    enc = scramble_phone(test)
    print(f"Hybrid Encrypted: {enc}")
    print(f"Decrypted: {unscramble_phone(enc)}")
    print("Core scrambler operational.")


def multi_mode_scramble(plaintext: str, secret: Optional[str] = None, modes: list = None) -> str:
    """Enhanced: multi-layer alien-tech scramble. Modes: aes, chaotic, lattice, dp.
    Default: full hybrid stack for maximum uniqueness and resilience.
    Generic key handling throughout.
    """
    if modes is None:
        modes = ["aes", "chaotic", "lattice"]
    result = plaintext
    if "aes" in modes:
        ct, nonce, tag = encrypt(result, secret)
        result = base64.urlsafe_b64encode(ct + nonce + tag).decode()
    if "chaotic" in modes:
        result = hybrid_scramble(result, secret)
    if "lattice" in modes:
        # Lattice on encoded
        from .lattice import scramble_lattice
        vec = [ord(c) % 256 for c in result[:32]]
        scrambled = scramble_lattice(vec)
        result = result + "|" + "".join(map(str, scrambled))
    return result
