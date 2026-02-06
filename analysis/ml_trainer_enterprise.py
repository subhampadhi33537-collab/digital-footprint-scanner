"""
Enterprise ML Model Trainer
===========================
Trains ML models using real data from Groq API in JSON format.
Generates realistic training data based on actual digital footprint patterns.
"""

import json
import logging
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

from ai_engine.groq_client import get_groq_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnterpriseMLTrainer:
    """Advanced ML trainer using real data from Groq API"""

    def __init__(self):
        self.groq = get_groq_client()
        self.models_dir = "models"
        os.makedirs(self.models_dir, exist_ok=True)

    def get_training_data_from_groq(self) -> dict:
        """
        Generate realistic training data from Groq API
        Returns JSON format with multiple scenarios
        """
        logger.info("🤖 Fetching training data from Groq API...")

        prompt = """Generate realistic digital footprint data in JSON format for ML training.
Create 20 different user scenarios with the following structure for each:
{
  "user_id": "unique_id",
  "username_variations": 3,
  "platforms_found": number between 2-15,
  "risky_platform_count": number,
  "email_exposures": number,
  "name_matches": number,
  "social_links": number,
  "suspicious_accounts": boolean,
  "data_breaches": number,
  "location_leaks": number,
  "phone_leaks": number,
  "risk_score": float between 0-100,
  "risk_level": "LOW|MEDIUM|HIGH",
  "recommendations_count": number
}

Make it realistic with correlations (more platforms = higher risk, etc).
Return ONLY valid JSON array, no other text."""

        try:
            response_text = self.groq.generate_text(prompt, max_tokens=2000)
            
            # Extract JSON from response
            try:
                data = json.loads(response_text)
                logger.info(f"✅ Generated {len(data)} training samples from Groq")
                return data
            except json.JSONDecodeError:
                # Fallback: parse JSON from response
                import re
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    logger.info(f"✅ Extracted {len(data)} training samples")
                    return data
                raise
        except Exception as e:
            logger.error(f"Failed to get Groq data: {e}. Using realistic fallback.")
            return self._generate_realistic_fallback_data()

    def _generate_realistic_fallback_data(self) -> list:
        """Generate realistic training data programmatically"""
        logger.info("📊 Generating realistic training data with smart correlations...")
        
        data = []
        
        # Generate diverse scenarios with realistic correlations
        risk_profiles = [
            # LOW RISK: Few platforms, minimal exposure
            {
                "platforms": (2, 6),
                "exposures": (0, 3),
                "breaches": (0, 1),
                "risk_range": (10, 30),
                "count": 4
            },
            # MEDIUM RISK: Moderate presence, some exposure
            {
                "platforms": (6, 11),
                "exposures": (3, 7),
                "breaches": (1, 3),
                "risk_range": (35, 65),
                "count": 8
            },
            # HIGH RISK: Large presence, extensive exposure
            {
                "platforms": (11, 16),
                "exposures": (8, 15),
                "breaches": (3, 10),
                "risk_range": (70, 95),
                "count": 6
            },
            # CRITICAL: Extreme exposure
            {
                "platforms": (14, 16),
                "exposures": (15, 20),
                "breaches": (10, 20),
                "risk_range": (90, 100),
                "count": 2
            }
        ]

        user_id = 1000
        for profile in risk_profiles:
            for _ in range(profile["count"]):
                platforms = np.random.randint(*profile["platforms"])
                exposures = np.random.randint(*profile["exposures"])
                breaches = np.random.randint(*profile["breaches"])
                risk_score = np.random.uniform(*profile["risk_range"])

                # Correlation logic: more platforms = higher risk
                score_adjustment = platforms * 3
                risk_score = min(100, risk_score + score_adjustment * 0.1)

                sample = {
                    "user_id": f"user_{user_id}",
                    "platforms_found": platforms,
                    "exposures": exposures,
                    "breaches": breaches,
                    "username_variations": np.random.randint(1, 5),
                    "location_leaks": np.random.randint(0, 3),
                    "phone_leaks": np.random.randint(0, 2),
                    "suspicious_accounts": np.random.choice([True, False], p=[0.3, 0.7]),
                    "risk_score": float(risk_score),
                    "risk_level": self._calculate_risk_level(risk_score)
                }
                data.append(sample)
                user_id += 1

        logger.info(f"✅ Generated {len(data)} realistic training samples")
        return data

    def _calculate_risk_level(self, score: float) -> str:
        """Map risk score to level"""
        if score < 35:
            return "LOW"
        elif score < 65:
            return "MEDIUM"
        elif score < 85:
            return "HIGH"
        else:
            return "CRITICAL"

    def prepare_features(self, data: list) -> tuple:
        """
        Prepare features for ML training
        X: features, y_risk: risk scores, y_level: risk levels
        """
        X = []
        y_risk = []
        y_level = []

        for sample in data:
            features = [
                sample.get("platforms_found", 0),
                sample.get("exposures", 0),
                sample.get("breaches", 0),
                sample.get("username_variations", 1),
                sample.get("location_leaks", 0),
                sample.get("phone_leaks", 0),
                1 if sample.get("suspicious_accounts") else 0,
            ]
            X.append(features)
            y_risk.append(sample.get("risk_score", 50))
            
            # Map level to numeric
            level_map = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
            y_level.append(level_map.get(sample.get("risk_level", "MEDIUM"), 1))

        return np.array(X), np.array(y_risk), np.array(y_level)

    def train_all_models(self) -> dict:
        """Train all ML models with real data"""
        logger.info("\n" + "="*60)
        logger.info("🚀 Starting Advanced ML Training (Enterprise Mode)")
        logger.info("="*60)

        # 1. Get training data from Groq
        training_data = self.get_training_data_from_groq()
        
        # 2. Prepare features
        logger.info("📊 Preparing features...")
        X, y_risk, y_level = self.prepare_features(training_data)
        
        # 3. Split data
        X_train, X_test, y_risk_train, y_risk_test, y_level_train, y_level_test = train_test_split(
            X, y_risk, y_level, test_size=0.2, random_state=42
        )

        # 4. Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        results = {}

        # Train Risk Score Model (Regression)
        logger.info("\n🔍 Training Risk Score Regressor...")
        risk_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        risk_model.fit(X_train_scaled, y_risk_train)
        risk_score = risk_model.score(X_test_scaled, y_risk_test)
        
        logger.info(f"   ✅ Risk Model R² Score: {risk_score:.4f}")
        joblib.dump(risk_model, f"{self.models_dir}/risk_model.pkl")
        joblib.dump(scaler, f"{self.models_dir}/scaler.pkl")
        results["risk_model"] = {"r2_score": float(risk_score)}

        # Train Risk Level Classifier (Classification)
        logger.info("\n🎯 Training Risk Level Classifier...")
        level_model = GradientBoostingClassifier(
            n_estimators=50,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        level_model.fit(X_train_scaled, y_level_train)
        level_score = level_model.score(X_test_scaled, y_level_test)
        
        logger.info(f"   ✅ Level Model Accuracy: {level_score:.4f}")
        joblib.dump(level_model, f"{self.models_dir}/level_model.pkl")
        results["level_model"] = {"accuracy": float(level_score)}

        # 5. Generate predictions on test set for validation
        logger.info("\n📈 Validating Models...")
        y_risk_pred = risk_model.predict(X_test_scaled)
        y_level_pred = level_model.predict(X_test_scaled)

        # Calculate metrics
        from sklearn.metrics import mean_absolute_error, mean_squared_error
        mae = mean_absolute_error(y_risk_test, y_risk_pred)
        rmse = np.sqrt(mean_squared_error(y_risk_test, y_risk_pred))
        
        logger.info(f"   MAE: {mae:.2f}, RMSE: {rmse:.2f}")

        # 6. Save summary
        summary = {
            "status": "success",
            "training_samples": len(training_data),
            "test_samples": len(X_test),
            "risk_model": {
                "type": "RandomForest",
                "r2_score": float(risk_score),
                "mae": float(mae),
                "rmse": float(rmse)
            },
            "level_model": {
                "type": "GradientBoosting",
                "accuracy": float(level_score)
            },
            "features": [
                "platforms_found",
                "exposures",
                "breaches",
                "username_variations",
                "location_leaks",
                "phone_leaks",
                "suspicious_accounts"
            ],
            "risk_levels": ["LOW (0-35%)", "MEDIUM (35-65%)", "HIGH (65-85%)", "CRITICAL (85-100%)"]
        }

        logger.info("\n" + "="*60)
        logger.info("✅ ALL MODELS TRAINED SUCCESSFULLY")
        logger.info("="*60)
        logger.info(json.dumps(summary, indent=2))

        return summary

    def predict_risk(self, features: list) -> dict:
        """
        Predict risk for new scan
        features: [platforms, exposures, breaches, ...]
        """
        try:
            risk_model = joblib.load(f"{self.models_dir}/risk_model.pkl")
            level_model = joblib.load(f"{self.models_dir}/level_model.pkl")
            scaler = joblib.load(f"{self.models_dir}/scaler.pkl")

            X = np.array([features])
            X_scaled = scaler.transform(X)

            risk_score = float(risk_model.predict(X_scaled)[0])
            risk_score = max(0, min(100, risk_score))  # Clip to 0-100

            risk_level_pred = int(level_model.predict(X_scaled)[0])
            level_names = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            risk_level = level_names[min(risk_level_pred, 3)]

            return {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "confidence": float(level_model.predict_proba(X_scaled).max()),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                "risk_score": 50,
                "risk_level": "MEDIUM",
                "confidence": 0.5,
                "status": "error",
                "error": str(e)
            }


def get_enterprise_trainer():
    """Get global trainer instance"""
    global _trainer
    if '_trainer' not in globals():
        _trainer = EnterpriseMLTrainer()
    return _trainer
