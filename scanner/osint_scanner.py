"""
OSINT Scanner Orchestrator for AI-Powered Digital Footprint Scanner
-------------------------------------------------------------------
Responsibilities:
- Orchestrates email and username scanning
- Respects ethical OSINT limits
- Uses public data only (no private account access)
- Normalizes results for dashboard and AI analysis
- OAuth is used ONLY for user authentication (not data access)
"""

import time
import logging
from config import config

# Real scanning modules
from scanner.email_scanner import scan_email
from scanner.username_scanner import check_username_presence
from scanner.platform_checker import SUPPORTED_PLATFORMS
from scanner.data_normalizer import normalize_scan_data

# ---------------------------
# Logging Setup
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [OSINT SCANNER] %(levelname)s: %(message)s"
)

# ---------------------------
# Main Scan Function
# ---------------------------
def run_full_scan(user_input: str, max_platforms: int = None, timeout: int = None) -> dict:
    """
    Orchestrates a full ethical OSINT scan.

    Args:
        user_input (str): Email or username to scan
        max_platforms (int): Maximum number of platforms to scan
        timeout (int): HTTP request timeout per platform

    Returns:
        dict: Normalized scan results
    """

    max_platforms = max_platforms or config.MAX_PLATFORMS
    timeout = timeout or config.SCAN_TIMEOUT

    logging.info(f"Starting OSINT scan for: {user_input}")

    scan_data = {
        "user_input": user_input,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "email_exposure": [],
        "username_exposure": [],
        "platforms_checked": []
    }

    # ---------------------------
    # EMAIL SCAN (PUBLIC OSINT)
    # ---------------------------
    if "@" in user_input:
        logging.info(f"Detected email input. Running email OSINT checks.")
        try:
            # scan_email internally uses API keys from config
            scan_data["email_exposure"] = scan_email(user_input)
        except Exception as e:
            logging.error(f"Email scan failed: {e}")
            scan_data["email_exposure"] = []

    # ---------------------------
    # USERNAME SCAN
    # ---------------------------
    username = user_input.split("@")[0] if "@" in user_input else user_input
    logging.info(f"Scanning username across platforms: {username}")

    try:
        username_results = check_username_presence(
            username=username,
            platforms=SUPPORTED_PLATFORMS,
            max_platforms=max_platforms,
            timeout=timeout
        )
    except Exception as e:
        logging.error(f"Username scan failed: {e}")
        username_results = []

    scan_data["username_exposure"] = username_results

    # ---------------------------
    # Platforms Checked
    # ---------------------------
    scan_data["platforms_checked"] = [
        entry.get("platform") for entry in username_results if isinstance(entry, dict)
    ]

    # ---------------------------
    # Normalize Data
    # ---------------------------
    logging.info("Normalizing scan data for dashboard and AI")
    try:
        normalized_data = normalize_scan_data(scan_data)
    except Exception as e:
        logging.error(f"Data normalization failed: {e}")
        normalized_data = scan_data

    logging.info("OSINT scan completed successfully")
    return normalized_data
