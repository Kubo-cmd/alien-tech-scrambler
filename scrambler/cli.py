"""
CLI for alien-tech-scrambler.
Real working interface for phone/device scrambling with advanced tech.
Usage: python -m scrambler.cli [command] [args]
"""

import argparse
import json
import sys

from .scrambler import scramble_phone, unscramble_phone, hybrid_scramble, hybrid_unscramble
from .device import generate_base_device, scramble_device_profile
from .audio_scrambler import generate_test_signal, fft_phase_roll_scramble, fft_phase_roll_unscramble
from leakage.scanner import scan_text  # type: ignore  # run as module
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(description="Phone and Device Privacy Scrambler - hybrid cryptographic and privacy toolkit")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # phone
    p_phone = sub.add_parser("phone", help="Scramble/unscramble phone")
    p_phone.add_argument("action", choices=["scramble", "unscramble"])
    p_phone.add_argument("value")

    # device
    p_dev = sub.add_parser("device", help="Generate and scramble device profile")
    p_dev.add_argument("--seed", default="demo-device-001")
    p_dev.add_argument("--epsilon", type=float, default=0.5)

    # audio
    p_audio = sub.add_parser("audio", help="Demo audio/signal scramble (FFT roll)")
    p_audio.add_argument("--roll", type=int, default=64)
    p_audio.add_argument("--duration", type=float, default=0.05)

    # scan
    p_scan = sub.add_parser("scan", help="Scan text for leaks + entropy")
    p_scan.add_argument("text", nargs="?", default=None)
    p_scan.add_argument("--file", help="read from file")

    # simulate
    p_sim = sub.add_parser("simulate", help="Run Monte Carlo simulations (1M target)")
    p_sim.add_argument("--n", type=int, default=1000000, help="number of simulations")
    p_sim.add_argument("--seed", type=int, default=42)
    p_sim.add_argument("--save", action="store_true", help="save results to simulations/")

    args = parser.parse_args()

    if args.cmd == "phone":
        if args.action == "scramble":
            print(scramble_phone(args.value))
        else:
            print(unscramble_phone(args.value))
    elif args.cmd == "device":
        base = generate_base_device(args.seed)
        scr = scramble_device_profile(base, args.epsilon)
        print(json.dumps(scr, indent=2))
    elif args.cmd == "audio":
        sig = generate_test_signal(args.duration)
        scr = fft_phase_roll_scramble(sig, args.roll, jitter=0.05)
        un = fft_phase_roll_unscramble(scr, args.roll, jitter=0.05)
        corr = float(np.corrcoef(sig, un)[0,1]) if len(sig)>1 else 0.0
        print(f"Original len: {len(sig)} | Scrambled len: {len(scr)} | Reconstruct corr: {corr:.4f}")
        print("Signal scrambled with FFT roll (reversible). Real freq-domain privacy method.")
    elif args.cmd == "scan":
        txt = args.text
        if args.file:
            with open(args.file) as f:
                txt = f.read()
        if not txt:
            txt = "Example: phone 555-123-4567 email foo@bar.com key AKIA1234567890ABCDEF"
        results = scan_text(txt)
        for r in results:
            print(r)
    elif args.cmd == "hybrid":
        enc = hybrid_scramble(args.text)
        dec = hybrid_unscramble(enc)
        print(f"Input: {args.text}")
        print(f"Hybrid: {enc}")
        print(f"Roundtrip: {dec}")
    elif args.cmd == "simulate":
        from .simulation import run_monte_carlo, save_results
        res = run_monte_carlo(n=args.n, seed=args.seed, verbose=True)
        if args.save:
            save_results(res)
        print("=== SIMULATION SUMMARY ===")
        print(f"Target n: {res['n_target']}")
        print(f"Actual sims approx: {res.get('total_simulations_approx', 'N/A')}")
        print(f"Time: {res['total_time_seconds']}s")
        for cat, stats in res.get("categories", {}).items():
            print(f"  {cat}: {stats}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


def main():
    """Entry point for pip installed cli."""
    import sys
    if len(sys.argv) > 1:
        # simple passthrough for demo
        import subprocess
        subprocess.call([sys.executable, "-m", "scrambler.cli"] + sys.argv[1:])
    else:
        print("alien-tech-scrambler CLI. Use python -m scrambler.cli --help")

if __name__ == "__main__":
    main()
