"""
Render Deployment Entry Point
AI-Powered Digital Footprint Scanner
"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from flask import Flask
    from flask_session import Session
    from flask_cors import CORS
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # ==================================================
    # CREATE FLASK APP
    # ==================================================
    app = Flask(__name__)
    
    # ==================================================
    # CORS CONFIGURATION
    # ==================================================
    CORS(app)
    
    # ==================================================
    # FLASK + SESSION CONFIGURATION
    # ==================================================
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret-key'),
        DEBUG=False,
        ENV='production',
        SESSION_TYPE='filesystem',
        SESSION_PERMANENT=False,
        SESSION_USE_SIGNER=True,
        SESSION_KEY_PREFIX='dfs_',
    )
    
    Session(app)
    
    # ==================================================
    # HEALTH CHECK ENDPOINT (Always works)
    # ==================================================
    @app.route('/api/health', methods=['GET'])
    def health():
        return {"status": "healthy", "service": "Digital Footprint Scanner", "version": "1.0"}, 200
    
    @app.route('/api/status', methods=['GET'])
    def status():
        return {"status": "online", "environment": "Vercel"}, 200
    
    # ==================================================
    # TRY TO LOAD ROUTES
    # ==================================================
    try:
        from routes import register_routes
        register_routes(app)
        logger.info("Routes loaded successfully")
    except Exception as route_error:
        logger.error(f"Failed to load routes: {str(route_error)}")
        
        # Fallback route
        @app.route('/', methods=['GET'])
        def index():
            return {
                "status": "running",
                "message": "Digital Footprint Scanner API",
                "note": "Full routes may not be available"
            }, 200
    
    # ==================================================
    # TRY TO LOAD ML ENDPOINTS
    # ==================================================
    try:
        from api.ml_endpoints import ml_api
        app.register_blueprint(ml_api)
        logger.info("ML endpoints loaded successfully")
    except Exception as ml_error:
        logger.warning(f"ML endpoints not available: {str(ml_error)}")
    
    # ==================================================
    # ROOT ROUTE
    # ==================================================
    @app.route('/', methods=['GET', 'POST'])
    def root():
        return {
            "service": "Digital Footprint Scanner",
            "status": "operational",
            "endpoints": [
                "/api/health",
                "/api/status",
                "/scan",
                "/dashboard"
            ]
        }, 200
    
    # ==================================================
    # ERROR HANDLERS
    # ==================================================
    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Endpoint not found", "status": 404}, 404
    
    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal error: {str(e)}")
        return {"error": "Internal server error", "status": 500}, 500
    
    # ==================================================
    # WSGI HANDLER FOR VERCEL
    # ==================================================
    handler = app
    
    logger.info("Flask app initialized successfully for Vercel")

except Exception as e:
    logger.error(f"Failed to initialize Flask app: {str(e)}", exc_info=True)
    
    # Fallback minimal app
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return jsonify({"error": "App initialization failed", "message": str(e)}), 500
    
    handler = app

