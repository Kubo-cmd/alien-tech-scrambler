"""
Chaotic scrambler using logistic map.
Legitimate real technique from chaos-based cryptography literature.
Deterministic keystream for XOR layer on top of symmetric crypto.
"""

from __future__ import annotations

import numpy as np
from typing import List


def logistic_map_keystream(length: int, seed: float = 0.5, r: float = 4.0) -> List[int]:
    """
    Generate keystream bytes from logistic map (r=4 is fully chaotic).
    Seed in (0,1). Returns list of int 0-255 for XOR.
    Real primitive used in lightweight encryption research.
    """
    if not 0 < seed < 1:
        seed = 0.5
    x = seed
    keystream = []
    for _ in range(length):
        x = r * x * (1 - x)
        # Map to byte
        byte = int(x * 256) % 256
        keystream.append(byte)
    return keystream


def xor_scramble(data: bytes, seed: float = 0.5) -> bytes:
    """
    XOR data with logistic map keystream. Reversible with same seed.
    """
    ks = logistic_map_keystream(len(data), seed)
    return bytes(d ^ k for d, k in zip(data, ks))


def xor_unscramble(data: bytes, seed: float = 0.5) -> bytes:
    """Same as scramble for XOR."""
    return xor_scramble(data, seed)
