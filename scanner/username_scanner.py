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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# -------------------------------
# STATUS-ONLY PLATFORMS
# Facebook, LinkedIn, Instagram, GitHub (and similar) often return 200 with login
# walls or generic pages that contain "page not found" / "content not available"
# in footers/UI. HTML fingerprinting causes FALSE NEGATIVES (existing accounts
# marked "not found"). For these, we use ONLY HTTP status: 200 = found, 404 = not_found.
# -------------------------------
STATUS_ONLY_PLATFORMS = frozenset({
    "facebook",
    "linkedin",
    "instagram",
    "github",
})

# -------------------------------
# Platform-specific NOT FOUND fingerprints (used only when NOT status-only)
# Must be specific to avoid false positives. Generic phrases in footers excluded.
# -------------------------------
NOT_FOUND_PATTERNS = {
    "twitter": ["this account doesn't exist", "account suspended", "we couldn't find that account"],
    "reddit": ["nobody on reddit goes by that name", "sorry, nobody on reddit goes by that name"],
    "medium": ["whoops", "this page doesn't exist"],
    "stackoverflow": ["user does not exist"],
    "devto": ["the page you were looking for doesn't exist"],
    "pinterest": ["sorry! we couldn't find that page"],
    "youtube": ["this channel doesn't exist", "sorry, we can't find that page", "404"],  # ✅ FIXED: Better YouTube detection
    "tiktok": ["couldn't find this account", "user not found"],
    "twitch": ["channel does not exist", "sorry. unless you've got a time machine"],
    "imgur": ["oops we couldn't find that page"],
    "spotify": ["couldn't find that user"],
}

# -------------------------------
# Default scanning settings
# -------------------------------
DEFAULT_TIMEOUT = 5         # seconds (optimized for speed - reduced from 8)
DEFAULT_MAX_PLATFORMS = len(SUPPORTED_PLATFORMS)
DEFAULT_REQUEST_DELAY = 0.1 # seconds (reduced from 0.3 for much faster scanning)


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
            status_code = response.status_code

            # Status-only platforms: login walls / generic 200 pages often contain
            # "not found" phrases. Use ONLY HTTP status to avoid false "not found".
            if platform.lower() in STATUS_ONLY_PLATFORMS:
                if status_code == 200:
                    status = "found"
                    logging.info(f"[{platform}] Username '{username}' FOUND (200)")
                elif status_code == 404:
                    status = "not_found"
                    logging.info(f"[{platform}] Username '{username}' NOT FOUND (404)")
                else:
                    status = f"unknown_status_{status_code}"
                    logging.warning(f"[{platform}] Status {status_code} for '{username}'")
            else:
                # Use HTML fingerprinting only for platforms that return distinct pages
                html = response.text.lower()
                not_found_signals = NOT_FOUND_PATTERNS.get(platform, [])

                if status_code == 404:
                    status = "not_found"
                    logging.info(f"[{platform}] Username '{username}' NOT FOUND (404)")
                elif not_found_signals and any(s in html for s in not_found_signals):
                    status = "not_found"
                    logging.info(f"[{platform}] Username '{username}' NOT FOUND (fingerprint)")
                elif status_code == 200:
                    status = "found"
                    logging.info(f"[{platform}] Username '{username}' FOUND")
                else:
                    status = f"unknown_status_{status_code}"
                    logging.warning(f"[{platform}] Status {status_code} for '{username}'")

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
