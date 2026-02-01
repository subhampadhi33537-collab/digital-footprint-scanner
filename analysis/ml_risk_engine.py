"""
Advanced ML Risk Analysis Engine
=================================
Uses machine learning and data science techniques to:
1. Score digital footprint risk with ML models
2. Detect anomalies in account patterns
3. Correlate accounts across platforms
4. Identify impersonation risks
5. Integrate with Groq API for advanced analysis
"""

import json
import logging
import math
from typing import Dict, List, Tuple
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ML ANALYSIS] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class MLRiskAnalyzer:
    """
    Advanced ML-based risk assessment and threat analysis
    """
    
    # Platform risk weights (based on data breach frequency and sensitivity)
    PLATFORM_RISK_WEIGHTS = {
        "twitter": 0.7,
        "instagram": 0.6,
        "facebook": 0.85,  # High breach history
        "reddit": 0.5,
        "medium": 0.4,
        "linkedin": 0.8,   # Contains professional data
        "github": 0.6,     # Can expose code/projects
        "youtube": 0.5,
        "tiktok": 0.65,
        "twitch": 0.55,
        "pinterest": 0.4,
        "spotify": 0.35,
        "imgur": 0.45,
        "stackoverflow": 0.6,
        "devto": 0.4,
    }
    
    # Platform sensitivity (how much personal data exposed)
    PLATFORM_SENSITIVITY = {
        "facebook": 0.95,   # Full personal profile
        "linkedin": 0.90,   # Professional + personal info
        "twitter": 0.75,    # Posts, location hints
        "instagram": 0.80,  # Photos, location
        "reddit": 0.60,     # Potentially anonymous
        "github": 0.70,     # Code, projects, interests
        "youtube": 0.65,    # Upload history, preferences
        "tiktok": 0.75,     # Videos, behavioral data
        "medium": 0.50,     # Articles, interests
        "twitch": 0.55,     # Stream history
        "pinterest": 0.50,  # Pin interests
        "spotify": 0.45,    # Music preferences
        "imgur": 0.40,      # Public uploads
        "stackoverflow": 0.55,  # Technical skills
        "devto": 0.50,      # Articles, interests
    }

    def __init__(self):
        """Initialize ML analyzer"""
        self.analysis_timestamp = datetime.now().isoformat()
        logger.info("🤖 ML Risk Analyzer initialized")

    def calculate_ml_risk_score(self, scan_results: Dict) -> Dict:
        """
        Calculate risk using ML-based scoring

        Args:
            scan_results: Full scan results from OSINT scanner

        Returns:
            {
                'ml_risk_score': 0-100,
                'risk_level': 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL',
                'confidence': 0-100,
                'platform_risks': {...},
                'anomalies': [...],
                'recommendations': [...]
            }
        """
        logger.info("⚙️ Calculating ML-based risk score...")

        platforms_found = scan_results.get("all_platforms_checked", [])
        found_count = sum(1 for p in platforms_found if p.get("status") == "found")
        
        # Feature extraction for ML model
        features = self._extract_features(scan_results)
        
        # ML scoring
        base_score = self._calculate_base_score(features)
        platform_risk_score = self._calculate_platform_risk(platforms_found)
        exposure_score = self._calculate_exposure_score(features)
        correlation_score = self._calculate_correlation_score(scan_results)
        
        # Weighted ensemble (ML model combination)
        ml_risk_score = (
            base_score * 0.25 +
            platform_risk_score * 0.35 +
            exposure_score * 0.25 +
            correlation_score * 0.15
        )
        
        # Confidence based on data quality
        confidence = self._calculate_confidence(features)
        
        # Risk level classification
        risk_level = self._classify_risk_level(ml_risk_score)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(scan_results, features)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            ml_risk_score, risk_level, anomalies, platforms_found
        )
        
        result = {
            "ml_risk_score": round(ml_risk_score, 2),
            "risk_level": risk_level,
            "confidence": round(confidence, 1),
            "platform_risks": self._get_platform_risks(platforms_found),
            "anomalies": anomalies,
            "recommendations": recommendations,
            "analysis_timestamp": self.analysis_timestamp,
            "features": features  # For debugging
        }
        
        logger.info(f"✅ ML Risk Score: {ml_risk_score:.1f}/100 ({risk_level})")
        return result

    def _extract_features(self, scan_results: Dict) -> Dict:
        """Extract ML features from scan results"""
        platforms_found = scan_results.get("all_platforms_checked", [])
        
        found_platforms = [p for p in platforms_found if p.get("status") == "found"]
        error_platforms = [p for p in platforms_found if p.get("status") in ["error", "timeout"]]
        
        features = {
            "total_platforms_scanned": len(platforms_found),
            "platforms_found": len(found_platforms),
            "platforms_not_found": len(platforms_found) - len(found_platforms),
            "error_count": len(error_platforms),
            "found_percentage": (len(found_platforms) / len(platforms_found) * 100) if platforms_found else 0,
            "platform_diversity": len(found_platforms),  # More platforms = higher risk
            "username_consistency": self._calculate_username_consistency(scan_results),
            "has_personal_info": len(scan_results.get("names_found", [])) > 0,
            "has_emails": len(scan_results.get("emails_found", [])) > 0,
            "platform_categories": self._categorize_platforms(found_platforms),
        }
        
        return features

    def _calculate_base_score(self, features: Dict) -> float:
        """Calculate base risk score from features"""
        score = 0
        
        # More platforms = higher risk (more places to be compromised)
        platforms_found = features.get("platforms_found", 0)
        score += min(platforms_found * 10, 50)  # Max 50 from platform count
        
        # High visibility across many categories
        categories = features.get("platform_categories", {})
        category_count = len([c for c in categories.values() if c > 0])
        score += min(category_count * 8, 25)  # Max 25 from diversity
        
        # Personal info exposure
        if features.get("has_personal_info"):
            score += 15
        if features.get("has_emails"):
            score += 10
            
        return min(score, 100)

    def _calculate_platform_risk(self, platforms_found: List[Dict]) -> float:
        """Calculate risk based on platform types"""
        if not platforms_found:
            return 0
        
        found_platforms = [p for p in platforms_found if p.get("status") == "found"]
        if not found_platforms:
            return 0
        
        total_risk = 0
        for platform in found_platforms:
            platform_name = platform.get("platform", "").lower()
            weight = self.PLATFORM_RISK_WEIGHTS.get(platform_name, 0.5)
            total_risk += weight * 10
        
        return min(total_risk / len(found_platforms), 100)

    def _calculate_exposure_score(self, features: Dict) -> float:
        """Calculate data exposure risk"""
        score = 0
        
        found_platforms = features.get("platforms_found", 0)
        
        # Sensitivity-weighted exposure
        for platform, sensitivity in self.PLATFORM_SENSITIVITY.items():
            if features.get("platform_categories", {}).get(platform, 0) > 0:
                score += sensitivity * 20
        
        # Username consistency increases risk (easy to correlate)
        consistency = features.get("username_consistency", 0)
        score += consistency * 15
        
        return min(score, 100)

    def _calculate_correlation_score(self, scan_results: Dict) -> float:
        """Calculate risk from account correlation"""
        platforms_found = scan_results.get("all_platforms_checked", [])
        found_platforms = [p for p in platforms_found if p.get("status") == "found"]
        
        if len(found_platforms) < 2:
            return 0
        
        # More platforms with same username = easier to correlate = higher risk
        correlation_risk = (len(found_platforms) / 15) * 100  # Normalize to 15 platforms max
        
        return min(correlation_risk, 100)

    def _calculate_username_consistency(self, scan_results: Dict) -> float:
        """
        Calculate how consistent the username is across platforms
        1.0 = identical username everywhere (highest risk)
        """
        platforms_found = scan_results.get("all_platforms_checked", [])
        found_platforms = [p for p in platforms_found if p.get("status") == "found"]
        
        if len(found_platforms) < 2:
            return 0.0
        
        # If found on many platforms with same base, consistency is high
        consistency = len(found_platforms) / 15  # Normalize
        return min(consistency, 1.0)

    def _categorize_platforms(self, found_platforms: List[Dict]) -> Dict[str, int]:
        """Categorize platforms by type"""
        categories = {
            "social_media": 0,
            "professional": 0,
            "developer": 0,
            "creative": 0,
            "entertainment": 0,
        }
        
        categorization = {
            "twitter": "social_media",
            "instagram": "social_media",
            "facebook": "social_media",
            "tiktok": "social_media",
            "reddit": "social_media",
            "linkedin": "professional",
            "github": "developer",
            "stackoverflow": "developer",
            "devto": "developer",
            "medium": "creative",
            "youtube": "entertainment",
            "twitch": "entertainment",
            "pinterest": "creative",
            "imgur": "creative",
            "spotify": "entertainment",
        }
        
        for platform in found_platforms:
            platform_name = platform.get("platform", "").lower()
            category = categorization.get(platform_name, "social_media")
            categories[category] += 1
        
        return categories

    def _classify_risk_level(self, score: float) -> str:
        """Classify risk level using ML thresholds"""
        if score < 25:
            return "LOW"
        elif score < 50:
            return "MEDIUM"
        elif score < 75:
            return "HIGH"
        else:
            return "CRITICAL"

    def _calculate_confidence(self, features: Dict) -> float:
        """Calculate confidence in risk assessment (0-100)"""
        confidence = 70  # Base confidence
        
        # More data = higher confidence
        if features.get("has_personal_info"):
            confidence += 10
        if features.get("has_emails"):
            confidence += 10
        
        # More platforms checked = higher confidence
        platforms_scanned = features.get("total_platforms_scanned", 15)
        confidence += (platforms_scanned / 15) * 10
        
        return min(confidence, 100)

    def _detect_anomalies(self, scan_results: Dict, features: Dict) -> List[str]:
        """Detect anomalies in digital footprint"""
        anomalies = []
        
        platforms_found = scan_results.get("all_platforms_checked", [])
        found_platforms = [p for p in platforms_found if p.get("status") == "found"]
        
        # Anomaly 1: No accounts found (unusual)
        if len(found_platforms) == 0:
            anomalies.append("No online presence detected - May indicate heavy privacy practices or pseudonym")
        
        # Anomaly 2: Too many accounts (potential spam/bot)
        if len(found_platforms) > 12:
            anomalies.append("Unusually high number of accounts - May indicate spamming or bot activity")
        
        # Anomaly 3: Only on single platform (isolated)
        if len(found_platforms) == 1:
            single_platform = found_platforms[0].get("platform", "").upper()
            anomalies.append(f"Account only found on {single_platform} - May indicate focused service usage")
        
        # Anomaly 4: Mix of professional and unprofessional platforms
        categories = features.get("platform_categories", {})
        if categories.get("professional", 0) > 0 and categories.get("entertainment", 0) > 0:
            anomalies.append("Mixed professional and entertainment presence - May reveal personal/work boundary issues")
        
        # Anomaly 5: Errors/timeouts on specific platforms
        error_platforms = [p for p in platforms_found if p.get("status") in ["error", "timeout"]]
        if len(error_platforms) > 3:
            anomalies.append("Multiple platform access errors - May indicate IP blocking or service restrictions")
        
        return anomalies

    def _get_platform_risks(self, platforms_found: List[Dict]) -> Dict:
        """Get individual platform risk scores"""
        platform_risks = {}
        
        for platform_data in platforms_found:
            platform = platform_data.get("platform", "").lower()
            status = platform_data.get("status")
            
            if status == "found":
                risk_weight = self.PLATFORM_RISK_WEIGHTS.get(platform, 0.5)
                sensitivity = self.PLATFORM_SENSITIVITY.get(platform, 0.5)
                risk_score = (risk_weight * 0.6 + sensitivity * 0.4) * 100
                
                platform_risks[platform] = {
                    "risk_score": round(risk_score, 1),
                    "status": "FOUND",
                    "sensitivity": round(sensitivity * 100, 1),
                }
            elif status == "not_found":
                platform_risks[platform] = {
                    "risk_score": 0,
                    "status": "NOT_FOUND",
                    "sensitivity": 0,
                }
        
        return platform_risks

    def _generate_recommendations(
        self,
        ml_risk_score: float,
        risk_level: str,
        anomalies: List[str],
        platforms_found: List[Dict]
    ) -> List[str]:
        """Generate actionable security recommendations"""
        recommendations = []
        
        # Risk-level based recommendations
        if risk_level == "CRITICAL":
            recommendations.append("🚨 CRITICAL: Immediate action required - Consider privacy mode for sensitive platforms")
            recommendations.append("Review all linked accounts for suspicious activity")
            recommendations.append("Consider using different usernames on sensitive platforms (finance, health, etc.)")
        
        elif risk_level == "HIGH":
            recommendations.append("⚠️ HIGH: Review privacy settings on all major platforms")
            recommendations.append("Enable two-factor authentication (2FA) on critical accounts")
            recommendations.append("Audit account recovery options (email, phone)")
        
        elif risk_level == "MEDIUM":
            recommendations.append("📋 MEDIUM: Review privacy settings on key platforms")
            recommendations.append("Consider limiting personal information visibility")
            recommendations.append("Check what information is publicly visible")
        
        else:  # LOW
            recommendations.append("✅ LOW: Maintain current privacy practices")
            recommendations.append("Regular reviews recommended")
        
        # Platform-specific recommendations
        found_platforms = [p for p in platforms_found if p.get("status") == "found"]
        for platform in found_platforms:
            platform_name = platform.get("platform", "").lower()
            
            if platform_name in ["facebook", "linkedin"]:
                recommendations.append(f"🔒 {platform_name.upper()}: Limit visible connections and profile details")
            
            if platform_name in ["twitter", "instagram"]:
                recommendations.append(f"🌐 {platform_name.upper()}: Review geotagged posts and location services")
            
            if platform_name == "github":
                recommendations.append("💻 GITHUB: Audit public repositories for sensitive data exposure")
        
        # Anomaly-based recommendations
        if anomalies:
            recommendations.append(f"⚡ Anomaly detected: {anomalies[0]}")
        
        return recommendations[:7]  # Return top 7 recommendations


class GroqMLAnalyzer:
    """
    Integration with Groq API for advanced ML analysis
    Uses LLM for sophisticated threat intelligence
    """
    
    def __init__(self, groq_client=None):
        """Initialize Groq ML analyzer"""
        self.groq_client = groq_client
        logger.info("🧠 Groq ML Analyzer initialized")

    def analyze_with_groq(self, scan_data: Dict, ml_scores: Dict) -> str:
        """
        Use Groq API to generate advanced threat analysis

        Args:
            scan_data: Scan results from OSINT
            ml_scores: ML risk scores

        Returns:
            Advanced analysis text from Groq
        """
        if not self.groq_client:
            logger.warning("Groq client not available")
            return "Groq analysis unavailable"

        platforms_found = [
            p.get("platform") for p in scan_data.get("all_platforms_checked", [])
            if p.get("status") == "found"
        ]
        
        prompt = f"""Analyze this digital footprint for security risks:

Digital Footprint Profile:
- Platforms Found: {', '.join(platforms_found) if platforms_found else 'None'}
- ML Risk Score: {ml_scores.get('ml_risk_score', 0)}/100
- Risk Level: {ml_scores.get('risk_level', 'UNKNOWN')}
- Anomalies: {', '.join(ml_scores.get('anomalies', ['None'])) if ml_scores.get('anomalies') else 'None'}
- Total Exposures: {scan_data.get('total_exposures', 0)}

Provide:
1. Threat assessment (1-2 sentences)
2. Primary risks (3 key vulnerabilities)
3. Priority actions (top 2 immediate steps)
4. Long-term strategy (1 recommendation)

Keep response concise and actionable."""

        try:
            response = self.groq_client.generate_text(prompt, max_tokens=300)
            logger.info("✅ Groq analysis completed")
            return response
        except Exception as e:
            logger.error(f"Groq analysis failed: {e}")
            return f"Analysis error: {str(e)}"


def get_ml_risk_analysis(scan_results: Dict, groq_client=None) -> Dict:
    """
    Main function to get complete ML-based risk analysis

    Args:
        scan_results: Full OSINT scan results
        groq_client: Optional Groq client for advanced analysis

    Returns:
        Complete analysis with ML scores, anomalies, and recommendations
    """
    # Initialize ML analyzer
    ml_analyzer = MLRiskAnalyzer()
    
    # Get ML risk scores
    ml_scores = ml_analyzer.calculate_ml_risk_score(scan_results)
    
    # Get Groq-based analysis if available
    groq_analysis = None
    if groq_client:
        groq_analyzer = GroqMLAnalyzer(groq_client)
        groq_analysis = groq_analyzer.analyze_with_groq(scan_results, ml_scores)
    
    return {
        "ml_analysis": ml_scores,
        "groq_analysis": groq_analysis,
        "timestamp": datetime.now().isoformat(),
    }
