"""
Data Normalizer for AI-Powered Digital Footprint Scanner
---------------------------------------------------------
Responsibilities:
- Convert raw scan results into structured JSON
- Prepare data for risk analysis engine
- Include fields for dashboard visualization and AI assistant
- Fully connected to scanner, analysis, and routes
"""

from config import config
import time

def normalize_scan_data(scan_data: dict) -> dict:
    """
    Normalizes raw scan data into a structured format.

    Args:
        scan_data (dict): Raw scan output from osint_scanner.py
            Expected keys: user_input, timestamp, email_exposure, username_exposure

    Returns:
        dict: Structured, standardized scan result
    """

    normalized = {
        "user_input": scan_data.get("user_input", ""),
        "timestamp": scan_data.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S")),
        "platforms_found": [],
        "emails_found": [],
        "usernames_found": [],
        "exposure_summary": {
            "personal_identifiers": 0,
            "contact_information": 0,
            "online_accounts": 0,
            "total_exposures": 0
        },
        "risk_ready": {},  # Placeholder for risk_engine.py
        "correlation_ready": {},  # Placeholder for correlation_analyzer.py
    }

    # ---------------------------
    # Process Email Exposure
    # ---------------------------
    for email_entry in scan_data.get("email_exposure", []):
        normalized["emails_found"].append({
            "platform": email_entry.get("platform"),
            "url": email_entry.get("url"),
            "detail": email_entry.get("detail")
        })
        # Count exposure categories for AI & analysis
        normalized["exposure_summary"]["contact_information"] += 1
        normalized["exposure_summary"]["total_exposures"] += 1

    # ---------------------------
    # Process Username Exposure
    # ---------------------------
    for user_entry in scan_data.get("username_exposure", []):
        normalized["usernames_found"].append({
            "platform": user_entry.get("platform"),
            "url": user_entry.get("url"),
            "status": user_entry.get("status")
        })
        if user_entry.get("status") == "found":
            normalized["platforms_found"].append(user_entry.get("platform"))
            # Count exposure categories
            normalized["exposure_summary"]["online_accounts"] += 1
            normalized["exposure_summary"]["total_exposures"] += 1

    # ---------------------------
    # Ensure exposure categories exist
    # ---------------------------
    for key in ["personal_identifiers", "contact_information", "online_accounts"]:
        normalized["exposure_summary"].setdefault(key, 0)

    # ---------------------------
    # Prepare risk_ready structure
    # ---------------------------
    normalized["risk_ready"] = {
        "low_threshold": config.RISK_THRESHOLDS["LOW"],
        "medium_threshold": config.RISK_THRESHOLDS["MEDIUM"],
        "high_threshold": config.RISK_THRESHOLDS["HIGH"]
    }

    # ---------------------------
    # Prepare correlation_ready structure
    # ---------------------------
    normalized["correlation_ready"] = {
        "platforms_linked": normalized["platforms_found"],
        "email_links": [e["platform"] for e in normalized["emails_found"]],
        "username_links": [u["platform"] for u in normalized["usernames_found"]]
    }

    # ---------------------------
    # Final Normalized Data Ready
    # ---------------------------
    return normalized
