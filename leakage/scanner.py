"""
Leakage scanner for detecting sensitive information in text.
"""

from __future__ import annotations

import re
from typing import List, Dict, Tuple

# Patterns for common leakage
PATTERNS: List[Tuple[str, re.Pattern]] = [
    # Private keys
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    # AWS Access Key ID
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    # OpenAI API Key
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    # GitHub Personal Access Token
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    # Google API Key
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}\b")),
    # Slack Token
    ("slack_token", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b")),
    # JWT
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")),
    # Email
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    # IPv4
    ("ipv4", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    # Bearer token (the token part after "Bearer ")
    ("bearer_token", re.compile(r"(?i)Bearer\s+([A-Za-z0-9\-._~+/]+=*)")),
    # Phone number (US format)
    ("phone", re.compile(r"\b(?:[\+]?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")),
    # Social Security Number
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
]

def _redact(value: str) -> str:
    """Redact a value, showing first and last two characters with ellipsis in between."""
    if len(value) <= 8:
        return value
    return value[:4] + "…" + value[-2:]

def scan_text(text: str) -> List[Dict[str, str]]:
    """
    Scan text for leakage patterns.

    Returns a list of dictionaries with keys: 'type' and 'match' (redacted).
    """
    findings: List[Dict[str, str]] = []
    for name, pattern in PATTERNS:
        for match in pattern.findall(text):
            # If the pattern has groups, findall returns tuples of groups.
            # We want the entire match if there are no groups, or the first group if there are groups.
            # However, we designed the patterns so that the capturing group (if any) is the interesting part.
            # For patterns without groups, match is a string.
            # For patterns with groups, match is a tuple; we take the first group.
            if isinstance(match, tuple):
                # Take the first non-empty group, or if all empty, skip.
                token = None
                for group in match:
                    if group:
                        token = group
                        break
                if token is None:
                    # If all groups are empty, skip this match.
                    continue
                match_str = token
            else:
                match_str = match

            if match_str:
                findings.append({
                    "type": name,
                    "match": _redact(match_str)
                })
    return findings

if __name__ == "__main__":  # pragma: no cover
    # Example usage
    test = """
    My phone number is 555-123-4567.
    Email: test@example.com
    AWS Key: AKIAIOSFODNN7EXAMPLE
    OpenAI Key: sk-abcdefghijklmnopqrstuvwxyz1234567890ab
    Bearer Token: ya29.a0AfH6SMB...
    """
    results = scan_text(test)
    for r in results:
        print(f"[{r['type']}] {r['match']}")