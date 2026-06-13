"""
PII Anonymization and Masking utility for SecureCopilot 365.
Redacts names, emails, phone numbers, and employee credentials before submission to LLMs.
Allows localized restoration of PII in output responses.
"""
import re

# Regex for common PII patterns
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"\+?\b\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b")
EMPLOYEE_ID_REGEX = re.compile(r"\bEMP-[0-9]{5,6}\b")
IP_ADDRESS_REGEX = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")

# Names masking is tricky without NER model. We can match common names or mock pattern,
# or look for key indicators (e.g. "Name: Sarah Connor", "user John Doe").
# Let's match typical name introduction patterns for basic heuristic masking.
NAME_INTRO_REGEX = re.compile(r"(?:name\s+is\s+|user\s+|employee\s+|mr\.\s+|ms\.\s+)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)")

def mask_pii(text: str) -> tuple[str, dict[str, str]]:
    """
    Masks PII elements and returns the anonymized string and a mapping dictionary.
    """
    if not text:
        return "", {}

    mask_map = {}
    counter = 1

    # 1. Mask Emails
    emails = EMAIL_REGEX.findall(text)
    for email in set(emails):
        placeholder = f"[EMAIL_{counter}]"
        mask_map[placeholder] = email
        text = text.replace(email, placeholder)
        counter += 1

    # 2. Mask Phone numbers
    phones = PHONE_REGEX.findall(text)
    for phone in set(phones):
        # Prevent masking short digits like years or compliance count
        if len(phone.strip().replace("-", "").replace(" ", "")) >= 7:
            placeholder = f"[PHONE_{counter}]"
            mask_map[placeholder] = phone
            text = text.replace(phone, placeholder)
            counter += 1

    # 3. Mask Employee IDs
    emp_ids = EMPLOYEE_ID_REGEX.findall(text)
    for emp_id in set(emp_ids):
        placeholder = f"[EMP_ID_{counter}]"
        mask_map[placeholder] = emp_id
        text = text.replace(emp_id, placeholder)
        counter += 1

    # 4. Mask IP addresses
    ips = IP_ADDRESS_REGEX.findall(text)
    for ip in set(ips):
        if ip != "127.0.0.1": # Keep localhost
            placeholder = f"[IP_{counter}]"
            mask_map[placeholder] = ip
            text = text.replace(ip, placeholder)
            counter += 1

    # 5. Mask Names from patterns
    names = NAME_INTRO_REGEX.findall(text)
    for name in set(names):
        # Filter out common false positives
        if name.lower() not in ["email", "phone", "employee", "vendor", "compliance", "securecopilot"]:
            placeholder = f"[NAME_{counter}]"
            mask_map[placeholder] = name
            text = text.replace(name, placeholder)
            counter += 1

    return text, mask_map

def unmask_pii(text: str, mask_map: dict[str, str]) -> str:
    """
    Restores the original PII values back into the text based on the mask map.
    """
    if not text or not mask_map:
        return text

    sanitized_text = text
    for placeholder, original in mask_map.items():
        sanitized_text = sanitized_text.replace(placeholder, original)
    return sanitized_text
