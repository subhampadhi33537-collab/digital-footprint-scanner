"""
Exposure Classifier for AI-Powered Digital Footprint Scanner
-------------------------------------------------------------
Responsibilities:
- Classify types of exposure (personal identifiers, contact info, online accounts)
- Analyze normalized scan data
- Provide structured output for dashboard and AI assistant
- Fully connected with risk_engine, dashboard, AI, and routes
"""

import logging

# -------------------------------
# Logging Setup
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [EXPOSURE CLASSIFIER] %(levelname)s: %(message)s"
)

# -------------------------------
# Exposure Classification
# -------------------------------
def classify_exposure(normalized_data: dict) -> dict:
    """
    Classify exposure types from normalized scan data
    
    Args:
        normalized_data (dict): Output from scanner/data_normalizer.py
            Expected keys: emails_found, usernames_found
    
    Returns:
        dict: Structured classification of exposures
    """
    classified = {
        "personal_identifiers": [],
        "contact_information": [],
        "online_accounts": [],
        "total_exposures": 0
    }

    # ---------------------------
    # Process Email Exposure
    # ---------------------------
    for email_entry in normalized_data.get("emails_found", []):
        classified["contact_information"].append({
            "platform": email_entry.get("platform"),
            "email": email_entry.get("url"),
            "detail": email_entry.get("detail")
        })

    # ---------------------------
    # Process Username Exposure
    # ---------------------------
    for user_entry in normalized_data.get("usernames_found", []):
        if user_entry.get("status") == "found":
            classified["online_accounts"].append({
                "platform": user_entry.get("platform"),
                "url": user_entry.get("url"),
                "username": user_entry.get("username", user_entry.get("url"))  # fallback to URL if username missing
            })



    # ---------------------------
    # Optional: Personal Identifiers
    # Could include name, date of birth, phone, etc.
    # For now, mock data if available in normalized_data
    # ---------------------------
    personal_data = normalized_data.get("personal_data", [])
    for item in personal_data:
        classified["personal_identifiers"].append({
            "type": item.get("type"),
            "value": item.get("value"),
            "source": item.get("source")
        })

    # ---------------------------
    # Count total exposures
    # ---------------------------
    classified["total_exposures"] = (
        len(classified["personal_identifiers"]) +
        len(classified["contact_information"]) +
        len(classified["online_accounts"])
    )

    logging.info(f"Exposure classified: {classified['total_exposures']} total exposures")
    return classified

# -------------------------------
# Helper: Quick Summary for Dashboard
# -------------------------------
def exposure_summary(classified_exposure: dict) -> dict:
    """
    Returns summarized counts for dashboard visualization
    """
    summary = {
        "personal_identifiers": len(classified_exposure.get("personal_identifiers", [])),
        "contact_information": len(classified_exposure.get("contact_information", [])),
        "online_accounts": len(classified_exposure.get("online_accounts", [])),
        "total_exposures": classified_exposure.get("total_exposures", 0)
    }
    return summary
