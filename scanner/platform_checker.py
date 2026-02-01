"""
Platform Checker for AI-Powered Digital Footprint Scanner
-----------------------------------------------------------
Responsibilities:
- Define all supported platforms for ethical username scanning
- Check if a username exists on a platform
- Provide utilities for the OSINT scanner and dashboard
"""

import requests
import time
import logging
from typing import Dict, List

# ---------------------------
# Logging Setup
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PLATFORM CHECKER] %(levelname)s: %(message)s"
)

# ---------------------------
# Supported Platforms
# ---------------------------
SUPPORTED_PLATFORMS: List[str] = [
    "github",
    "twitter",
    "linkedin",
    "instagram",
    "facebook",
    "reddit",
    "medium",
    "stackoverflow",
    "devto",
    "pinterest",
    "youtube",
    "tiktok",
    "twitch",
    "imgur",
    "spotify",
]

# ---------------------------
# Platform URL Patterns (real, working URLs for OSINT)
# YouTube uses @username format for channels
# ---------------------------
PLATFORM_URL_PATTERNS: Dict[str, str] = {
    "github": "https://github.com/{}",
    "twitter": "https://x.com/{}",
    "linkedin": "https://www.linkedin.com/in/{}",
    "instagram": "https://www.instagram.com/{}/",
    "facebook": "https://www.facebook.com/{}",
    "reddit": "https://www.reddit.com/user/{}",
    "medium": "https://medium.com/@{}",
    "stackoverflow": "https://stackoverflow.com/users/{}",
    "devto": "https://dev.to/{}",
    "pinterest": "https://www.pinterest.com/{}",
    "youtube": "https://www.youtube.com/@{}",  # ✅ FIXED: YouTube channels use @username format
    "tiktok": "https://www.tiktok.com/@{}",   # ✅ FIXED: TikTok also uses @username
    "twitch": "https://www.twitch.tv/{}",
    "imgur": "https://imgur.com/user/{}",
    "spotify": "https://open.spotify.com/user/{}",
}

# ---------------------------
# Request Headers (browser-like for fewer blocks)
# ---------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Ethical delay (seconds)
REQUEST_DELAY = 1


# ---------------------------
# Platform Availability Check (🔥 REQUIRED FIX)
# ---------------------------
def is_platform_available(platform: str) -> bool:
    """
    Check whether a platform is supported by the scanner.
    REQUIRED by scanner.__init__ and osint_scanner
    """
    return platform.lower() in PLATFORM_URL_PATTERNS


# ---------------------------
# Generate Profile URL
# ---------------------------
def generate_profile_url(platform: str, username: str) -> str | None:
    """
    Generate profile URL for a platform + username
    """
    platform = platform.lower()
    if not is_platform_available(platform):
        return None
    return PLATFORM_URL_PATTERNS[platform].format(username)


# ---------------------------
# Username Presence Check
# ---------------------------
def is_username_present(platform: str, username: str, timeout: int = 5) -> bool:
    """
    Check if a username exists on a given platform
    """
    platform = platform.lower()

    if not is_platform_available(platform):
        logging.warning(f"Unsupported platform: {platform}")
        return False

    url = generate_profile_url(platform, username)

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=True,
        )

        exists = response.status_code == 200

        # Extra validation for some platforms
        if platform in {"linkedin", "instagram", "facebook"}:
            page_text = response.text.lower()
            if "page not found" in page_text or "doesn't exist" in page_text:
                exists = False

        logging.info(f"{platform} | {username} | exists={exists}")
        time.sleep(REQUEST_DELAY)
        return exists

    except requests.RequestException as e:
        logging.error(f"{platform} | {username} | error: {e}")
        return False


# ---------------------------
# Scan Username Across Platforms
# ---------------------------
def scan_username_all_platforms(
    username: str,
    platforms: List[str] | None = None,
    max_platforms: int | None = None,
    timeout: int = 5,
) -> Dict[str, bool]:
    """
    Scan a username across multiple platforms
    """
    platforms = platforms or SUPPORTED_PLATFORMS
    max_platforms = max_platforms or len(platforms)

    results: Dict[str, bool] = {}
    scanned = 0

    for platform in platforms:
        if scanned >= max_platforms:
            break

        results[platform] = is_username_present(platform, username, timeout)
        scanned += 1

    return results


# ---------------------------
# Platform Reachability Check
# ---------------------------
def check_all_platforms_available(timeout: int = 5) -> Dict[str, bool]:
    """
    Check if platforms are reachable (basic health check)
    """
    results = {}

    for platform in SUPPORTED_PLATFORMS:
        try:
            test_url = generate_profile_url(platform, "example")
            r = requests.get(test_url, headers=HEADERS, timeout=timeout)
            results[platform] = r.status_code == 200
            time.sleep(REQUEST_DELAY)
        except requests.RequestException:
            results[platform] = False

    return results


# ---------------------------
# Manual Test
# ---------------------------
if __name__ == "__main__":
    test_username = "subham123"
    print(f"Scanning username: {test_username}")
    scan_results = scan_username_all_platforms(test_username)
    for platform, found in scan_results.items():
        print(f"{platform}: {'Found' if found else 'Not Found'}")
