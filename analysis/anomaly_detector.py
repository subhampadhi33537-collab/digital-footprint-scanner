"""
Advanced Anomaly Detection Engine
==================================
Detects unusual patterns, behaviors, and potential threats in digital footprints
using statistical and pattern-recognition techniques
"""

import logging
import math
from typing import Dict, List, Tuple
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ANOMALY DETECTION] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Advanced anomaly detection using statistical methods and heuristics
    """
    
    def __init__(self):
        self.detection_timestamp = datetime.now().isoformat()
        logger.info("🔍 Anomaly Detector initialized")

    def detect_all_anomalies(self, scan_results: Dict) -> Dict:
        """
        Run comprehensive anomaly detection

        Returns:
            {
                'anomalies': [...],
                'severity': 'LOW' | 'MEDIUM' | 'HIGH',
                'suspicious_patterns': [...],
                'threat_indicators': {...},
                'impersonation_risk': 0-100,
                'bot_likelihood': 0-100,
            }
        """
        logger.info("⚙️ Running comprehensive anomaly detection...")
        
        anomalies = []
        threat_indicators = {}
        
        # Run detection engines
        anomalies.extend(self._detect_platform_anomalies(scan_results))
        anomalies.extend(self._detect_username_anomalies(scan_results))
        anomalies.extend(self._detect_temporal_anomalies(scan_results))
        anomalies.extend(self._detect_correlation_anomalies(scan_results))
        
        # Calculate threat scores
        impersonation_risk = self._calculate_impersonation_risk(scan_results)
        bot_likelihood = self._calculate_bot_likelihood(scan_results)
        suspicious_patterns = self._identify_suspicious_patterns(scan_results)
        
        # Calculate overall severity
        severity = self._calculate_severity(len(anomalies), impersonation_risk, bot_likelihood)
        
        result = {
            "anomalies": anomalies,
            "severity": severity,
            "suspicious_patterns": suspicious_patterns,
            "threat_indicators": {
                "impersonation_risk": impersonation_risk,
                "bot_likelihood": bot_likelihood,
                "account_coordination": self._calculate_account_coordination(scan_results),
            },
            "timestamp": self.detection_timestamp,
            "total_anomalies": len(anomalies),
        }
        
        logger.info(f"✅ Anomaly detection complete: {len(anomalies)} anomalies found")
        return result

    def _detect_platform_anomalies(self, scan_results: Dict) -> List[str]:
        """Detect anomalies in platform distribution"""
        anomalies = []
        platforms_found = scan_results.get("all_platforms_checked", [])
        found = [p for p in platforms_found if p.get("status") == "found"]
        
        if not found:
            return anomalies
        
        # Anomaly: Only niche/underground platforms
        niche_platforms = {"reddit", "4chan", "imgur", "imgur", "devto"}
        niche_count = sum(1 for p in found if p.get("platform", "").lower() in niche_platforms)
        
        if niche_count == len(found) and len(found) > 0:
            anomalies.append("🔴 Only niche platforms detected - May indicate privacy focus or anonymity-seeking behavior")
        
        # Anomaly: Professional + Entertainment mix (unusual combination)
        pro_platforms = {"linkedin", "github", "stackoverflow"}
        ent_platforms = {"tiktok", "twitch"}
        
        pro_count = sum(1 for p in found if p.get("platform", "").lower() in pro_platforms)
        ent_count = sum(1 for p in found if p.get("platform", "").lower() in ent_platforms)
        
        if pro_count > 0 and ent_count > 0 and len(found) > 6:
            anomalies.append("🟡 Mixed professional and entertainment platforms - Unusual activity pattern detected")
        
        # Anomaly: Geographic/language suspicious patterns
        error_platforms = [p for p in platforms_found if p.get("status") in ["error", "timeout"]]
        if len(error_platforms) > 6:
            anomalies.append("🔴 Multiple platform errors - May indicate geographic blocking or bot detection")
        
        return anomalies

    def _detect_username_anomalies(self, scan_results: Dict) -> List[str]:
        """Detect anomalies in username patterns"""
        anomalies = []
        username = scan_results.get("user_input", "").lower()
        
        if not username:
            return anomalies
        
        # Anomaly: Suspiciously simple username
        if len(username) < 4:
            anomalies.append("🟡 Very short username - May be impersonating or generic account")
        
        # Anomaly: Only numbers (suspicious)
        if username.replace("@gmail.com", "").replace(".", "").isdigit():
            anomalies.append("🔴 Numeric-only username - Typical of auto-generated or bot accounts")
        
        # Anomaly: Special patterns
        if username.count("_") > 2 or username.count(".") > 2:
            anomalies.append("🟡 Excessive special characters - May indicate multiple accounts or obfuscation")
        
        return anomalies

    def _detect_temporal_anomalies(self, scan_results: Dict) -> List[str]:
        """Detect temporal anomalies (if we had account creation dates)"""
        anomalies = []
        
        # This would require account metadata which we don't have yet
        # Placeholder for future enhancement with API integrations
        
        return anomalies

    def _detect_correlation_anomalies(self, scan_results: Dict) -> List[str]:
        """Detect anomalies in account correlation patterns"""
        anomalies = []
        platforms_found = scan_results.get("all_platforms_checked", [])
        found = [p for p in platforms_found if p.get("status") == "found"]
        
        # Anomaly: Perfect correlation (identical username everywhere)
        if len(found) >= 5:
            # If we see the exact same username on 5+ major platforms, it's either:
            # 1. A real person (normal)
            # 2. An impersonator (suspicious)
            # 3. A brand account (normal)
            anomalies.append("🟡 High username correlation - Account easily linked across platforms")
        
        # Anomaly: No correlation (different usernames or patterns)
        if len(found) >= 3 and len(found) < 5:
            anomalies.append("🟡 Low account correlation - May indicate privacy consciousness")
        
        return anomalies

    def _calculate_impersonation_risk(self, scan_results: Dict) -> int:
        """
        Calculate risk of impersonation (0-100)
        Higher = more likely to be impersonated
        """
        risk = 0
        
        # Risk factors
        platforms_found = scan_results.get("all_platforms_checked", [])
        found = [p for p in platforms_found if p.get("status") == "found"]
        
        # Celebrity/common names are more likely to be impersonated
        # Check if it matches known patterns
        username = scan_results.get("user_input", "").lower()
        common_patterns = ["admin", "test", "user", "demo", "john", "jane"]
        
        if any(pattern in username for pattern in common_patterns):
            risk += 30  # Higher impersonation risk
        
        # Presence on social media + no verification = higher risk
        social_platforms = {"twitter", "instagram", "facebook", "tiktok"}
        social_count = sum(1 for p in found if p.get("platform", "").lower() in social_platforms)
        
        if social_count >= 2:
            risk += 20
        
        # Missing professional verification (no LinkedIn/GitHub) = higher risk
        if "linkedin" not in [p.get("platform", "").lower() for p in found]:
            if len(found) >= 2:
                risk += 15
        
        return min(risk, 100)

    def _calculate_bot_likelihood(self, scan_results: Dict) -> int:
        """
        Calculate likelihood of being a bot (0-100)
        Higher = more likely bot activity
        """
        likelihood = 0
        
        platforms_found = scan_results.get("all_platforms_checked", [])
        found = [p for p in platforms_found if p.get("status") == "found"]
        
        # Bot indicators
        
        # Indicator 1: Too many accounts (>10)
        if len(found) > 10:
            likelihood += 30
        
        # Indicator 2: Only entertainment platforms
        entertainment = {"twitch", "tiktok", "youtube", "spotify"}
        if len(found) > 0 and all(p.get("platform", "").lower() in entertainment for p in found):
            likelihood += 20
        
        # Indicator 3: Perfect numeric or generic username
        username = scan_results.get("user_input", "").lower()
        if username.replace("@gmail.com", "").replace(".", "").isdigit():
            likelihood += 25
        
        # Indicator 4: Account errors/blocks on multiple platforms
        errors = [p for p in platforms_found if p.get("status") in ["error"]]
        if len(errors) > 4:
            likelihood += 15
        
        return min(likelihood, 100)

    def _calculate_account_coordination(self, scan_results: Dict) -> float:
        """
        Calculate how coordinated the accounts are (0-100)
        Higher = accounts are well-managed and consistent
        """
        platforms_found = scan_results.get("all_platforms_checked", [])
        found = [p for p in platforms_found if p.get("status") == "found"]
        
        if not found:
            return 0
        
        # More platforms with consistent username = better coordination
        coordination = (len(found) / 15) * 100  # Normalize to 15 platforms
        
        # High coordination suggests either real person or sophisticated operation
        return round(coordination, 1)

    def _identify_suspicious_patterns(self, scan_results: Dict) -> List[str]:
        """Identify suspicious behavioral patterns"""
        patterns = []
        platforms_found = scan_results.get("all_platforms_checked", [])
        found = [p for p in platforms_found if p.get("status") == "found"]
        
        # Pattern 1: Selective social media (only mainstream)
        mainstream = {"facebook", "instagram", "twitter"}
        if len(found) >= 2 and all(p.get("platform", "").lower() in mainstream for p in found):
            patterns.append("Mainstream social media only - Standard consumer behavior")
        
        # Pattern 2: Technical focus
        technical = {"github", "stackoverflow", "devto"}
        tech_count = sum(1 for p in found if p.get("platform", "").lower() in technical)
        if tech_count >= 2:
            patterns.append("Strong technical presence - Developer or tech professional")
        
        # Pattern 3: Creator/Content focus
        creators = {"youtube", "twitch", "medium", "devto"}
        creator_count = sum(1 for p in found if p.get("platform", "").lower() in creators)
        if creator_count >= 2:
            patterns.append("Content creator profile - Likely monetized presence")
        
        # Pattern 4: Privacy-conscious
        if len(found) < 3 and len(platforms_found) >= 10:
            patterns.append("Privacy-focused - Selective platform usage despite testing multiple")
        
        return patterns

    def _calculate_severity(self, anomaly_count: int, impersonation_risk: int, bot_likelihood: int) -> str:
        """Calculate overall severity of detected anomalies"""
        # Weighted scoring
        score = (anomaly_count * 10) + (impersonation_risk * 0.3) + (bot_likelihood * 0.3)
        
        if score > 60:
            return "HIGH"
        elif score > 30:
            return "MEDIUM"
        else:
            return "LOW"


class BreachDetector:
    """
    Check if email appears in known breaches
    Requires integration with breach databases
    """
    
    def __init__(self):
        logger.info("💾 Breach Detector initialized")
    
    def check_breach_status(self, email: str) -> Dict:
        """
        Check if email appears in known breaches
        Placeholder - requires actual API integration (e.g., Have I Been Pwned)
        """
        # TODO: Integrate with actual breach database API
        
        return {
            "is_breached": False,
            "breach_count": 0,
            "breaches": [],
            "note": "Breach checking requires API integration"
        }


def get_comprehensive_anomaly_analysis(scan_results: Dict) -> Dict:
    """
    Main function to get comprehensive anomaly analysis
    """
    detector = AnomalyDetector()
    anomalies = detector.detect_all_anomalies(scan_results)
    
    return {
        "anomalies": anomalies,
        "timestamp": datetime.now().isoformat(),
    }
