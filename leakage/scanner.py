"""
Leakage scanner for detecting sensitive information in text.
Enhanced with Shannon entropy analysis (using numpy) for high-entropy secrets.
Real technique for secret detection in code audits.
"""

from __future__ import annotations

import re
import math
from typing import List, Dict, Tuple

import numpy as np

# Patterns for common leakage (expanded)
PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")),
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("ipv4", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    ("bearer_token", re.compile(r"(?i)Bearer\s+([A-Za-z0-9\-._~+/]+=* )")),
    ("phone", re.compile(r"\b(?:[\+]?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")),
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
]


def _redact(value: str) -> str:
    if len(value) <= 8:
        return value
    return value[:4] + "…" + value[-2:]


def shannon_entropy(data: str) -> float:
    """Calculate Shannon entropy. High (>4.5) often indicates random secrets."""
    if not data:
        return 0.0
    probs = [float(data.count(c)) / len(data) for c in set(data)]
    return -sum(p * math.log(p, 2) for p in probs if p > 0)


def scan_text(text: str, entropy_threshold: float = 4.5) -> List[Dict[str, str]]:
    """
    Scan text for leakage patterns + flag high entropy strings.
    Returns list of {'type': , 'match': redacted, 'entropy': optional}
    """
    findings: List[Dict[str, str]] = []
    for name, pattern in PATTERNS:
        for match in pattern.findall(text):
            if isinstance(match, tuple):
                token = next((g for g in match if g), None)
            else:
                token = match
            if token:
                ent = round(shannon_entropy(token), 2)
                entry = {
                    "type": name,
                    "match": _redact(str(token)),
                    "entropy": str(ent)
                }
                if ent > entropy_threshold:
                    entry["note"] = "high-entropy (possible secret)"
                findings.append(entry)

    # Additional: scan for long high-entropy substrings (e.g. 20+ chars base64-like)
    for m in re.finditer(r"[A-Za-z0-9+/=]{20,}", text):
        tok = m.group(0)
        ent = round(shannon_entropy(tok), 2)
        if ent > entropy_threshold:
            findings.append({
                "type": "high_entropy_string",
                "match": _redact(tok),
                "entropy": str(ent),
                "note": "high-entropy substring"
            })

    return findings


if __name__ == "__main__":  # pragma: no cover
    test = """
    My phone number is 555-123-4567.
    Email: test@example.com
    AWS Key: AKIAEXAMPLEKEY1234
    OpenAI Key: sk-1234567890abcdef1234567890
    Bearer Token: ya29.a0AfH6SMB...
    """
    results = scan_text(test)
    for r in results:
        print(f"[{r['type']}] {r['match']} entropy={r.get('entropy')} {r.get('note','')}")
