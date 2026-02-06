"""
AI-Powered Digital Footprint Scanner
Main Flask Application Entry Point

Production Responsibilities:
- Load environment & configuration
- Validate critical settings
- Initialize Flask + sessions
- Register routes (API, OAuth, UI)
- Handle real OSINT scanning requests

Deployment: Vercel Serverless
Local Testing: python app.py
"""

import os
from flask import Flask
from flask_session import Session
from flask_cors import CORS
from dotenv import load_dotenv

from config import config

# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================
load_dotenv()

# ==================================================
# CREATE FLASK APP
# ==================================================
app = Flask(__name__)

# ==================================================
# CORS CONFIGURATION (for API access)
# ==================================================
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# ==================================================
# FLASK + SESSION CONFIGURATION
# ==================================================
# Use filesystem for development, but allow override for production
session_type = os.getenv("SESSION_TYPE", "filesystem")
session_dir = os.getenv("SESSION_FILE_DIR", os.path.join(os.getcwd(), ".flask_session"))

app.config.from_mapping(
    SECRET_KEY=config.SECRET_KEY,
    DEBUG=config.FLASK_DEBUG,
    ENV=config.FLASK_ENV,

    # Server-side sessions
    SESSION_TYPE=session_type,
    SESSION_FILE_DIR=session_dir if session_type == "filesystem" else None,
    SESSION_PERMANENT=False,
    SESSION_USE_SIGNER=True,
    SESSION_KEY_PREFIX="dfs_",
    PERMANENT_SESSION_LIFETIME=3600,  # 1 hour for production
)

Session(app)

# ==================================================
# VALIDATE CONFIGURATION (FAIL FAST)
# ==================================================
try:
    config.validate()
except Exception as e:
    print("[ERROR] CONFIGURATION ERROR")
    print(str(e))
    raise SystemExit(1)

print("[OK] Environment & configuration validated")

# ==================================================
# INITIALIZE & TRAIN ML MODELS (ENTERPRISE MODE)
# ==================================================
print("[INFO] Initializing ML models with real training data from Groq API...")
try:
    from analysis.ml_trainer_enterprise import EnterpriseMLTrainer
    import os
    
    # Check if models already trained
    models_dir = "models"
    has_trained_models = (
        os.path.exists(os.path.join(models_dir, "risk_model.pkl")) and
        os.path.exists(os.path.join(models_dir, "level_model.pkl")) and
        os.path.exists(os.path.join(models_dir, "scaler.pkl"))
    )
    
    if has_trained_models:
        print("[OK] ✅ Trained models found - Loading existing models")
    else:
        print("[INFO] 🤖 Training new ML models from Groq API data...")
        trainer = EnterpriseMLTrainer()
        trainer.train_all_models()
        print("[OK] ✅ ML models trained successfully")
        
except Exception as e:
    print(f"[WARNING] ML training initialization issue: {e}")
    print("[WARNING] Models will be trained on first request")

# ==================================================
# REGISTER ROUTES & API BLUEPRINTS
# ==================================================
from routes import register_routes  # noqa: E402
from api.ml_endpoints import ml_api  # noqa: E402

register_routes(app)
app.register_blueprint(ml_api)

# ==================================================
# ERROR HANDLERS
# ==================================================
@app.errorhandler(404)
def not_found(e):
    return {"error": "Endpoint not found"}, 404


@app.errorhandler(500)
def internal_error(e):
    return {"error": "Internal server error"}, 500

# ==================================================
# MAIN ENTRY POINT
# ==================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    print("[INFO] Starting AI-Powered Digital Footprint Scanner")
    print(f">> Environment : {config.FLASK_ENV}")
    print(f">> Debug Mode  : {config.FLASK_DEBUG}")
    print(f">> Port        : {port}")
    print("[INFO] OAuth & scanning systems initialized")

    app.run(host="0.0.0.0", port=port)
