"""
Scanner Package Initialization
---------------------------------------------------
Responsibilities:
- Expose unified interface to run OSINT scans
- Import all scanner modules for easy access
- Connect configuration and ethical scanning defaults
- Ready for routes.py, analysis, dashboard, and AI assistant
"""

# ===============================
# IMPORT CONFIGURATION
# ===============================
from config import config
import logging
import time

# ===============================
# IMPORT SCANNER MODULES
# ===============================
from .osint_scanner import run_full_scan
from .email_scanner import scan_email
from .username_scanner import check_username_presence
from .platform_checker import SUPPORTED_PLATFORMS, generate_profile_url, is_platform_available
from .data_normalizer import normalize_scan_data

# ===============================
# LOGGING SETUP
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SCANNER INIT] %(levelname)s: %(message)s"
)

# ===============================
# PACKAGE LEVEL INTERFACE
# ===============================
# Other modules can import these directly
__all__ = [
    "run_full_scan",
    "scan_email",
    "check_username_presence",
    "SUPPORTED_PLATFORMS",
    "generate_profile_url",
    "is_platform_available",
    "normalize_scan_data",
    "scan_user"
]

# ===============================
# UNIFIED SCAN FUNCTION
# ===============================
def scan_user(user_input: str) -> dict:
    """
    Unified interface to scan a user input (email or username)
    
    Args:
        user_input (str): Email or username
    
    Returns:
        dict: Normalized structured scan results ready for analysis, dashboard, and AI
    """
    logging.info(f"Starting unified scan for: {user_input}")
    start_time = time.time()
    scan_result = run_full_scan(
        user_input=user_input,
        max_platforms=getattr(config, "MAX_PLATFORMS", 10),
        timeout=getattr(config, "SCAN_TIMEOUT", 10)
    )
    duration = time.time() - start_time
    logging.info(f"Scan completed in {duration:.2f} seconds for: {user_input}")
    return scan_result

# ===============================
# OPTIONAL: PACKAGE READY MESSAGE
# ===============================
logging.info("✅ Scanner package initialized. All modules loaded and ready.")
