"""
Email Scanner for AI-Powered Digital Footprint Scanner
-------------------------------------------------------
Responsibilities:
- Check Gmail or other emails for public exposure
- Validate syntax and detect disposable emails
- Use free Abstract API for validation (if API key is present)
- Trigger username OSINT scan based on email prefix
- Return structured results for normalization and dashboard
"""

import requests # type: ignore
import re
from config import config
from scanner.username_scanner import check_username_presence

# -----------------------------------------
# Temporary / disposable email domains
# -----------------------------------------
TEMP_EMAIL_DOMAINS = {
    "mailinator.com", "10minutemail.com", "tempmail.com",
    "guerrillamail.com", "yopmail.com", "guerrillamail.org"
}

# -----------------------------------------
# Utilities
# -----------------------------------------
def extract_username(email: str) -> str:
    """Extract username from email before '@'"""
    return email.split("@")[0].lower()

def check_email_syntax(email: str) -> bool:
    """Validate basic email syntax"""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def check_disposable(email: str) -> bool:
    """Check if email belongs to a disposable domain"""
    domain = email.split("@")[-1].lower()
    return domain in TEMP_EMAIL_DOMAINS

def abstract_email_validation(email: str) -> dict:
    """
    Validate email using Abstract API (free tier)
    Returns dict with API result or error
    """
    if not getattr(config, "ABSTRACT_EMAIL_API_KEY", None):
        return {"status": "skipped", "reason": "API key missing"}

    try:
        response = requests.get(
            getattr(config, "ABSTRACT_EMAIL_API_URL", "https://emailvalidation.abstractapi.com/v1/"),
            params={
                "api_key": config.ABSTRACT_EMAIL_API_KEY,
                "email": email
            },
            timeout=getattr(config, "SCAN_TIMEOUT", 10)
        )
        return response.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}

# -----------------------------------------
# Main Scanner Function
# -----------------------------------------
def scan_email(email: str) -> list:
    """
    Run full email scan including:
    - Syntax check
    - Disposable email check
    - Free API validation (if API key exists)
    - Username OSINT scan
    Returns list of structured results
    """
    results = []

    # 1️⃣ Email Syntax
    syntax_valid = check_email_syntax(email)
    results.append({
        "check": "Email Syntax",
        "status": "valid" if syntax_valid else "invalid"
    })

    # 2️⃣ Disposable Email
    disposable = check_disposable(email)
    results.append({
        "check": "Disposable Email",
        "status": "yes" if disposable else "no"
    })

    # 3️⃣ Abstract API Validation
    api_result = abstract_email_validation(email)
    results.append({
        "check": "Email Validation API",
        "result": api_result
    })

    # 4️⃣ Username OSINT Scan (from email prefix)
    username = extract_username(email)
    username_results = check_username_presence(username)
    results.append({
        "check": "Username OSINT",
        "username": username,
        "platforms": username_results
    })

    return results
