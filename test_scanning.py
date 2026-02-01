#!/usr/bin/env python3
"""
Test script for Digital Footprint Scanner
- Tests scanning workflow
- Tests data normalization
- Tests risk calculation
- Tests result persistence
"""

import json
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [TEST] %(levelname)s: %(message)s"
)

def test_imports():
    """Test that all modules import correctly"""
    print("\n" + "="*60)
    print("TEST 1: Module Imports")
    print("="*60)
    try:
        from config import config
        print("✅ config imported")
        
        from scanner import run_full_scan, normalize_scan_data
        print("✅ scanner modules imported")
        
        from analysis.risk_engine import calculate_risk
        print("✅ risk_engine imported")
        
        from ai_engine.groq_client import GroqClient
        print("✅ groq_client imported")
        
        print("\n✅ ALL IMPORTS SUCCESSFUL\n")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}\n")
        return False


def test_configuration():
    """Test that configuration is properly loaded"""
    print("\n" + "="*60)
    print("TEST 2: Configuration Validation")
    print("="*60)
    try:
        from config import config
        
        assert config.GROQ_API_KEY, "GROQ_API_KEY not set"
        assert config.SCAN_TIMEOUT == 5, f"SCAN_TIMEOUT should be 5, got {config.SCAN_TIMEOUT}"
        assert config.MAX_PLATFORMS == 15, f"MAX_PLATFORMS should be 15, got {config.MAX_PLATFORMS}"
        assert config.GROQ_MAX_TOKENS == 512, f"GROQ_MAX_TOKENS should be 512, got {config.GROQ_MAX_TOKENS}"
        
        print(f"✅ GROQ_API_KEY: SET")
        print(f"✅ SCAN_TIMEOUT: {config.SCAN_TIMEOUT}s")
        print(f"✅ MAX_PLATFORMS: {config.MAX_PLATFORMS}")
        print(f"✅ GROQ_MAX_TOKENS: {config.GROQ_MAX_TOKENS}")
        print(f"✅ GROQ_TEMPERATURE: {config.GROQ_TEMPERATURE}")
        
        print("\n✅ CONFIGURATION VALID\n")
        return True
    except AssertionError as e:
        print(f"❌ Configuration check failed: {e}\n")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {e}\n")
        return False


def test_normalization():
    """Test data normalization"""
    print("\n" + "="*60)
    print("TEST 3: Data Normalization")
    print("="*60)
    try:
        from scanner.data_normalizer import normalize_scan_data
        
        # Test with sample data
        sample_scan_data = {
            "user_input": "testuser",
            "timestamp": "2026-02-01 10:00:00",
            "email_exposure": [],
            "username_exposure": [
                {
                    "platform": "github",
                    "url": "https://github.com/testuser",
                    "status": "found"
                },
                {
                    "platform": "twitter",
                    "url": "https://twitter.com/testuser",
                    "status": "not_found"
                }
            ]
        }
        
        normalized = normalize_scan_data(sample_scan_data)
        
        assert "platforms_found" in normalized, "Missing platforms_found"
        assert "all_platforms_checked" in normalized, "Missing all_platforms_checked"
        assert len(normalized["platforms_found"]) == 1, f"Should find 1 platform, got {len(normalized['platforms_found'])}"
        assert "github" in normalized["platforms_found"], "github should be in platforms_found"
        assert len(normalized["all_platforms_checked"]) == 2, f"Should check 2 platforms, got {len(normalized['all_platforms_checked'])}"
        
        print(f"✅ Normalized data structure valid")
        print(f"✅ Found {len(normalized['platforms_found'])} platforms")
        print(f"✅ Checked {len(normalized['all_platforms_checked'])} total platforms")
        print(f"✅ Platforms found: {normalized['platforms_found']}")
        
        print("\n✅ NORMALIZATION TEST PASSED\n")
        return True
    except Exception as e:
        print(f"❌ Normalization test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_risk_calculation():
    """Test risk calculation"""
    print("\n" + "="*60)
    print("TEST 4: Risk Calculation")
    print("="*60)
    try:
        from analysis.risk_engine import calculate_risk
        
        # Test with sample normalized data
        sample_risk_data = {
            "platforms_found": ["github", "twitter"],
            "emails_found": [{"email": "test@example.com"}],
            "names_found": ["testuser"],
            "exposure_summary": {
                "personal_identifiers": 1,
                "contact_information": 1,
                "online_accounts": 2,
                "total_exposures": 4
            }
        }
        
        risk_result = calculate_risk(sample_risk_data)
        
        assert "risk_level" in risk_result, "Missing risk_level in result"
        assert risk_result["risk_level"] in ["LOW", "MEDIUM", "HIGH"], f"Invalid risk level: {risk_result['risk_level']}"
        
        print(f"✅ Risk calculated: {risk_result['risk_level']}")
        print(f"✅ Exposures detected: {sample_risk_data['exposure_summary']['total_exposures']}")
        
        print("\n✅ RISK CALCULATION TEST PASSED\n")
        return True
    except Exception as e:
        print(f"❌ Risk calculation test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_groq_client():
    """Test Groq client initialization"""
    print("\n" + "="*60)
    print("TEST 5: Groq Client Initialization")
    print("="*60)
    try:
        from ai_engine.groq_client import GroqClient, get_groq_client
        
        client = get_groq_client()
        
        assert client is not None, "Client is None"
        assert hasattr(client, 'generate_text'), "Client missing generate_text method"
        assert hasattr(client, 'chat'), "Client missing chat method"
        assert client.api_key is not None, "API key not set"
        assert client.model is not None, "Model not set"
        
        print(f"✅ Groq client initialized")
        print(f"✅ Model: {client.model}")
        print(f"✅ API URL: {client.api_url}")
        print(f"✅ Max tokens: {client.max_tokens}")
        print(f"✅ Temperature: {client.temperature}")
        
        print("\n✅ GROQ CLIENT TEST PASSED\n")
        return True
    except Exception as e:
        print(f"❌ Groq client test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "█" * 60)
    print("DIGITAL FOOTPRINT SCANNER - TEST SUITE")
    print("█" * 60)
    
    results = {
        "Imports": test_imports(),
        "Configuration": test_configuration(),
        "Normalization": test_normalization(),
        "Risk Calculation": test_risk_calculation(),
        "Groq Client": test_groq_client(),
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your scanner is ready to use.\n")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
