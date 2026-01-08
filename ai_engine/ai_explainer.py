"""
AI Explainer for Digital Footprint Scanner
------------------------------------------------
Responsibilities:
- Take analysis results and generate user-friendly explanations
- Explain risk level, exposure types, and cross-platform correlations
- Provide structured output for dashboard and AI assistant
- Fully connected with chatbot_handler, gemini_client, scanner, and analysis modules
"""

import logging
import json

# -------------------------------
# Logging Setup
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AI EXPLAINER] %(levelname)s: %(message)s"
)

# -------------------------------
# Main Explainer Function
# -------------------------------
def explain_analysis(analysis_result: dict) -> dict:
    """
    Generate a human-friendly explanation for the analysis results
    
    Args:
        analysis_result (dict): Output from analysis.analyze_user_data()
            Contains classified_exposure, exposure_summary, risk_result, correlation_result

    Returns:
        dict: Structured explanation for dashboard and AI assistant
            - risk_explanation
            - exposure_explanation
            - correlation_explanation
            - recommendations
    """
    try:
        # ---------------------------
        # Extract key info
        # ---------------------------
        classified = analysis_result.get("classified_exposure", {})
        summary = analysis_result.get("exposure_summary", {})
        risk = analysis_result.get("risk_result", {})
        correlations = analysis_result.get("correlation_result", {})

        # ---------------------------
        # Risk Explanation
        # ---------------------------
        risk_level = risk.get("risk_level", "Unknown")
        risk_explanation = f"Your overall digital footprint risk is {risk_level}. "
        if risk_level == "HIGH":
            risk_explanation += "You have many exposures across multiple platforms, which could be potentially harmful if sensitive information is involved."
        elif risk_level == "MEDIUM":
            risk_explanation += "You have a moderate number of exposures. Some caution is advised."
        else:
            risk_explanation += "Your exposure is low, but you should continue safe online practices."

        # ---------------------------
        # Exposure Explanation
        # ---------------------------
        exposure_explanation = "Exposure Summary:\n"
        exposure_explanation += f"- Personal Identifiers: {summary.get('personal_identifiers', 0)}\n"
        exposure_explanation += f"- Contact Information: {summary.get('contact_information', 0)}\n"
        exposure_explanation += f"- Online Accounts: {summary.get('online_accounts', 0)}\n"

        # Optional: list example exposures (limit for readability)
        max_display = 3
        if classified.get("personal_identifiers"):
            exposure_explanation += "- Example Personal Identifiers: " + \
                ", ".join([str(item.get("value")) for item in classified["personal_identifiers"][:max_display]]) + "\n"
        if classified.get("contact_information"):
            exposure_explanation += "- Example Emails: " + \
                ", ".join([str(item.get("email")) for item in classified["contact_information"][:max_display]]) + "\n"
        if classified.get("online_accounts"):
            exposure_explanation += "- Example Accounts: " + \
                ", ".join([str(item.get("platform")) for item in classified["online_accounts"][:max_display]]) + "\n"

        # ---------------------------
        # Correlation Explanation
        # ---------------------------
        cross_matches = correlations.get("cross_platform_matches", [])
        correlation_explanation = ""
        if cross_matches:
            correlation_explanation += f"You have {len(cross_matches)} cross-platform linkages, meaning same usernames or emails appear on multiple platforms. This increases exposure risk.\n"
            # Optionally list first few examples
            for match in cross_matches[:max_display]:
                correlation_explanation += f"- {match['type'].title()}: {match['identifier']} on {', '.join(match['platforms'])}\n"
        else:
            correlation_explanation += "No significant cross-platform linkages detected."

        # ---------------------------
        # Recommendations
        # ---------------------------
        recommendations = []
        if risk_level == "HIGH":
            recommendations.append("Consider updating privacy settings on all platforms.")
            recommendations.append("Avoid reusing usernames and emails across platforms.")
            recommendations.append("Review and remove outdated personal information online.")
        elif risk_level == "MEDIUM":
            recommendations.append("Check accounts for privacy leaks and update passwords regularly.")
            recommendations.append("Limit sharing personal info on public platforms.")
        else:
            recommendations.append("Continue safe online practices.")
            recommendations.append("Regularly monitor digital footprint for changes.")

        explanation = {
            "risk_explanation": risk_explanation,
            "exposure_explanation": exposure_explanation,
            "correlation_explanation": correlation_explanation,
            "recommendations": recommendations
        }

        logging.info("AI Explainer generated successfully.")
        return explanation

    except Exception as e:
        logging.error(f"Error generating AI explanation: {e}")
        return {
            "risk_explanation": "Unable to generate explanation.",
            "exposure_explanation": "",
            "correlation_explanation": "",
            "recommendations": []
        }

# -------------------------------
# Helper Function for Dashboard / AI
# -------------------------------
def get_explanation_for_user(analysis_result: dict) -> str:
    """
    Returns a formatted text explanation suitable for dashboard or chatbot
    """
    explanation = explain_analysis(analysis_result)
    formatted_text = f"{explanation['risk_explanation']}\n\n"
    formatted_text += f"{explanation['exposure_explanation']}\n"
    formatted_text += f"{explanation['correlation_explanation']}\n\n"
    formatted_text += "Recommendations:\n" + "\n".join(["- " + r for r in explanation['recommendations']])
    return formatted_text
