"""
Lattice-inspired scrambler module.
Simple implementation of Learning With Errors (LWE) style noise addition.
Real post-quantum crypto foundation (Regev 2005+). Used here for device vector obfuscation.
Adds small integer noise to numeric vectors for "alien" uniqueness.
"""

from __future__ import annotations

import numpy as np
from typing import List, Tuple


def generate_lattice_vector(dim: int = 8, seed: int | None = None) -> np.ndarray:
    """Generate a base vector (simulated device feature vector)."""
    if seed is not None:
        np.random.seed(seed)
    return np.random.randint(0, 100, size=dim).astype(np.int64)


def add_lwe_noise(vec: np.ndarray, error_bound: int = 5, seed: int | None = None) -> np.ndarray:
    """
    Add small error vector (LWE style).
    error_bound: small noise range.
    """
    if seed is not None:
        np.random.seed(seed)
    error = np.random.randint(-error_bound, error_bound + 1, size=vec.shape)
    return vec + error


def scramble_lattice(vec: np.ndarray, error_bound: int = 5, seed: int | None = None) -> Tuple[np.ndarray, np.ndarray]:
    """Return (scrambled, error) for reversibility demo."""
    scrambled = add_lwe_noise(vec, error_bound, seed)
    error = scrambled - vec
    return scrambled, error


def unscramble_lattice(scrambled: np.ndarray, error: np.ndarray) -> np.ndarray:
    return scrambled - error
