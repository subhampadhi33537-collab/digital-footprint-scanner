#!/usr/bin/env python3
"""
Startup Script for Digital Footprint Scanner
Ensures all directories exist and models are trained before starting the app
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [STARTUP] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def ensure_directories():
    """Create required directories if they don't exist"""
    directories = [
        "models",
        "data",
        "data/scans",
        "data/temp",
        "data/models",
        "data/training_data",
        "static/data",
        ".flask_session",
        "logs"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"✅ Directory ensured: {directory}")
        except Exception as e:
            logger.error(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

def check_models():
    """Check if ML models exist and are valid"""
    required_models = [
        "models/risk_model.pkl",
        "models/level_model.pkl",
        "models/scaler.pkl"
    ]
    
    all_exist = all(os.path.exists(model) for model in required_models)
    
    if all_exist:
        logger.info("✅ ML models found")
        return True
    else:
        logger.warning("⚠️  ML models not found - will train on first scan")
        return False

def train_models():
    """Train ML models if they don't exist"""
    try:
        logger.info("🤖 Training ML models...")
        from analysis.ml_trainer_enterprise import EnterpriseMLTrainer
        
        trainer = EnterpriseMLTrainer()
        results = trainer.train_all_models()
        
        logger.info("✅ ML models trained successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to train models: {e}")
        logger.warning("⚠️  App will continue without pre-trained models")
        return False

def validate_configuration():
    """Validate that required configuration is present"""
    try:
        from config import config
        config.validate()
        logger.info("✅ Configuration validated")
        return True
    except Exception as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        return False

def main():
    """Main startup sequence"""
    logger.info("=" * 60)
    logger.info("🚀 Digital Footprint Scanner - Startup")
    logger.info("=" * 60)
    
    # Step 1: Ensure directories
    logger.info("Step 1: Creating required directories...")
    if not ensure_directories():
        logger.error("Failed to create directories. Exiting.")
        return False
    
    # Step 2: Validate configuration
    logger.info("Step 2: Validating configuration...")
    if not validate_configuration():
        logger.error("Configuration validation failed. Exiting.")
        return False
    
    # Step 3: Check/train models
    logger.info("Step 3: Checking ML models...")
    if not check_models():
        logger.info("Models not found, training now...")
        if not train_models():
            logger.warning("Model training failed, but app will continue")
    
    logger.info("=" * 60)
    logger.info("✅ Startup complete - App is ready")
    logger.info("=" * 60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
