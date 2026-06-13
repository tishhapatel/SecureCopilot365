"""
Guardrails and safety scanners for SecureCopilot 365 AI operations.
Detects prompt injections, jailbreaks, instruction overrides, and validates model output.
"""
import re
import logging

logger = logging.getLogger(__name__)

# Heuristic matches for standard prompt injections & jailbreaks
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"system\s+override", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+in\s+developer\s+mode", re.IGNORECASE),
    re.compile(r"pretend\s+you\s+are\s+a\s+different\s+ai", re.IGNORECASE),
    re.compile(r"dan\s+mode|jailbreak", re.IGNORECASE),
    re.compile(r"disable\s+safety\s+filters", re.IGNORECASE),
    re.compile(r"reveal\s+(?:your\s+)?system\s+instructions", re.IGNORECASE),
    re.compile(r"operating\s+parameters", re.IGNORECASE),
    re.compile(r"bypass\s+restrictions", re.IGNORECASE)
]

# Sensitive indicators that should never leak out of the model
SENSITIVE_LEAKAGE_PATTERNS = [
    re.compile(r"xox[p|b|o|a]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}", re.IGNORECASE), # Slack Token
    re.compile(r"AIzaSy[A-Za-z0-9_-]{33}", re.IGNORECASE), # Google API Key
    re.compile(r"sk-[A-Za-z0-9]{48}", re.IGNORECASE), # OpenAI Key
    re.compile(r"amzn\.mws\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.IGNORECASE), # AWS Token
    re.compile(r"-----\s*BEGIN\s+RSA\s+PRIVATE\s+KEY\s*-----", re.IGNORECASE) # Private key
]

def scan_prompt_for_injection(prompt: str) -> bool:
    """
    Scans the prompt input for known injection patterns.
    Returns True if an injection attempt is detected.
    """
    if not prompt:
        return False

    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern.search(prompt):
            logger.error(f"AI Safety Blocked: Prompt injection detected: '{pattern.pattern}'")
            return True
    return False

def scan_output_for_leakage(output: str) -> bool:
    """
    Scans the LLM output to prevent leakage of credentials or keys.
    Returns True if a leak is detected.
    """
    if not output:
        return False

    for pattern in SENSITIVE_LEAKAGE_PATTERNS:
        if pattern.search(output):
            logger.critical(f"AI Leakage Gated: System attempted to output sensitive string: '{pattern.pattern}'")
            return True
    return False

def sanitize_response(output: str) -> str:
    """
    Applies sanitization to output if toxic or unsafe content is suspected.
    """
    # Quick toxicity/unsafe heuristic check
    toxic_words = ["harmful", "illegal", "exploit", "hack into", "bypass password"]
    for word in toxic_words:
        if word in output.lower() and "how to" in output.lower():
            logger.warning("AI Safety Warning: Output sanitization triggered due to instructional hazard")
            return "Policy Warning: SecureCopilot 365 cannot provide instructions on executing offensive hacks or security bypasses."
    return output
