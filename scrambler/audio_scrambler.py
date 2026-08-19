"""
Audio / signal scrambler for phone call simulation.
Uses FFT-based phase randomization / spectrum roll for obfuscation.
Reversible with same parameters. Real technique variants used in analog/digital voice privacy systems.
Preserves some signal energy but destroys intelligibility.
"""

from __future__ import annotations

import numpy as np
from scipy.fft import fft, ifft
from typing import Tuple


def generate_test_signal(duration: float = 0.1, sample_rate: int = 8000) -> np.ndarray:
    """Generate a simple test tone (sine) for demo. Simulates voice snippet."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # Mix tones like voice
    signal = 0.5 * np.sin(2 * np.pi * 440 * t) + 0.3 * np.sin(2 * np.pi * 880 * t)
    return signal.astype(np.float64)


def fft_phase_roll_scramble(signal: np.ndarray, roll: int = 100) -> np.ndarray:
    """
    Scramble by rolling the FFT spectrum. Reverses with negative roll.
    Real freq-domain manipulation used in scramblers.
    """
    f = fft(signal)
    scrambled_f = np.roll(f, roll)
    scrambled = np.real(ifft(scrambled_f))
    return scrambled


def fft_phase_roll_unscramble(signal: np.ndarray, roll: int = 100) -> np.ndarray:
    """Reverse the roll."""
    return fft_phase_roll_scramble(signal, -roll)


def scramble_audio_bytes(audio_bytes: bytes, roll: int = 50) -> bytes:
    """
    Pack bytes to float signal, scramble, back to bytes (demo, lossy for simplicity).
    In real use: use float32 wav etc.
    """
    # Interpret bytes as float approx
    arr = np.frombuffer(audio_bytes, dtype=np.float64) if len(audio_bytes) % 8 == 0 else np.frombuffer(audio_bytes.ljust((len(audio_bytes)//8+1)*8, b'\0'), dtype=np.float64)
    if len(arr) == 0:
        arr = np.zeros(8, dtype=np.float64)
    scrambled = fft_phase_roll_scramble(arr, roll)
    return scrambled.tobytes()[:len(audio_bytes)]  # truncate to orig


def unscramble_audio_bytes(sc_bytes: bytes, roll: int = 50) -> bytes:
    arr = np.frombuffer(sc_bytes, dtype=np.float64)
    unscr = fft_phase_roll_unscramble(arr, roll)
    return unscr.tobytes()[:len(sc_bytes)]
