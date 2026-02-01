"""
Data Normalizer for AI-Powered Digital Footprint Scanner
---------------------------------------------------------
Responsibilities:
- Convert raw scan results into structured JSON
- Prepare data for risk analysis engine
- Include fields for dashboard visualization and AI assistant
- Handles real email_scanner output (checks) and username_exposure (platform, url, status)
"""

from config import config
import time


def _extract_username(user_input: str) -> str:
    if not user_input:
        return ""
    return user_input.split("@")[0].strip().lower() if "@" in user_input else user_input.strip().lower()


def normalize_scan_data(scan_data: dict) -> dict:
    """
    Normalizes raw scan data into a structured format.

    Args:
        scan_data (dict): Raw scan output from osint_scanner.py
            Expected keys: user_input, timestamp, email_exposure, username_exposure

    Returns:
        dict: Structured, standardized scan result
    """
    user_input = scan_data.get("user_input", "")
    username = _extract_username(user_input)

    normalized = {
        "user_input": user_input,
        "username_scanned": username,
        "timestamp": scan_data.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S")),
        "platforms_found": [],
        "emails_found": [],
        "usernames_found": [],
        "all_platforms_checked": [],
        "names_found": [],
        "platform_links": [],
        "exposure_summary": {
            "personal_identifiers": 0,
            "contact_information": 0,
            "online_accounts": 0,
            "total_exposures": 0,
        },
        "risk_ready": {},
        "correlation_ready": {},
    }

    # ---------------------------
    # Process Email Exposure (real email_scanner format: list of checks)
    # ---------------------------
    for entry in scan_data.get("email_exposure", []):
        check = entry.get("check", "")
        if check == "Global Public Exposure (Gravatar)":
            res = entry.get("result") or {}
            if res.get("found"):
                normalized["emails_found"].append({
                    "platform": "Gravatar",
                    "url": res.get("profile_url", ""),
                    "detail": "Email linked to public Gravatar profile",
                    "email": user_input if "@" in user_input else "",
                })
        elif check == "Email Validation API":
            res = entry.get("result") or {}
            if isinstance(res, dict) and res.get("status") != "skipped" and res.get("status") != "error":
                deliverable = (res.get("deliverability") or "").lower() in ("deliverable", "valid")
                if deliverable and user_input and "@" in user_input:
                    normalized["emails_found"].append({
                        "platform": "Email Validation",
                        "url": "",
                        "detail": f"Valid/deliverable ({res.get('deliverability', 'unknown')})",
                        "email": user_input,
                    })

    if user_input and "@" in user_input and not normalized["emails_found"]:
        normalized["emails_found"].append({
            "platform": "Input",
            "url": "",
            "detail": "Email scanned",
            "email": user_input,
        })

    # ---------------------------
    # Process Username Exposure (real username_scanner format: platform, url, status)
    # ---------------------------
    for user_entry in scan_data.get("username_exposure", []):
        plat = user_entry.get("platform", "")
        url = user_entry.get("url", "")
        status = user_entry.get("status", "")
        normalized["usernames_found"].append({
            "platform": plat,
            "url": url,
            "status": status,
        })
        normalized["all_platforms_checked"].append({
            "platform": plat,
            "url": url,
            "status": status,
        })
        if status == "found":
            normalized["platforms_found"].append(plat)
            normalized["platform_links"].append(plat)

    if username:
        normalized["names_found"] = [username]

    # ---------------------------
    # Exposure counts
    # ---------------------------
    normalized["exposure_summary"]["personal_identifiers"] = len(normalized["names_found"])
    normalized["exposure_summary"]["contact_information"] = len(normalized["emails_found"])
    normalized["exposure_summary"]["online_accounts"] = len(normalized["platforms_found"])
    normalized["exposure_summary"]["total_exposures"] = (
        normalized["exposure_summary"]["personal_identifiers"]
        + normalized["exposure_summary"]["contact_information"]
        + normalized["exposure_summary"]["online_accounts"]
    )

    for key in ["personal_identifiers", "contact_information", "online_accounts"]:
        normalized["exposure_summary"].setdefault(key, 0)

    # ---------------------------
    # Risk & correlation ready
    # ---------------------------
    normalized["risk_ready"] = {
        "low_threshold": config.RISK_THRESHOLDS["LOW"],
        "medium_threshold": config.RISK_THRESHOLDS["MEDIUM"],
        "high_threshold": config.RISK_THRESHOLDS["HIGH"],
    }
    normalized["correlation_ready"] = {
        "platforms_linked": normalized["platforms_found"],
        "email_links": [e.get("platform", "") for e in normalized["emails_found"]],
        "username_links": [u["platform"] for u in normalized["usernames_found"]],
    }

    return normalized
