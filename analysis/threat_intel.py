"""
Advanced Threat Intelligence Engine
====================================
Provides sophisticated threat analysis, correlation intelligence,
and actionable security insights using Groq API
"""

import logging
from typing import Dict, List
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [THREAT INTEL] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class ThreatIntelligenceEngine:
    """
    Advanced threat intelligence using Groq LLM for deep analysis
    """
    
    def __init__(self, groq_client=None):
        self.groq_client = groq_client
        logger.info("🛡️ Threat Intelligence Engine initialized")

    def generate_threat_report(self, scan_data: Dict, ml_scores: Dict, anomalies: Dict) -> str:
        """
        Generate comprehensive threat intelligence report using Groq

        Args:
            scan_data: Raw scan results
            ml_scores: ML risk analysis
            anomalies: Anomaly detection results

        Returns:
            Comprehensive threat intelligence report
        """
        if not self.groq_client:
            logger.warning("Groq client not available")
            return self._generate_fallback_report(scan_data, ml_scores, anomalies)

        platforms_found = [
            p.get("platform") for p in scan_data.get("all_platforms_checked", [])
            if p.get("status") == "found"
        ]
        
        anomaly_list = anomalies.get("anomalies", {}).get("anomalies", [])
        
        prompt = f"""Generate a professional security threat intelligence report:

DIGITAL FOOTPRINT ANALYSIS:
- Username: {scan_data.get('user_input', 'Unknown')}
- Platforms Found: {', '.join(platforms_found) if platforms_found else 'None'}
- ML Risk Score: {ml_scores.get('ml_risk_score', 0)}/100
- Risk Level: {ml_scores.get('risk_level', 'UNKNOWN')}
- Anomalies: {len(anomaly_list)} detected

THREAT ASSESSMENT REQUIRED:
1. Executive Summary (1 sentence threat level)
2. Key Risk Factors (3 main vulnerabilities)
3. Attack Surface Analysis (how attacker could exploit this)
4. Recommended Mitigations (3 priority actions)
5. Monitoring Strategy (what to watch for)

Format: Professional, concise, actionable
Target Audience: Security professional or individual
Keep under 400 words."""

        try:
            report = self.groq_client.generate_text(prompt, max_tokens=400)
            logger.info("✅ Threat intelligence report generated")
            return report
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return self._generate_fallback_report(scan_data, ml_scores, anomalies)

    def _generate_fallback_report(self, scan_data: Dict, ml_scores: Dict, anomalies: Dict) -> str:
        """Fallback report when Groq is unavailable"""
        risk_level = ml_scores.get("risk_level", "UNKNOWN")
        score = ml_scores.get("ml_risk_score", 0)
        
        return f"""THREAT INTELLIGENCE REPORT
Generated: {datetime.now().isoformat()}

EXECUTIVE SUMMARY:
Risk Level: {risk_level} (Score: {score}/100)

KEY FINDINGS:
- Exposure across multiple platforms detected
- Digital footprint correlation possible
- Privacy settings require review

RECOMMENDATIONS:
1. Enable 2FA on critical accounts
2. Review platform privacy settings
3. Monitor account access regularly"""

    def detect_impersonation_patterns(self, scan_data: Dict) -> Dict:
        """
        Detect patterns suggesting account impersonation
        """
        patterns = []
        
        platforms = scan_data.get("all_platforms_checked", [])
        found = [p for p in platforms if p.get("status") == "found"]
        
        # Pattern detection logic
        if len(found) > 8 and all(p.get("status") == "found" for p in found[:8]):
            patterns.append("High saturation attack pattern detected")
        
        return {
            "impersonation_patterns": patterns,
            "impersonation_risk": len(patterns) > 0,
            "detection_timestamp": datetime.now().isoformat(),
        }

    def identify_correlation_vectors(self, scan_data: Dict) -> List[Dict]:
        """
        Identify how accounts can be correlated and linked together
        """
        correlation_vectors = []
        
        platforms = scan_data.get("all_platforms_checked", [])
        found = [p for p in platforms if p.get("status") == "found"]
        
        if len(found) >= 2:
            # Vector 1: Username correlation
            correlation_vectors.append({
                "vector": "Username Correlation",
                "risk": "HIGH" if len(found) >= 5 else "MEDIUM",
                "description": f"Accounts linkable via identical username across {len(found)} platforms",
                "mitigation": "Use different usernames on sensitive platforms"
            })
        
        # Vector 2: Email correlation (if found)
        emails = scan_data.get("emails_found", [])
        if emails and len(found) >= 2:
            correlation_vectors.append({
                "vector": "Email Correlation",
                "risk": "HIGH",
                "description": f"Email linked to {len(found)} social accounts",
                "mitigation": "Use separate emails for different account types"
            })
        
        # Vector 3: Profile information correlation
        names = scan_data.get("names_found", [])
        if names and len(found) >= 3:
            correlation_vectors.append({
                "vector": "Profile Information",
                "risk": "MEDIUM",
                "description": f"Name '{names[0]}' appears in profiles",
                "mitigation": "Use pseudonyms or nicknames on some platforms"
            })
        
        return correlation_vectors

    def calculate_data_exposure_impact(self, scan_data: Dict, ml_scores: Dict) -> Dict:
        """
        Calculate impact of exposed data
        """
        platform_risks = ml_scores.get("ml_analysis", {}).get("platform_risks", {})
        
        total_exposure = 0
        sensitive_exposure = 0
        
        sensitive_platforms = {"facebook": 95, "linkedin": 90, "github": 70}
        
        for platform, risk in platform_risks.items():
            if risk.get("status") == "FOUND":
                total_exposure += risk.get("sensitivity", 50)
                if platform in sensitive_platforms:
                    sensitive_exposure += sensitive_platforms[platform]
        
        return {
            "total_exposure_score": round(total_exposure / 15 * 100, 1),  # Normalize
            "sensitive_exposure_score": round(sensitive_exposure / 300 * 100, 1),  # 3 platforms max
            "exposure_summary": self._generate_exposure_summary(scan_data),
            "data_types_exposed": self._identify_exposed_data_types(scan_data),
        }

    def _identify_exposed_data_types(self, scan_data: Dict) -> List[str]:
        """Identify what types of data are exposed"""
        exposed = []
        
        platforms = scan_data.get("all_platforms_checked", [])
        found = [p for p in platforms if p.get("status") == "found"]
        
        # Data type identification
        platform_names = {p.get("platform", "").lower() for p in found}
        
        if any(p in platform_names for p in ["facebook", "instagram", "twitter"]):
            exposed.append("Personal information (name, profile)")
        
        if "github" in platform_names:
            exposed.append("Code repositories and projects")
        
        if "linkedin" in platform_names:
            exposed.append("Professional history and skills")
        
        if any(p in platform_names for p in ["instagram", "twitter", "tiktok"]):
            exposed.append("Location hints and travel patterns")
        
        if "spotify" in platform_names:
            exposed.append("Music preferences and behavioral patterns")
        
        if any(p in platform_names for p in ["twitch", "youtube"]):
            exposed.append("Content consumption history")
        
        return exposed

    def _generate_exposure_summary(self, scan_data: Dict) -> str:
        """Generate exposure summary text"""
        platforms = scan_data.get("all_platforms_checked", [])
        found_count = sum(1 for p in platforms if p.get("status") == "found")
        
        if found_count == 0:
            return "No significant exposure detected"
        elif found_count <= 2:
            return "Limited online presence with minimal exposure"
        elif found_count <= 5:
            return "Moderate online presence with exposure across multiple platforms"
        else:
            return "Extensive online presence with high exposure across many platforms"


class SecurityRecommendationEngine:
    """
    Generate personalized security recommendations
    """
    
    def __init__(self):
        logger.info("💡 Security Recommendation Engine initialized")

    def generate_recommendations(self, scan_data: Dict, ml_scores: Dict, threat_data: Dict) -> List[Dict]:
        """
        Generate prioritized security recommendations
        """
        recommendations = []
        
        risk_level = ml_scores.get("ml_analysis", {}).get("risk_level", "LOW")
        platforms = scan_data.get("all_platforms_checked", [])
        found = [p for p in platforms if p.get("status") == "found"]
        
        # Immediate actions (Priority 1)
        if risk_level in ["CRITICAL", "HIGH"]:
            recommendations.append({
                "priority": 1,
                "action": "Enable Two-Factor Authentication (2FA)",
                "platforms": [p.get("platform", "").upper() for p in found[:3]],
                "impact": "HIGH",
                "implementation_time": "15 minutes",
                "details": "2FA significantly reduces account takeover risk"
            })
            
            recommendations.append({
                "priority": 1,
                "action": "Audit Account Recovery Options",
                "platforms": ["All"],
                "impact": "HIGH",
                "implementation_time": "10 minutes",
                "details": "Verify email and phone numbers are current and secure"
            })
        
        # Medium-term actions (Priority 2)
        if len(found) > 5:
            recommendations.append({
                "priority": 2,
                "action": "Consolidate Online Presence",
                "platforms": [p.get("platform", "").upper() for p in found[5:]],
                "impact": "MEDIUM",
                "implementation_time": "1-2 hours",
                "details": "Deactivate unused accounts to reduce attack surface"
            })
        
        # Long-term strategy (Priority 3)
        recommendations.append({
            "priority": 3,
            "action": "Implement Privacy-First Practices",
            "platforms": ["All"],
            "impact": "MEDIUM",
            "implementation_time": "Ongoing",
            "details": "Regular audits, limit personal info sharing, use unique passwords"
        })
        
        return recommendations[:10]  # Return top 10


def get_complete_threat_intelligence(scan_data: Dict, ml_scores: Dict, anomalies: Dict, groq_client=None) -> Dict:
    """
    Generate complete threat intelligence package
    """
    engine = ThreatIntelligenceEngine(groq_client)
    rec_engine = SecurityRecommendationEngine()
    
    return {
        "threat_report": engine.generate_threat_report(scan_data, ml_scores, anomalies),
        "impersonation_patterns": engine.detect_impersonation_patterns(scan_data),
        "correlation_vectors": engine.identify_correlation_vectors(scan_data),
        "data_exposure": engine.calculate_data_exposure_impact(scan_data, ml_scores),
        "security_recommendations": rec_engine.generate_recommendations(scan_data, ml_scores, None),
        "timestamp": datetime.now().isoformat(),
    }
