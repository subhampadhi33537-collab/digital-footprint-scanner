#!/usr/bin/env python3
"""
Test script to verify real scan results display on dashboard
Run this to test: python test_display.py
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from routes import transform_scan_for_js

# Example scan result from real scanning
REAL_SCAN_RESULT = {
    "user_input": "subhampadhi33537@gmail.com",
    "username_extracted": "subhampadhi33537",
    "names_found": ["Subham Padhi"],
    "emails_found": [
        {"email": "subhampadhi33537@gmail.com", "type": "primary", "status": "found"}
    ],
    "platforms_found": ["Twitter", "Instagram", "Pinterest", "Twitch", "Imgur", "Spotify"],
    "platform_links": [],
    "all_platforms_checked": [
        {"platform": "github", "url": "https://github.com/subhampadhi33537", "status": "not_found"},
        {"platform": "twitter", "url": "https://twitter.com/subhampadhi33537", "status": "found"},
        {"platform": "linkedin", "url": "https://linkedin.com/in/subhampadhi33537", "status": "error"},
        {"platform": "instagram", "url": "https://instagram.com/subhampadhi33537", "status": "found"},
        {"platform": "facebook", "url": "https://facebook.com/subhampadhi33537", "status": "error"},
        {"platform": "reddit", "url": "https://reddit.com/user/subhampadhi33537", "status": "error"},
        {"platform": "medium", "url": "https://medium.com/@subhampadhi33537", "status": "error"},
        {"platform": "stackoverflow", "url": "https://stackoverflow.com/users/subhampadhi33537", "status": "not_found"},
        {"platform": "devto", "url": "https://dev.to/subhampadhi33537", "status": "not_found"},
        {"platform": "pinterest", "url": "https://pinterest.com/subhampadhi33537", "status": "found"},
        {"platform": "youtube", "url": "https://youtube.com/@subhampadhi33537", "status": "not_found"},
        {"platform": "tiktok", "url": "https://tiktok.com/@subhampadhi33537", "status": "timeout"},
        {"platform": "twitch", "url": "https://twitch.tv/subhampadhi33537", "status": "found"},
        {"platform": "imgur", "url": "https://imgur.com/user/subhampadhi33537", "status": "found"},
        {"platform": "spotify", "url": "https://open.spotify.com/user/subhampadhi33537", "status": "found"}
    ]
}

REAL_RISK_RESULT = {
    "risk_level": "MEDIUM",
    "exposure_count": 8,
    "total_platforms": 15,
    "found_count": 6,
    "error_count": 4,
    "timeout_count": 1
}

def test_transform():
    """Test that transform function properly displays real results"""
    print("\n" + "="*70)
    print("TEST: Transform Scan Results to Dashboard Display")
    print("="*70)
    
    # Transform the results
    dashboard_payload = transform_scan_for_js(
        scan_results=REAL_SCAN_RESULT,
        risk_results=REAL_RISK_RESULT,
        user_input="subhampadhi33537@gmail.com"
    )
    
    # Display output
    print("\n📊 DASHBOARD PAYLOAD:\n")
    print(json.dumps(dashboard_payload, indent=2))
    
    # Verify structure
    print("\n" + "="*70)
    print("VERIFICATION RESULTS:")
    print("="*70)
    
    checks = [
        ("User input captured", dashboard_payload.get("user_input") == "subhampadhi33537@gmail.com"),
        ("Platforms list generated", len(dashboard_payload.get("platforms", [])) > 0),
        ("Risk level set", dashboard_payload.get("risk_level") == "MEDIUM"),
        ("Platform count correct", len(dashboard_payload.get("platforms", [])) == 15),
        ("Found platforms detected", len([p for p in dashboard_payload.get("platforms", []) if p.get("found")]) == 6),
        ("URLs populated", len([p for p in dashboard_payload.get("platforms", []) if p.get("url")]) == 15),
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check_name}")
        if not result:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED - Dashboard will display REAL results!")
    else:
        print("❌ SOME TESTS FAILED - Check the transform function")
    print("="*70 + "\n")
    
    # Show platform display sample
    print("\n📱 SAMPLE PLATFORM CARDS (as displayed on dashboard):\n")
    for platform in dashboard_payload.get("platforms", [])[:5]:
        found_status = "✅ FOUND" if platform.get("found") else "❌ NOT FOUND"
        print(f"  • {platform.get('name')}: {found_status}")
        if platform.get("url"):
            print(f"    URL: {platform.get('url')}")
    
    print("\n  ... and 10 more platforms\n")
    
    return all_passed

if __name__ == "__main__":
    success = test_transform()
    sys.exit(0 if success else 1)
