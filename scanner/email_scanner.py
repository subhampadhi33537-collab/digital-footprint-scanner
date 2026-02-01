"""
Email Scanner for AI-Powered Digital Footprint Scanner
-------------------------------------------------------
Responsibilities:
- Validate email syntax
- Detect disposable emails
- Validate email using Abstract API (if key exists)
- Detect GLOBAL public exposure via Gravatar
- Username scan is done by osint_scanner; no duplicate here.
"""

import requests
import re
import hashlib
from config import config

# -----------------------------------------
# Disposable email domains
# -----------------------------------------
TEMP_EMAIL_DOMAINS = {
    "mailinator.com", "10minutemail.com", "tempmail.com",
    "guerrillamail.com", "yopmail.com"
}

# -----------------------------------------
# Utilities
# -----------------------------------------
def extract_username(email: str) -> str:
    return email.split("@")[0].lower()

def check_email_syntax(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def check_disposable(email: str) -> bool:
    domain = email.split("@")[-1].lower()
    return domain in TEMP_EMAIL_DOMAINS

# -----------------------------------------
# Gravatar OSINT (GLOBAL)
# -----------------------------------------
def gravatar_lookup(email: str) -> dict:
    """
    Checks if email is registered on Gravatar (global public OSINT)
    """
    email_clean = email.strip().lower()
    email_hash = hashlib.md5(email_clean.encode()).hexdigest()
    gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"

    try:
        r = requests.get(gravatar_url, timeout=5)
        if r.status_code == 200:
            return {
                "found": True,
                "profile_url": f"https://www.gravatar.com/{email_hash}"
            }
        return {"found": False}
    except Exception as e:
        return {"found": False, "error": str(e)}

# -----------------------------------------
# Abstract Email Validation
# -----------------------------------------
def abstract_email_validation(email: str) -> dict:
    key = getattr(config, "ABSTRACT_EMAIL_API_KEY", None) or getattr(config, "ABSTRACT_API_KEY", None)
    if not key:
        return {"status": "skipped", "reason": "API key missing"}

    try:
        key = getattr(config, "ABSTRACT_EMAIL_API_KEY", None) or getattr(config, "ABSTRACT_API_KEY", None)
        r = requests.get(
            "https://emailvalidation.abstractapi.com/v1/",
            params={"api_key": key, "email": email},
            timeout=config.SCAN_TIMEOUT
        )
        return r.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}

# -----------------------------------------
# Main Email Scan
# -----------------------------------------
def scan_email(email: str) -> list:
    results = []

    # 1️⃣ Syntax
    results.append({
        "check": "Email Syntax",
        "status": "valid" if check_email_syntax(email) else "invalid"
    })

    # 2️⃣ Disposable
    results.append({
        "check": "Disposable Email",
        "status": "yes" if check_disposable(email) else "no"
    })

    # 3️⃣ Abstract API
    results.append({
        "check": "Email Validation API",
        "result": abstract_email_validation(email)
    })

    # 4️⃣ Gravatar Global Exposure
    results.append({
        "check": "Global Public Exposure (Gravatar)",
        "result": gravatar_lookup(email)
    })

    return results
