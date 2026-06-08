"""
Sanitize input helper to strip prompt injection attempts.
"""
import re

def sanitize_text(text: str) -> str:
    injection_patterns = [
        r"ignore (previous|all|above) instructions",
        r"system:\s",
        r"you are now",
        r"new instructions:",
        r"forget everything",
        r"<\|system\|>",
        r"<\|user\|>",
        r"\[INST\]",
        r"###\s*(System|Instruction)",
    ]
    sanitized = text
    for pattern in injection_patterns:
        sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)
    # Cap size to prevent token stuffing
    return sanitized[:8000]
