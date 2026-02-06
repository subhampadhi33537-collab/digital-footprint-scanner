"""
ML Training & Model Management API Endpoints
=============================================
Provides REST API for:
- Training ML models from Groq-generated data
- Making predictions
- Accessing training model insights
- Enterprise-grade ML operations
"""

from flask import Blueprint, request, jsonify
import os
import json
from pathlib import Path
from datetime import datetime
import logging

from analysis.ml_trainer_enterprise import EnterpriseMLTrainer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ML API] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Create blueprint
ml_api = Blueprint('ml_api', __name__, url_prefix='/api/ml')

# Global trainer instance
trainer = None

def get_trainer():
    """Get or create enterprise ML trainer instance"""
    global trainer
    if trainer is None:
        trainer = EnterpriseMLTrainer()
    return trainer


# ========================
# TRAINING ENDPOINTS
# ========================

@ml_api.route('/train', methods=['POST'])
def train_models():
    """
    Train all ML models from scratch
    Generates training data from Groq API
    """
    try:
        logger.info("Starting model training...")
        trainer = get_trainer()
        
        # Get number of samples from request or use default
        num_samples = request.json.get('num_samples', 150) if request.json else 150
        
        logger.info(f"Training with {num_samples} samples...")
        result = trainer.train_all_models()
        
        return jsonify({
            "status": "success",
            "message": "Models trained successfully",
            "results": result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Training error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@ml_api.route('/train/risk', methods=['POST'])
def train_risk_model():
    """Train all ML models (Enterprise Mode) - includes risk & level"""
    try:
        trainer = get_trainer()
        result = trainer.train_all_models()
        
        return jsonify({
            "status": "success",
            "message": "Enterprise ML models trained successfully",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Risk model training error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@ml_api.route('/train/threat', methods=['POST'])
def train_threat_model():
    """Train all ML models (Enterprise Mode) - includes risk & level"""
    try:
        trainer = get_trainer()
        result = trainer.train_all_models()
        
        return jsonify({
            "status": "success",
            "message": "Enterprise ML models trained successfully",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Threat model training error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ========================
# TRAINING DATA ENDPOINTS
# ========================

@ml_api.route('/training-data/generate', methods=['POST'])
def generate_training_data():
    """Generate training data from Groq API"""
    try:
        num_samples = request.json.get('num_samples', 100) if request.json else 100
        
        trainer = get_trainer()
        data = trainer.generate_training_data_from_groq(num_samples)
        
        return jsonify({
            "status": "success",
            "samples_generated": len(data),
            "data": data,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Data generation error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@ml_api.route('/training-data/list', methods=['GET'])
def list_training_data():
    """List all saved training data files"""
    try:
        training_dir = Path("data/training_data")
        if not training_dir.exists():
            return jsonify({"status": "success", "files": []}), 200
        
        files = sorted(training_dir.glob("*.json"), reverse=True)
        
        file_info = []
        for f in files[:10]:  # Last 10 files
            size = f.stat().st_size
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            
            file_info.append({
                "filename": f.name,
                "size_bytes": size,
                "created": mtime.isoformat(),
                "url": f"/data/training_data/{f.name}"
            })
        
        return jsonify({
            "status": "success",
            "total_files": len(list(training_dir.glob("*.json"))),
            "files": file_info
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing training data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_api.route('/training-data/<filename>', methods=['GET'])
def get_training_data(filename):
    """Get specific training data file"""
    try:
        filepath = Path("data/training_data") / filename
        
        if not filepath.exists():
            return jsonify({"status": "error", "message": "File not found"}), 404
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return jsonify({
            "status": "success",
            "filename": filename,
            "data": data,
            "total_samples": len(data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error reading training data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ========================
# PREDICTION ENDPOINTS
# ========================

@ml_api.route('/predict/risk', methods=['POST'])
def predict_risk():
    """Predict risk level for given scan features"""
    try:
        if not request.json:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        data = request.json
        
        # Extract features for ML model
        features = [
            data.get("platforms_found", 0),
            data.get("exposures", 0),
            data.get("breaches", 0),
            data.get("username_variations", 1),
            data.get("location_leaks", 0),
            data.get("phone_leaks", 0),
            1 if data.get("suspicious_accounts") else 0,
        ]
        
        trainer = get_trainer()
        prediction = trainer.predict_risk(features)
        
        return jsonify({
            "status": "success",
            "prediction": prediction,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@ml_api.route('/predict/batch', methods=['POST'])
def batch_predict():
    """Batch predict risk levels for multiple scans"""
    try:
        if not request.json or 'scans' not in request.json:
            return jsonify({"status": "error", "message": "No scans provided"}), 400
        
        scans = request.json['scans']
        trainer = get_trainer()
        
        predictions = []
        for scan in scans:
            features = [
                scan.get("platforms_found", 0),
                scan.get("exposures", 0),
                scan.get("breaches", 0),
                scan.get("username_variations", 1),
                scan.get("location_leaks", 0),
                scan.get("phone_leaks", 0),
                1 if scan.get("suspicious_accounts") else 0,
            ]
            pred = trainer.predict_risk(features)
            predictions.append(pred)
        
        return jsonify({
            "status": "success",
            "predictions": predictions,
            "total_predictions": len(predictions),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ========================
# MODEL INFO ENDPOINTS
# ========================

@ml_api.route('/models/list', methods=['GET'])
def list_models():
    """List all trained models"""
    try:
        models_dir = Path("data/models")
        if not models_dir.exists():
            return jsonify({"status": "success", "models": []}), 200
        
        models = {}
        for f in models_dir.glob("*_latest.json"):
            model_name = f.name.replace("_latest.json", "")
            
            with open(f, 'r') as mf:
                model_meta = json.load(mf)
            
            models[model_name] = {
                "name": model_name,
                "timestamp": model_meta.get("timestamp"),
                "status": "trained",
                "file": f.name
            }
        
        return jsonify({
            "status": "success",
            "models": models,
            "total_models": len(models)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_api.route('/models/info', methods=['GET'])
def get_model_info():
    """Get detailed model information"""
    try:
        models_dir = Path("data/models")
        
        info = {
            "models_dir": str(models_dir),
            "exists": models_dir.exists(),
            "model_count": len(list(models_dir.glob("*.pkl"))) if models_dir.exists() else 0,
            "training_data_dir": "data/training_data",
            "total_training_files": len(list(Path("data/training_data").glob("*.json"))) if Path("data/training_data").exists() else 0
        }
        
        return jsonify({
            "status": "success",
            "info": info
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ========================
# UTILITY ENDPOINTS
# ========================

@ml_api.route('/health', methods=['GET'])
def health():
    """Check ML system health"""
    try:
        models_dir = Path("data/models")
        training_dir = Path("data/training_data")
        
        return jsonify({
            "status": "healthy",
            "models_available": len(list(models_dir.glob("*.pkl"))) if models_dir.exists() else 0,
            "training_data_files": len(list(training_dir.glob("*.json"))) if training_dir.exists() else 0,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@ml_api.route('/stats', methods=['GET'])
def get_stats():
    """Get ML system statistics"""
    try:
        models_dir = Path("data/models")
        training_dir = Path("data/training_data")
        
        # Count files
        model_files = list(models_dir.glob("*.pkl")) if models_dir.exists() else []
        training_files = list(training_dir.glob("*.json")) if training_dir.exists() else []
        
        # Calculate total training samples from all files
        total_samples = 0
        for f in training_files:
            try:
                with open(f, 'r') as tf:
                    data = json.load(tf)
                    total_samples += len(data)
            except:
                pass
        
        return jsonify({
            "status": "success",
            "stats": {
                "total_models": len(model_files),
                "total_training_files": len(training_files),
                "total_training_samples": total_samples,
                "models_dir_size_mb": sum(f.stat().st_size for f in model_files) / (1024*1024),
                "training_dir_size_mb": sum(f.stat().st_size for f in training_files) / (1024*1024)
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
