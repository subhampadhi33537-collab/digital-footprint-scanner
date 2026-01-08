"""
Username Scanner for AI-Powered Digital Footprint Scanner
---------------------------------------------------------
REAL OSINT IMPLEMENTATION

Responsibilities:
- Scan a given username across supported platforms
- Perform real existence checks using HTML fingerprinting
- Avoid false positives caused by HTTP 200 responses
- Use ethical OSINT techniques (timeouts, delays)
- Return structured results for normalization, dashboard, and AI
"""

import requests # type: ignore
import time
import logging
from scanner.platform_checker import SUPPORTED_PLATFORMS, generate_profile_url

# -------------------------------
# Logging Setup
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [USERNAME SCANNER] %(levelname)s: %(message)s"
)

# -------------------------------
# HTTP Headers
# -------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; DigitalFootprintScanner/1.0; +https://github.com/yourrepo)"
}

# -------------------------------
# Platform-specific NOT FOUND fingerprints
# -------------------------------
NOT_FOUND_PATTERNS = {
    "github": ["not found", "404"],
    "twitter": ["this account doesn’t exist", "account suspended"],
    "instagram": ["sorry, this page isn't available"],
    "facebook": ["content isn't available", "page isn't available"],
    "reddit": ["page not found", "nobody on reddit goes by that name"],
    "linkedin": ["profile not found", "this page doesn’t exist"],
    "medium": ["page not found", "whoops"],
    "stackoverflow": ["user does not exist"],
    "devto": ["page not found"],
    "pinterest": ["sorry! we couldn't find that page"]
}

# -------------------------------
# Default scanning settings
# -------------------------------
DEFAULT_TIMEOUT = 10        # seconds
DEFAULT_MAX_PLATFORMS = len(SUPPORTED_PLATFORMS)
DEFAULT_REQUEST_DELAY = 0.6 # seconds


# -------------------------------
# Scan Username Across Platforms
# -------------------------------
def scan_username(
    username: str,
    platforms: list = None,
    max_platforms: int = None,
    timeout: int = None,
    request_delay: float = None
) -> list:
    """
    Scan the given username across multiple platforms using real OSINT logic

    Args:
        username (str): Username to scan
        platforms (list): List of platforms to scan (defaults to SUPPORTED_PLATFORMS)
        max_platforms (int): Maximum platforms to scan
        timeout (int): HTTP request timeout in seconds
        request_delay (float): Delay between requests (ethical scanning)

    Returns:
        list of dict: [{'platform': platform_name, 'url': profile_url, 'status': found/not_found/error}]
    """
    platforms = platforms or SUPPORTED_PLATFORMS
    max_platforms = max_platforms or DEFAULT_MAX_PLATFORMS
    timeout = timeout or DEFAULT_TIMEOUT
    request_delay = request_delay or DEFAULT_REQUEST_DELAY

    results = []
    scanned_count = 0

    logging.info(f"Starting real username scan for '{username}'")

    for platform in platforms:
        if scanned_count >= max_platforms:
            break

        profile_url = generate_profile_url(platform, username)
        if not profile_url:
            results.append({
                "platform": platform,
                "url": "",
                "status": "invalid_platform"
            })
            continue

        try:
            response = requests.get(profile_url, headers=HEADERS, timeout=timeout, allow_redirects=True)
            html = response.text.lower()
            not_found_signals = NOT_FOUND_PATTERNS.get(platform, [])

            if any(signal.lower() in html for signal in not_found_signals):
                status = "not_found"
                logging.info(f"[{platform}] Username '{username}' NOT FOUND")
            elif response.status_code == 200:
                status = "found"
                logging.info(f"[{platform}] Username '{username}' FOUND")
            else:
                status = f"unknown_status_{response.status_code}"
                logging.warning(f"[{platform}] Unknown response status {response.status_code}")

        except requests.exceptions.Timeout:
            status = "timeout"
            logging.error(f"[{platform}] Timeout for username '{username}'")
        except requests.exceptions.RequestException as e:
            status = "error"
            logging.error(f"[{platform}] Request exception: {e}")

        results.append({
            "platform": platform,
            "url": profile_url,
            "status": status
        })

        scanned_count += 1
        time.sleep(request_delay)  # ethical delay

    logging.info(f"Completed scan for username '{username}'")
    return results


# -------------------------------
# For backward compatibility
# If some older imports use 'check_username_presence'
check_username_presence = scan_username


# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    username_to_scan = "subham123"
    scan_results = scan_username(username_to_scan)
    for r in scan_results:
        print(f"{r['platform']}: {r['status']} -> {r['url']}")
