"""
Risk Engine for AI-Powered Digital Footprint Scanner
------------------------------------------------------
Responsibilities:
- Analyze normalized scan data
- Calculate risk level (Low / Medium / High) based on exposure
- Provide structured output for dashboard and AI assistant
- Fully connected with scanner, dashboard, AI, and routes
"""

from config import config
import logging

# -------------------------------
# Logging Setup
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [RISK ENGINE] %(levelname)s: %(message)s"
)

# -------------------------------
# Risk Level Calculation
# -------------------------------
def calculate_risk(normalized_data: dict) -> dict:
    """
    Calculate risk level based on exposure counts
    Args:
        normalized_data (dict): Output from scanner/data_normalizer.py
            Expected keys: exposure_summary
    Returns:
        dict: Risk summary with level, score, and details
    """

    exposure_summary = normalized_data.get("exposure_summary", {})
    total_exposures = exposure_summary.get("total_exposures", 0)

    # Thresholds from config
    low_threshold = getattr(config, "RISK_THRESHOLDS", {}).get("LOW", 2)
    medium_threshold = getattr(config, "RISK_THRESHOLDS", {}).get("MEDIUM", 5)
    high_threshold = getattr(config, "RISK_THRESHOLDS", {}).get("HIGH", 10)

    # -------------------------------
    # Determine Risk Level
    # -------------------------------
    if total_exposures >= high_threshold:
        risk_level = "HIGH"
    elif total_exposures >= medium_threshold:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # -------------------------------
    # Detailed Risk Score
    # -------------------------------
    risk_score = {
        "personal_identifiers": exposure_summary.get("personal_identifiers", 0),
        "contact_information": exposure_summary.get("contact_information", 0),
        "online_accounts": exposure_summary.get("online_accounts", 0),
        "total_exposures": total_exposures
    }

    # -------------------------------
    # Risk Output
    # -------------------------------
    risk_result = {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "low_threshold": low_threshold,
        "medium_threshold": medium_threshold,
        "high_threshold": high_threshold
    }

    logging.info(f"Risk calculated: Level={risk_level}, Total Exposures={total_exposures}")
    return risk_result

# -------------------------------
# Optional Helper: Is User At High Risk
# -------------------------------
def is_high_risk(normalized_data: dict) -> bool:
    """
    Quick check if user exposure is high risk
    """
    risk = calculate_risk(normalized_data)
    return risk["risk_level"] == "HIGH"
