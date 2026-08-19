"""
Device fingerprint scrambler.
Combines differential privacy on numeric fields + encryption of profile.
Generates realistic but obfuscated device profiles.
Real techniques: DP + symmetric encryption for privacy preserving device attestation or anti-fingerprint.
"""

from __future__ import annotations

import json
import hashlib
from typing import Dict, Any

from .diff_privacy import privatize_device_field
from .scrambler import encrypt, scramble_phone  # reuse core


def generate_base_device(seed: str = "demo-device") -> Dict[str, Any]:
    """Generate a deterministic base device profile from seed (fake but consistent)."""
    h = hashlib.sha256(seed.encode()).hexdigest()
    return {
        "device_id": h[:16],
        "model": "GenericMobile-" + h[0:4].upper(),
        "os_version": f"16.{int(h[4:6], 16) % 10}",
        "screen_width": 1080 + (int(h[6:8], 16) % 200),
        "screen_height": 1920 + (int(h[8:10], 16) % 300),
        "battery_percent": 50 + (int(h[10:12], 16) % 50),
        "lat": 37.0 + (int(h[12:14], 16) % 10) / 10.0,
        "lon": -122.0 + (int(h[14:16], 16) % 10) / 10.0,
        "phone": "555-" + str(int(h[16:19], 16) % 1000).zfill(3) + "-" + str(int(h[19:23], 16) % 10000).zfill(4),
    }


def scramble_device_profile(profile: Dict[str, Any], epsilon: float = 0.5) -> Dict[str, Any]:
    """
    Apply DP to numeric fields, encrypt sensitive strings.
    Returns scrambled profile dict (for storage/transmission).
    """
    scrambled = profile.copy()
    for key, val in profile.items():
        if isinstance(val, (int, float)):
            scrambled[key] = round(privatize_device_field(key, val, epsilon), 4)
        elif key in ("phone", "device_id") and isinstance(val, str):
            # Encrypt phone/device id
            try:
                enc = scramble_phone(val)
                scrambled[key] = enc
            except Exception:
                scrambled[key] = "SCRAMBLED"
    # Add meta
    scrambled["_scramble_meta"] = {"epsilon": epsilon, "method": "dp+hybrid-encrypt"}
    return scrambled


def unscrambled_device_summary(scrambled: Dict[str, Any]) -> Dict[str, Any]:
    """For demo: show structure without full decrypt."""
    summary = {k: v for k, v in scrambled.items() if not k.startswith("_")}
    summary["_note"] = "full decrypt requires keys; this is redacted view"
    return summary
