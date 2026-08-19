# Security Notes for alien-tech-scrambler

This is a privacy and obfuscation toolkit. It combines established methods for data scrambling.

## Cryptographic Boundary
- Primary security: AES-256-GCM (authenticated encryption).
- Chaotic keystream, lattice noise, FFT, and differential privacy are additional obfuscation and perturbation layers.
- Warning: 1D chaotic maps alone are not cryptographically secure against phase-space attacks. They are layered on top of AES here.

## Audio Scrambling
- FFT phase roll provides reversible frequency-domain obfuscation.
- Note: Modern ML models (e.g. neural vocoders) may partially reconstruct formants. For stronger protection, combine with other methods.

## Key Handling (Current)
- Uses simple hash derivation from secret or SCRAMBLER_KEY env.
- Recommendation: In real use, integrate Argon2id for key derivation and platform key stores (macOS Keychain, etc.).

## Usage Guidance
- Suitable for prototypes and internal tools.
- Run the 1M+ simulation suite and tests before relying on any component.
- Not a substitute for proper encryption libraries or audited systems.

## Reporting Issues
Use standard channels for the repository.
