"""
Real tests for alien-tech-scrambler.
Executes all core functions, roundtrips, verifies no regression.
Run: PYTHONPATH=. python3 tests/test_scrambler.py
"""

import sys
sys.path.insert(0, '.')
import unittest
import json
import numpy as np

from scrambler.scrambler import scramble_phone, unscramble_phone, hybrid_scramble, hybrid_unscramble
from scrambler.chaotic import xor_scramble, xor_unscramble
from scrambler.diff_privacy import add_laplace_noise, privatize_list
from scrambler.audio_scrambler import generate_test_signal, fft_phase_roll_scramble, fft_phase_roll_unscramble
from scrambler.device import generate_base_device, scramble_device_profile
from scrambler.lattice import generate_lattice_vector, add_lwe_noise, scramble_lattice, unscramble_lattice
from leakage.scanner import scan_text


class TestScrambler(unittest.TestCase):
    def test_phone_roundtrip(self):
        phone = "555-123-4567"
        enc = scramble_phone(phone)
        dec = unscramble_phone(enc)
        self.assertEqual(dec, phone)
        self.assertNotEqual(enc, phone)
        print("Phone hybrid roundtrip: PASS")

    def test_hybrid_scramble(self):
        text = "device-xyz-001"
        enc = hybrid_scramble(text)
        dec = hybrid_unscramble(enc)
        self.assertEqual(dec, text)

    def test_chaotic_xor(self):
        data = b"secret-device-data-12345"
        scr = xor_scramble(data, 0.7)
        un = xor_unscramble(scr, 0.7)
        self.assertEqual(un, data)
        self.assertNotEqual(scr, data)

    def test_dp_noise(self):
        vals = [42.0, 100.0, 3.14]
        noisy = privatize_list(vals, epsilon=1.0, seed=42)
        self.assertEqual(len(noisy), len(vals))
        self.assertNotEqual(noisy[0], vals[0])

    def test_audio_scramble_roundtrip(self):
        sig = generate_test_signal(0.02)
        scr = fft_phase_roll_scramble(sig, 32)
        un = fft_phase_roll_unscramble(scr, 32)
        self.assertEqual(len(un), len(sig))
        corr = np.corrcoef(sig, un)[0, 1]
        self.assertGreater(corr, 0.7)
        print(f"Audio FFT roundtrip corr: {corr:.4f} PASS")

    def test_device_scramble(self):
        base = generate_base_device("test-seed-xyz")
        scr = scramble_device_profile(base, epsilon=0.1)
        self.assertIn("device_id", scr)
        self.assertIn("_scramble_meta", scr)
        self.assertNotEqual(scr["battery_percent"], base["battery_percent"])
        self.assertTrue(len(scr["phone"]) > 20)
        print("Device profile DP+encrypt: PASS")

    def test_lattice_scramble(self):
        vec = generate_lattice_vector(dim=6, seed=99)
        scr, err = scramble_lattice(vec, error_bound=3, seed=99)
        un = unscramble_lattice(scr, err)
        self.assertTrue(np.array_equal(un, vec))
        self.assertFalse(np.array_equal(scr, vec))
        print("Lattice LWE roundtrip: PASS")

    def test_leakage_scanner(self):
        txt = "phone: 555-123-4567 email: leak@ex.com key: AKIA1234567890ABCDEF"
        findings = scan_text(txt)
        types = [f["type"] for f in findings]
        self.assertIn("phone", types)
        self.assertIn("email", types)
        self.assertIn("aws_access_key", types)
        self.assertTrue(any("entropy" in f for f in findings))
        print("Leakage + entropy scan: PASS")

    def test_full_integration(self):
        dev = generate_base_device()
        scr_dev = scramble_device_profile(dev)
        phone_enc = scramble_phone(dev["phone"])
        dec_phone = unscramble_phone(phone_enc)
        self.assertEqual(dec_phone, dev["phone"])
        findings = scan_text(json.dumps(scr_dev))
        plain_phones = [f for f in findings if f.get("type") == "phone"]
        self.assertEqual(len(plain_phones), 0)
        # lattice
        v = generate_lattice_vector(4)
        s, e = scramble_lattice(v)
        self.assertTrue(np.array_equal(unscramble_lattice(s, e), v))
        print("Full integration no-plain-leak + lattice: PASS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
