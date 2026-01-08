"""
Analysis Package Initialization
---------------------------------------------------
Responsibilities:
- Expose unified interface to analyze normalized scan data
- Import all analysis modules for easy access
- Connect scanner output to risk engine, exposure classifier, and correlation analyzer
- Ready for routes.py, dashboard, and AI assistant
"""

# ===============================
# IMPORT MODULES
# ===============================
from .risk_engine import calculate_risk, is_high_risk
from .exposure_classifier import classify_exposure, exposure_summary
from .correlation_analyzer import analyze_correlation
import logging

# ===============================
# LOGGING SETUP
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ANALYSIS INIT] %(levelname)s: %(message)s"
)

# ===============================
# PACKAGE LEVEL INTERFACE
# ===============================
__all__ = [
    "calculate_risk",
    "is_high_risk",
    "classify_exposure",
    "exposure_summary",
    "analyze_correlation",
    "analyze_user_data"
]

# ===============================
# UNIFIED ANALYSIS FUNCTION
# ===============================
def analyze_user_data(normalized_data: dict) -> dict:
    """
    Unified interface to analyze normalized scan data from scanner
    
    Args:
        normalized_data (dict): Output from scanner.scan_user()
    
    Returns:
        dict: Combined analysis results for dashboard and AI assistant
    """
    logging.info("Starting unified analysis of normalized data")

    # -------------------------------
    # Exposure Classification
    # -------------------------------
    classified_exposure = classify_exposure(normalized_data)
    summary_counts = exposure_summary(classified_exposure)

    # -------------------------------
    # Risk Assessment
    # -------------------------------
    risk_result = calculate_risk({"exposure_summary": summary_counts})

# Add description text for template
    if risk_result["risk_level"] == "HIGH":
        risk_result["description"] = "High risk! Many exposures across multiple platforms."
    elif risk_result["risk_level"] == "MEDIUM":
        risk_result["description"] = "Medium risk. Some exposures detected."
    else:
        risk_result["description"] = "Low risk. Your online exposure is minimal."


    # -------------------------------
    # Correlation Analysis
    # -------------------------------
    correlation_result = analyze_correlation(normalized_data)

    # -------------------------------
    # Combined Analysis Output
    # -------------------------------
    combined_analysis = {
        "classified_exposure": classified_exposure,
        "exposure_summary": summary_counts,
        "risk_result": risk_result,
        "correlation_result": correlation_result
    }

    logging.info("Unified analysis completed")
    return combined_analysis

# ===============================
# OPTIONAL: PACKAGE READY MESSAGE
# ===============================
logging.info("✅ Analysis package initialized. All modules loaded and ready.")
