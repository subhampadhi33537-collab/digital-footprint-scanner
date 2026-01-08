"""
AI-Powered Digital Footprint Scanner
Main Flask Application Entry Point

Responsibilities:
- Initialize Flask app
- Load and validate configuration
- Register API & web routes
- Handle sessions and debugging
- Serve as central backbone for scanner, analysis, and AI
"""

from flask import Flask  # type: ignore
from flask_session import Session  # type: ignore
from dotenv import load_dotenv  # type: ignore

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
# FLASK CORE CONFIG
# ==================================================
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["DEBUG"] = config.FLASK_DEBUG
app.config["ENV"] = config.FLASK_ENV

# ==================================================
# SERVER-SIDE SESSION CONFIGURATION (CRITICAL FIX)
# ==================================================
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./.flask_session"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_KEY_PREFIX"] = "dfs_"

Session(app)

# ==================================================
# VALIDATE CONFIGURATION
# ==================================================
try:
    config.validate()
except Exception as e:
    print("❌ Configuration validation failed:", e)
    raise SystemExit(1)

# ==================================================
# REGISTER ROUTES
# ==================================================
from routes import register_routes  # noqa: E402

register_routes(app)

# ==================================================
# ERROR HANDLERS
# ==================================================
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404 - Page Not Found</h1>", 404


@app.errorhandler(500)
def internal_error(e):
    return "<h1>500 - Internal Server Error</h1>", 500


# ==================================================
# MAIN ENTRY POINT
# ==================================================
if __name__ == "__main__":
    print("🚀 Starting AI-Powered Digital Footprint Scanner...")
    print(f"🔹 Flask ENV: {config.FLASK_ENV}")
    print(f"🔹 Debug Mode: {config.FLASK_DEBUG}")
    app.run(host="0.0.0.0", port=5000)
