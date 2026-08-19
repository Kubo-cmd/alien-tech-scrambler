"""
Leakage detection package.
Regex + entropy scanner for sensitive data in code/text.
"""

from .scanner import scan_text, PATTERNS
__all__ = ["scan_text", "PATTERNS"]
