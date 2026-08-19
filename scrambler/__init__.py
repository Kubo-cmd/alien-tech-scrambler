"""
Privacy toolkit for phone and device data obfuscation.
Exports core hybrid scrambler, chaotic, dp, audio, device, lattice modules.
All techniques are real, published privacy/cryptography methods.
Lattice adds post-quantum LWE-inspired uniqueness.
"""

from .scrambler import (
    encrypt,
    decrypt,
    hybrid_scramble,
    hybrid_unscramble,
    scramble_phone,
    unscramble_phone,
)
from .chaotic import xor_scramble, xor_unscramble, logistic_map_keystream
from .diff_privacy import add_laplace_noise, privatize_device_field, privatize_list
from .audio_scrambler import (
    generate_test_signal,
    fft_phase_roll_scramble,
    fft_phase_roll_unscramble,
    scramble_audio_bytes,
)
from .device import generate_base_device, scramble_device_profile, unscrambled_device_summary
from .lattice import generate_lattice_vector, add_lwe_noise, scramble_lattice, unscramble_lattice

__all__ = [
    "encrypt", "decrypt", "hybrid_scramble", "hybrid_unscramble",
    "scramble_phone", "unscramble_phone",
    "xor_scramble", "xor_unscramble", "logistic_map_keystream",
    "add_laplace_noise", "privatize_device_field", "privatize_list",
    "generate_test_signal", "fft_phase_roll_scramble", "fft_phase_roll_unscramble", "scramble_audio_bytes",
    "generate_base_device", "scramble_device_profile", "unscrambled_device_summary",
    "generate_lattice_vector", "add_lwe_noise", "scramble_lattice", "unscramble_lattice",
]
