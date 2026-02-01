"""
AI-Powered Digital Footprint Scanner
All Flask routes (Web & API) with Google OAuth integration
"""

import json
import os
import traceback
import logging
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

from config import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ROUTES] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ==============================
# IMPORT CORE MODULES
# ==============================
from scanner.osint_scanner import run_full_scan
from analysis.risk_engine import calculate_risk
from analysis.ml_risk_engine import get_ml_risk_analysis  # ✅ NEW: ML Analysis
from analysis.anomaly_detector import get_comprehensive_anomaly_analysis  # ✅ NEW: Anomaly Detection
from analysis.threat_intel import get_complete_threat_intelligence  # ✅ NEW: Threat Intel
from ai_engine.chatbot_handler import get_ai_response
from ai_engine.groq_client import GroqClient  # ✅ NEW: For Groq ML integration

# ==============================
# GOOGLE OAUTH IMPORTS
# ==============================
from google_auth_oauthlib.flow import Flow
import googleapiclient.discovery

# ==============================
# CONSTANTS
# ==============================
RESULTS_DIR = os.path.join("static", "data")
RESULTS_FILE = os.path.join(RESULTS_DIR, "results.json")
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.readonly"
]
# Use environment variable for Vercel compatibility
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://127.0.0.1:5000/callback")

# ==============================
# HELPER FUNCTIONS
# ==============================
def transform_scan_for_js(scan_results: dict, risk_results: dict, user_input: str = "") -> dict:
    """Build dashboard payload from real scan results. Shows ALL platforms checked (found + not found)."""
    platforms = []
    all_checked = scan_results.get("all_platforms_checked", [])
    
    # Build platform cards with real results
    if all_checked:
        for entry in all_checked:
            plat = entry.get("platform", "")
            url = entry.get("url", "")
            status = entry.get("status", "unknown")
            found = status == "found"
            
            # Determine status label
            if status == "found":
                status_label = "[OK] Found"
                badge_class = "bg-green-100 text-green-800"
            elif status == "not_found":
                status_label = "[Not Found]"
                badge_class = "bg-gray-100 text-gray-700"
            elif status == "timeout":
                status_label = "[TIMEOUT] Timeout"
                badge_class = "bg-yellow-100 text-yellow-800"
            elif status == "error":
                status_label = "[ERROR] Error"
                badge_class = "bg-red-100 text-red-800"
            else:
                status_label = f"[??] {status.title()}"
                badge_class = "bg-gray-100 text-gray-700"
            
            platforms.append({
                "name": plat.capitalize(),
                "platform": plat,
                "found": found,
                "summary": f"{'[OK] Account found' if found else '[Not Found]'}: {plat.capitalize()}",
                "url": url if url else "",
                "status": status,
                "status_label": status_label,
                "badge_class": badge_class,
            })

    def _email_display(e):
        return e.get("email") or e.get("url") or e.get("detail") or ""

    exposures = {
        "personal": scan_results.get("names_found", []),
        "contact": [x for x in (_email_display(e) for e in scan_results.get("emails_found", [])) if x],
        "online": list(scan_results.get("platforms_found", [])),
    }

    return {
        "user_input": user_input or scan_results.get("user_input", ""),
        "platforms": platforms,
        "exposures": exposures,
        "risk_level": risk_results.get("risk_level", "LOW"),
        "correlations": list(scan_results.get("platform_links", [])),
    }

def save_results(payload: dict) -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)

def load_latest_result():
    if not os.path.exists(RESULTS_FILE):
        return None
    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

# ==============================
# ROUTES REGISTRATION
# ==============================
def register_routes(app: Flask):

    # ------------------------------
    # HOME
    # ------------------------------
    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    # ------------------------------
    # GOOGLE OAUTH LOGIN
    # ------------------------------
    @app.route("/login")
    def login():
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        auth_url, _ = flow.authorization_url(prompt="consent")
        session['oauth_flow'] = flow
        return redirect(auth_url)

    @app.route("/callback")
    def callback():
        flow: Flow = session.get('oauth_flow')
        if not flow:
            return "OAuth flow not found in session. Please login again.", 400

        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials

        # Save credentials in session
        session['google_creds'] = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }

        # Fetch Gmail profile
        service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        session['user_email'] = profile.get('emailAddress', 'Unknown')

        return render_template("login_success.html", email=session['user_email'])

    # ------------------------------
    # SCAN API
    # ------------------------------
    @app.route("/scan", methods=["POST"])
    def scan():
        data = request.get_json() if request.is_json else request.form
        user_input = (data.get("user_input") or "").strip()

        if not user_input:
            return jsonify({"error": "User input is required"}), 400

        logger.info(f"[SCAN] Starting scan for: {user_input}")
        
        try:
            scan_results = run_full_scan(
                user_input=user_input,
                max_platforms=config.MAX_PLATFORMS,
                timeout=config.SCAN_TIMEOUT
            )

            risk_results = calculate_risk(scan_results)
            
            # ✅ NEW: Groq client for ML integration
            groq_client = GroqClient()
            
            # ✅ NEW: ML-based risk analysis with Groq
            ml_analysis = get_ml_risk_analysis(scan_results, groq_client)
            
            # ✅ NEW: Anomaly detection
            anomalies = get_comprehensive_anomaly_analysis(scan_results)
            
            # ✅ NEW: Threat intelligence
            threat_intel = get_complete_threat_intelligence(scan_results, ml_analysis.get("ml_analysis", {}), anomalies, groq_client)
            
            dashboard_payload = transform_scan_for_js(
                scan_results=scan_results,
                risk_results=risk_results,
                user_input=user_input
            )
            
            # ✅ NEW: Include all advanced analyses in payload
            dashboard_payload["ml_analysis"] = ml_analysis.get("ml_analysis", {})
            dashboard_payload["groq_analysis"] = ml_analysis.get("groq_analysis", "")
            dashboard_payload["anomalies"] = anomalies
            dashboard_payload["threat_intel"] = threat_intel

            # ✅ Save to disk for persistence
            save_results(dashboard_payload)

            # ✅ Save to session
            session["user_input"] = user_input
            session["scan_results"] = scan_results
            session["risk_results"] = risk_results
            session.modified = True

            logger.info(f"[OK] Scan completed for: {user_input}")
            return jsonify(dashboard_payload), 200

        except Exception as e:
            logger.error(f"[ERROR] Scan error: {e}")
            return jsonify({"error": "Scan failed. Please try again."}), 500

    # ------------------------------
    # DASHBOARD
    # ------------------------------
    @app.route("/dashboard", methods=["GET"])
    def dashboard():
        # Try to get from session first (most recent scan)
        user_input = session.get("user_input")
        scan_results = session.get("scan_results")
        risk_results = session.get("risk_results")
        
        if user_input and scan_results and risk_results:
            latest = transform_scan_for_js(
                scan_results=scan_results,
                risk_results=risk_results,
                user_input=user_input
            )
            logger.info(f"[OK] Dashboard: Using session data for {user_input}")
        else:
            # Fallback to saved results file
            latest = load_latest_result()
            if not latest or not latest.get("user_input"):
                logger.warning("No scan data found, redirecting to home")
                return redirect(url_for("index"))

        return render_template(
            "dashboard.html",
            scan_results=latest,
            user_input=latest.get("user_input", "")
        )

    # ------------------------------
    # DASHBOARD DATA
    # ------------------------------
    @app.route("/dashboard-data", methods=["GET"])
    def dashboard_data():
        # Try session first (most recent scan)
        if session.get("scan_results") and session.get("risk_results"):
            payload = transform_scan_for_js(
                scan_results=session.get("scan_results", {}),
                risk_results=session.get("risk_results", {}),
                user_input=session.get("user_input", "")
            )
            return jsonify(payload)
        
        # Fallback to file if no session
        result = load_latest_result()
        return jsonify(result or {})

    # ------------------------------
    # CHATBOT PAGE
    # ------------------------------
    @app.route("/chatbot", methods=["GET"])
    def chatbot():
        return render_template(
            "chatbot.html",
            user_input=session.get("user_input", "")
        )

    # ------------------------------
    # AI CHATBOT API
    # ------------------------------
    @app.route("/ai-assistant", methods=["POST"])
    def ai_assistant():
        try:
            data = request.get_json(silent=True) or {}
            user_message = data.get("message", "").strip()

            if not user_message:
                return jsonify({"error": "Empty message"}), 400

            scan_results = session.get("scan_results")
            risk_results = session.get("risk_results")

            if not scan_results or not risk_results:
                return jsonify({
                    "reply": "No scan data available. Please run a scan first."
                })

            ai_reply = get_ai_response(
                analysis_result={
                    "scan_results": scan_results,
                    "risk_results": risk_results
                },
                user_query=user_message
            )

            return jsonify({"reply": ai_reply})

        except Exception:
            print("❌ AI ASSISTANT ERROR")
            print(traceback.format_exc())
            return jsonify({
                "reply": "AI service unavailable. Please try again later."
            }), 500

    # ------------------------------
    # HEALTH CHECK
    # ------------------------------
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "OK",
            "timestamp": datetime.utcnow().isoformat()
        })
