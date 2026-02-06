"""
ML Model Trainer for Digital Footprint Scanner
===============================================
Trains machine learning models using data fetched from Groq API
Stores training data and models in JSON format for portability
"""

import os
import json
import logging
from typing import Dict, List, Any
from datetime import datetime
import pickle
import base64
from pathlib import Path

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
import numpy as np

from config import config
from ai_engine.groq_client import GroqClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ML TRAINER] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Paths for model storage
MODELS_DIR = Path("data/models")
TRAINING_DATA_DIR = Path("data/training_data")
MODELS_DIR.mkdir(parents=True, exist_ok=True)
TRAINING_DATA_DIR.mkdir(parents=True, exist_ok=True)


class MLModelTrainer:
    """
    Trains ML models using Groq API generated data
    Stores models and training data in JSON format
    """
    
    def __init__(self, groq_client=None):
        self.groq_client = groq_client or GroqClient()
        self.risk_model = None
        self.threat_model = None
        self.models_metadata = {}
        
    def generate_training_data_from_groq(self, num_samples: int = 100) -> List[Dict]:
        """
        Generate training data by querying Groq API
        Stores diverse scan scenarios for model training
        """
        logger.info(f"Generating {num_samples} training samples from Groq API...")
        
        training_data = []
        
        prompt = f"""Generate JSON training data for a digital footprint risk assessment model.
        
Provide {num_samples} diverse examples, each with:
- platform_count (1-15)
- exposure_score (0-100)
- username_consistency (0-1)
- email_exposure (boolean)
- platform_types (list: "social", "professional", "developer", "creative")
- anomaly_flags (list of detected anomalies)
- expected_risk_level ("LOW", "MEDIUM", "HIGH", "CRITICAL")
- risk_score (0-100)

Return ONLY a valid JSON array with all {num_samples} examples.
Format:
[
  {{"platform_count": 5, "exposure_score": 45, "username_consistency": 0.8, "email_exposure": true, "platform_types": ["social"], "anomaly_flags": [], "expected_risk_level": "MEDIUM", "risk_score": 55}},
  ...
]
"""
        
        try:
            response = self.groq_client.generate_text(prompt, max_tokens=2000)
            
            # Extract JSON from response
            json_str = self._extract_json_from_response(response)
            samples = json.loads(json_str)
            
            if isinstance(samples, list):
                training_data = samples[:num_samples]
                logger.info(f"✅ Generated {len(training_data)} training samples from Groq")
                
                # Save training data
                self._save_training_data(training_data)
                return training_data
            else:
                logger.warning("Groq response was not a list, using fallback data")
                return self._generate_fallback_training_data(num_samples)
                
        except Exception as e:
            logger.error(f"Error generating training data: {e}")
            return self._generate_fallback_training_data(num_samples)
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON from Groq response"""
        # Find JSON array in response
        start = response.find('[')
        end = response.rfind(']') + 1
        
        if start != -1 and end > start:
            return response[start:end]
        
        raise ValueError("No JSON array found in response")
    
    def _generate_fallback_training_data(self, num_samples: int) -> List[Dict]:
        """Generate fallback training data if Groq API fails"""
        logger.info("Using fallback training data generation...")
        
        data = []
        risk_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        platform_types_list = [
            ["social"],
            ["professional"],
            ["developer"],
            ["creative"],
            ["social", "professional"],
            ["developer", "creative"],
            ["social", "developer", "professional"]
        ]
        anomaly_names = ["bot_pattern", "privacy_gap", "impersonation_risk", "geographic_anomaly"]
        
        for i in range(num_samples):
            platform_count = np.random.randint(1, 16)
            risk_level = risk_levels[min(platform_count // 4, 3)]
            risk_score = (platform_count * 6) + np.random.randint(-10, 10)
            risk_score = max(0, min(100, risk_score))
            
            # Randomly select platform types (use index)
            selected_platform_types = platform_types_list[np.random.randint(0, len(platform_types_list))]
            
            # Randomly select anomaly flags
            num_anomalies = np.random.randint(0, 3)
            selected_anomalies = list(np.random.choice(anomaly_names, size=num_anomalies, replace=False))
            
            data.append({
                "platform_count": int(platform_count),
                "exposure_score": int(np.random.randint(20, 100)),
                "username_consistency": round(float(np.random.random()), 2),
                "email_exposure": bool(np.random.random() > 0.5),
                "platform_types": selected_platform_types,
                "anomaly_flags": selected_anomalies,
                "expected_risk_level": risk_level,
                "risk_score": int(risk_score)
            })
        
        self._save_training_data(data)
        return data
    
    def _save_training_data(self, data: List[Dict]) -> None:
        """Save training data to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = TRAINING_DATA_DIR / f"training_data_{timestamp}.json"
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ Training data saved to {filepath}")
    
    def train_risk_model(self, training_data: List[Dict] = None) -> Dict:
        """Train risk prediction model"""
        if training_data is None:
            training_data = self.generate_training_data_from_groq(num_samples=100)
        
        logger.info("Training risk prediction model...")
        
        # Prepare features and labels
        features = []
        labels = []
        risk_mapping = {"LOW": 0.25, "MEDIUM": 0.5, "HIGH": 0.75, "CRITICAL": 1.0}
        
        for sample in training_data:
            try:
                feature_vector = [
                    sample.get("platform_count", 0),
                    sample.get("exposure_score", 0),
                    sample.get("username_consistency", 0),
                    int(sample.get("email_exposure", False)),
                    len(sample.get("platform_types", [])),
                    len(sample.get("anomaly_flags", [])),
                ]
                
                features.append(feature_vector)
                risk_level = sample.get("expected_risk_level", "MEDIUM")
                labels.append(risk_mapping.get(risk_level, 0.5))
                
            except Exception as e:
                logger.warning(f"Skipping sample: {e}")
                continue
        
        if len(features) < 2:
            logger.warning("Not enough training samples")
            return {"status": "failed", "message": "Insufficient training data"}
        
        # Convert to numpy arrays
        X = np.array(features)
        y = np.array(labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        self.risk_model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1,
            max_depth=10
        )
        
        self.risk_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.risk_model.score(X_train_scaled, y_train)
        test_score = self.risk_model.score(X_test_scaled, y_test)
        
        logger.info(f"✅ Risk model trained - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
        
        # Save model
        self._save_model("risk_model", self.risk_model, scaler)
        
        return {
            "status": "success",
            "model_type": "risk_prediction",
            "train_score": float(train_score),
            "test_score": float(test_score),
            "samples_used": len(features),
            "timestamp": datetime.now().isoformat()
        }
    
    def train_threat_model(self, training_data: List[Dict] = None) -> Dict:
        """Train threat classification model"""
        if training_data is None:
            training_data = self.generate_training_data_from_groq(num_samples=100)
        
        logger.info("Training threat classification model...")
        
        features = []
        labels = []
        threat_mapping = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        
        for sample in training_data:
            try:
                feature_vector = [
                    sample.get("platform_count", 0),
                    sample.get("exposure_score", 0),
                    sample.get("username_consistency", 0),
                    int(sample.get("email_exposure", False)),
                    len(sample.get("platform_types", [])),
                    len(sample.get("anomaly_flags", [])),
                ]
                
                features.append(feature_vector)
                threat_level = sample.get("expected_risk_level", "MEDIUM")
                labels.append(threat_mapping.get(threat_level, 1))
                
            except Exception as e:
                logger.warning(f"Skipping sample: {e}")
                continue
        
        if len(features) < 2:
            logger.warning("Not enough training samples")
            return {"status": "failed", "message": "Insufficient training data"}
        
        X = np.array(features)
        y = np.array(labels)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.threat_model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            random_state=42,
            max_depth=5
        )
        
        self.threat_model.fit(X_train_scaled, y_train)
        
        train_score = self.threat_model.score(X_train_scaled, y_train)
        test_score = self.threat_model.score(X_test_scaled, y_test)
        
        logger.info(f"✅ Threat model trained - Train Acc: {train_score:.3f}, Test Acc: {test_score:.3f}")
        
        self._save_model("threat_model", self.threat_model, scaler)
        
        return {
            "status": "success",
            "model_type": "threat_classification",
            "train_score": float(train_score),
            "test_score": float(test_score),
            "samples_used": len(features),
            "timestamp": datetime.now().isoformat()
        }
    
    def _save_model(self, model_name: str, model: Any, scaler: StandardScaler) -> None:
        """Save trained model to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = MODELS_DIR / f"{model_name}_{timestamp}.pkl"
        
        model_data = {
            "model": base64.b64encode(pickle.dumps(model)).decode(),
            "scaler": base64.b64encode(pickle.dumps(scaler)).decode(),
            "timestamp": timestamp,
            "model_name": model_name
        }
        
        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=2)
        
        # Update latest symlink
        latest_filepath = MODELS_DIR / f"{model_name}_latest.json"
        with open(latest_filepath, 'w') as f:
            json.dump(model_data, f, indent=2)
        
        logger.info(f"✅ Model saved to {filepath}")
    
    def predict_risk(self, scan_features: Dict) -> Dict:
        """Predict risk level for a scan"""
        if self.risk_model is None:
            logger.warning("Risk model not loaded, training new model...")
            self.train_risk_model()
        
        try:
            feature_vector = np.array([[
                scan_features.get("platform_count", 0),
                scan_features.get("exposure_score", 0),
                scan_features.get("username_consistency", 0),
                int(scan_features.get("email_exposure", False)),
                len(scan_features.get("platform_types", [])),
                len(scan_features.get("anomaly_flags", [])),
            ]])
            
            prediction = self.risk_model.predict(feature_vector)[0]
            prediction = max(0, min(1, prediction))  # Clamp to 0-1
            
            return {
                "predicted_risk_score": float(prediction * 100),
                "risk_level": self._score_to_level(prediction * 100),
                "confidence": 0.85  # Model confidence
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {"error": str(e)}
    
    def _score_to_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score < 25:
            return "LOW"
        elif score < 50:
            return "MEDIUM"
        elif score < 75:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def train_all_models(self) -> Dict:
        """Train all models"""
        logger.info("Training all ML models...")
        training_data = self.generate_training_data_from_groq(num_samples=150)
        
        results = {
            "risk_model": self.train_risk_model(training_data),
            "threat_model": self.train_threat_model(training_data),
            "training_data_samples": len(training_data),
            "timestamp": datetime.now().isoformat()
        }
        
        return results


def get_ml_trainer() -> MLModelTrainer:
    """Get ML trainer instance"""
    return MLModelTrainer()
