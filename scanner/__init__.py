"""
Scanner Package Initialization
---------------------------------------------------
Responsibilities:
- Expose a unified interface to run OSINT scans
- Safely import scanner modules
- Avoid circular imports
- Provide a clean public API for routes, dashboard, and AI layer
"""

# ===============================
# STANDARD LIB IMPORTS
# ===============================
import logging
import time

# ===============================
# CONFIG IMPORT
# ===============================
from config import config

# ===============================
# LOGGING SETUP (safe for packages)
# ===============================
logger = logging.getLogger("scanner")
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [SCANNER] %(levelname)s: %(message)s"
    )

# ===============================
# IMPORT SCANNER MODULES
# (keep order to avoid circular imports)
# ===============================
from .platform_checker import (
    SUPPORTED_PLATFORMS,
    generate_profile_url,
    is_platform_available,
)

from .username_scanner import check_username_presence
from .email_scanner import scan_email
from .osint_scanner import run_full_scan
from .data_normalizer import normalize_scan_data

# ===============================
# PUBLIC PACKAGE INTERFACE
# ===============================
__all__ = [
    "run_full_scan",
    "scan_email",
    "check_username_presence",
    "SUPPORTED_PLATFORMS",
    "generate_profile_url",
    "is_platform_available",
    "normalize_scan_data",
    "scan_user",
]

# ===============================
# UNIFIED SCAN FUNCTION
# ===============================
def scan_user(user_input: str) -> dict:
    """
    Unified interface to scan a user input (email or username)

    Args:
        user_input (str): Email address or username

    Returns:
        dict: Normalized scan results
    """
    logger.info(f"Starting unified scan for: {user_input}")

    start_time = time.time()

    result = run_full_scan(
        user_input=user_input,
        max_platforms=getattr(config, "MAX_PLATFORMS", 10),
        timeout=getattr(config, "SCAN_TIMEOUT", 10),
    )

    duration = time.time() - start_time
    logger.info(f"Scan completed in {duration:.2f}s for: {user_input}")

    return result


# ===============================
# PACKAGE READY CONFIRMATION
# ===============================
logger.info("✅ Scanner package initialized successfully.")
