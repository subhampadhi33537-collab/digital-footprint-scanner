"""
Vercel Serverless Entry Point
AI-Powered Digital Footprint Scanner
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_session import Session
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import config
from config import config

# ==================================================
# CREATE FLASK APP
# ==================================================
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# ==================================================
# CORS CONFIGURATION
# ==================================================
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# ==================================================
# FLASK + SESSION CONFIGURATION
# ==================================================
app.config.from_mapping(
    SECRET_KEY=config.SECRET_KEY,
    DEBUG=False,
    ENV='production',
    
    # Server-side sessions - use filesystem for Vercel
    SESSION_TYPE='filesystem',
    SESSION_FILE_DIR='/tmp/.flask_session',
    SESSION_PERMANENT=False,
    SESSION_USE_SIGNER=True,
    SESSION_KEY_PREFIX='dfs_',
    PERMANENT_SESSION_LIFETIME=3600,
)

Session(app)

# ==================================================
# VALIDATE CONFIGURATION
# ==================================================
try:
    config.validate()
except Exception as e:
    print(f"[WARNING] Configuration validation: {str(e)}")
    # Don't fail on Vercel, just warn
    pass

# ==================================================
# REGISTER ROUTES
# ==================================================
from routes import register_routes
from api.ml_endpoints import ml_api

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
# HEALTH CHECK
# ==================================================
@app.route('/api/health')
def health():
    return {"status": "healthy", "service": "Digital Footprint Scanner"}, 200

# ==================================================
# VERCEL HANDLER
# ==================================================
# Vercel expects the app to be available for WSGI
if __name__ != "__main__":
    # Running on Vercel
    handler = app
