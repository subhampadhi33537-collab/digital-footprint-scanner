"""
Platform Checker for AI-Powered Digital Footprint Scanner
-----------------------------------------------------------
Responsibilities:
- Define all supported platforms for ethical username scanning
- Check if a username exists on a platform
- Provide utilities for the OSINT scanner and dashboard
- Fully connected with username scanning, normalization, and analytics
"""

import requests  # type: ignore
import time
import logging

# -------------------------------
# Logging Setup
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PLATFORM CHECKER] %(levelname)s: %(message)s"
)

# -------------------------------
# Supported Platforms
# -------------------------------
SUPPORTED_PLATFORMS = [
    "github",
    "twitter",
    "linkedin",
    "instagram",
    "facebook",
    "reddit",
    "medium",
    "stackoverflow",
    "devto",
    "pinterest"
]

# Mapping platform to URL pattern for username check
PLATFORM_URL_PATTERNS = {
    "github": "https://github.com/{}",
    "twitter": "https://twitter.com/{}",
    "linkedin": "https://www.linkedin.com/in/{}",
    "instagram": "https://www.instagram.com/{}",
    "facebook": "https://www.facebook.com/{}",
    "reddit": "https://www.reddit.com/user/{}",
    "medium": "https://medium.com/@{}",
    "stackoverflow": "https://stackoverflow.com/users/{}",
    "devto": "https://dev.to/{}",
    "pinterest": "https://www.pinterest.com/{}",
    "Xhamster": "https://xhamster.com/users/{}"
}

# -------------------------------
# Default request headers
# -------------------------------
HEADERS = {
    "User-Agent": "DigitalFootprintScanner/1.0 (+https://github.com/yourrepo)"
}

# -------------------------------
# Ethical request delay (seconds)
# -------------------------------
REQUEST_DELAY = 0.5


# -------------------------------
# Check if username exists on a platform
# -------------------------------
def is_username_present(platform: str, username: str, timeout: int = 5) -> bool:
    """
    Checks if a username exists on a specific platform.
    Args:
        platform (str): Platform name from SUPPORTED_PLATFORMS
        username (str): Username to check
        timeout (int): Timeout in seconds for the request
    Returns:
        bool: True if username exists, False otherwise
    """
    if platform not in PLATFORM_URL_PATTERNS:
        logging.warning(f"Platform '{platform}' not supported.")
        return False

    url = PLATFORM_URL_PATTERNS[platform].format(username)
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)

        # 200 means page exists → username exists
        # 404 means not found → username does not exist
        # Some platforms redirect non-existing profiles → handle cautiously
        exists = response.status_code == 200

        logging.info(f"Checked '{platform}' for username '{username}': {exists}")
        time.sleep(REQUEST_DELAY)  # ethical delay
        return exists

    except requests.exceptions.RequestException as e:
        logging.error(f"Error checking '{platform}' for username '{username}': {e}")
        return False


# -------------------------------
# Generate profile URL
# -------------------------------
def generate_profile_url(platform: str, username: str) -> str:
    """
    Returns the profile URL for a given username on the platform
    Args:
        platform (str): Platform name
        username (str): Username
    Returns:
        str: Complete URL
    """
    if platform not in PLATFORM_URL_PATTERNS:
        logging.warning(f"Platform '{platform}' not supported.")
        return ""
    return PLATFORM_URL_PATTERNS[platform].format(username)


# -------------------------------
# Scan username across all platforms
# -------------------------------
def scan_username_all_platforms(username: str, timeout: int = 5) -> dict:
    """
    Scans all supported platforms for the given username
    Args:
        username (str): Username to scan
        timeout (int): Request timeout
    Returns:
        dict: {platform: True/False} indicating presence
    """
    results = {}
    for platform in SUPPORTED_PLATFORMS:
        results[platform] = is_username_present(platform, username, timeout)
    return results


# -------------------------------
# Optional: Check all platforms availability (without username)
# -------------------------------
def check_all_platforms_available(timeout: int = 5) -> dict:
    """
    Checks if platform URLs are reachable in general (without username)
    Returns:
        dict: {platform: True/False}
    """
    results = {}
    for platform in SUPPORTED_PLATFORMS:
        test_url = PLATFORM_URL_PATTERNS[platform].format("example")
        try:
            r = requests.get(test_url, headers=HEADERS, timeout=timeout)
            results[platform] = r.status_code == 200
            time.sleep(REQUEST_DELAY)
        except requests.exceptions.RequestException:
            results[platform] = False
    return results

# Backward compatibility
def is_platform_available(platform: str, timeout: int = 5) -> bool:
    """
    Legacy function kept for imports.
    Checks if a platform is reachable using dummy username 'example'.
    """
    from . import is_username_present
    return is_username_present(platform, "example", timeout)

# -------------------------------
# Example Usage
# -------------------------------
if __name__ == "__main__":
    username = "subham123"
    print("Scanning username:", username)
    results = scan_username_all_platforms(username)
    for platform, found in results.items():
        print(f"{platform}: {'Found' if found else 'Not Found'}")
