"""
Correlation Analyzer for AI-Powered Digital Footprint Scanner
----------------------------------------------------------------
Responsibilities:
- Detect cross-platform linkages and correlations
- Identify patterns between emails, usernames, and platforms
- Provide structured insights for dashboard and AI assistant
- Fully connected with scanner, exposure classifier, risk engine, and routes
"""

import logging

# -------------------------------
# Logging Setup
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CORRELATION ANALYZER] %(levelname)s: %(message)s"
)

# -------------------------------
# Correlation Analysis
# -------------------------------
def analyze_correlation(normalized_data: dict) -> dict:
    """
    Analyze cross-platform linkages and correlations
    Args:
        normalized_data (dict): Normalized scan data from scanner
            Expected keys: emails_found, usernames_found, platforms_checked
    Returns:
        dict: Structured correlation results
    """
    correlation_results = {
        "linked_platforms": {},
        "email_to_platforms": {},
        "username_to_platforms": {},
        "cross_platform_matches": [],
        "summary": {}
    }

    # ---------------------------
    # Map emails to platforms
    # ---------------------------
    for email_entry in normalized_data.get("emails_found", []):
        platform = email_entry.get("platform")
        email = email_entry.get("url")  # or actual email value
        if email not in correlation_results["email_to_platforms"]:
            correlation_results["email_to_platforms"][email] = []
        correlation_results["email_to_platforms"][email].append(platform)

    # ---------------------------
    # Map usernames to platforms
    # ---------------------------
    for user_entry in normalized_data.get("usernames_found", []):
        platform = user_entry.get("platform")
        username = user_entry.get("url")  # profile URL
        if username not in correlation_results["username_to_platforms"]:
            correlation_results["username_to_platforms"][username] = []
        correlation_results["username_to_platforms"][username].append(platform)

    # ---------------------------
    # Detect cross-platform matches
    # ---------------------------
    # Example: same username/email on multiple platforms
    for username, platforms in correlation_results["username_to_platforms"].items():
        if len(platforms) > 1:
            correlation_results["cross_platform_matches"].append({
                "type": "username",
                "identifier": username,
                "platforms": platforms
            })

    for email, platforms in correlation_results["email_to_platforms"].items():
        if len(platforms) > 1:
            correlation_results["cross_platform_matches"].append({
                "type": "email",
                "identifier": email,
                "platforms": platforms
            })

    # ---------------------------
    # Linked platforms summary
    # ---------------------------
    for match in correlation_results["cross_platform_matches"]:
        for platform in match["platforms"]:
            if platform not in correlation_results["linked_platforms"]:
                correlation_results["linked_platforms"][platform] = []
            correlation_results["linked_platforms"][platform].append(match["identifier"])

    # ---------------------------
    # Summary statistics
    # ---------------------------
    correlation_results["summary"] = {
        "total_usernames_found": len(normalized_data.get("usernames_found", [])),
        "total_emails_found": len(normalized_data.get("emails_found", [])),
        "total_cross_platform_matches": len(correlation_results["cross_platform_matches"]),
        "total_linked_platforms": len(correlation_results["linked_platforms"])
    }

    logging.info(f"Correlation analysis completed: {correlation_results['summary']}")
    return correlation_results
