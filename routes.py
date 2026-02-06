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
from scanner.progress_tracker import scan_progress
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

    # ==============================
    # DEBUG & TEST ENDPOINTS
    # ==============================
    @app.route("/debug", methods=["GET"])
    def debug_page():
        """Debug page to test frontend-backend connectivity"""
        return """<!DOCTYPE html>
<html>
<head>
    <title>Digital Footprint Scanner - Debug</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-white p-8">
    <div class="max-w-2xl mx-auto">
        <h1 class="text-3xl font-bold mb-6">🔍 Scanner Debug Console</h1>
        
        <div class="space-y-4">
            <div class="bg-slate-800 p-4 rounded">
                <h2 class="font-bold mb-2">1. Backend Health Check</h2>
                <button onclick="testHealth()" class="bg-indigo-600 px-4 py-2 rounded">Test Backend</button>
                <pre id="health-result" class="mt-2 bg-slate-900 p-2 text-sm hidden"></pre>
            </div>
            
            <div class="bg-slate-800 p-4 rounded">
                <h2 class="font-bold mb-2">2. Quick Scan Test</h2>
                <input type="text" id="test-input" placeholder="testuser" class="bg-slate-700 px-3 py-2 rounded w-full text-black mb-2">
                <button onclick="testScan()" class="bg-indigo-600 px-4 py-2 rounded">Test Scan API</button>
                <pre id="scan-result" class="mt-2 bg-slate-900 p-2 text-sm max-h-64 overflow-auto hidden"></pre>
            </div>
            
            <a href="/" class="inline-block bg-purple-600 px-4 py-2 rounded">Back to Scanner</a>
        </div>
    </div>
    
    <script>
        async function testHealth() {
            const result = document.getElementById('health-result');
            try {
                const resp = await fetch('/health');
                const data = await resp.json();
                result.textContent = '✅ Backend OK\\n' + JSON.stringify(data, null, 2);
                result.classList.remove('hidden');
                result.classList.add('text-green-400');
            } catch (e) {
                result.textContent = '❌ Connection Failed: ' + e.message;
                result.classList.remove('hidden');
                result.classList.add('text-red-400');
            }
        }
        
        async function testScan() {
            const input = document.getElementById('test-input').value.trim();
            const result = document.getElementById('scan-result');
            
            if (!input) {
                result.textContent = '❌ Please enter a username';
                result.classList.remove('hidden', 'text-green-400');
                result.classList.add('text-red-400');
                return;
            }
            
            try {
                result.textContent = '⏳ Scanning ' + input + '...';
                result.classList.remove('hidden', 'text-green-400', 'text-red-400');
                
                const resp = await fetch('/scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_input: input })
                });
                
                const data = await resp.json();
                
                if (!resp.ok) {
                    result.textContent = '❌ Scan Error (' + resp.status + '):\\n' + JSON.stringify(data, null, 2);
                    result.classList.add('text-red-400');
                } else {
                    const summary = {
                        'Status': '✅ Success',
                        'Platforms': data.all_platforms_checked?.length || 0,
                        'Risk Score': data.ml_risk_score,
                        'Exposures': data.total_exposures
                    };
                    result.textContent = JSON.stringify(summary, null, 2);
                    result.classList.add('text-green-400');
                }
            } catch (e) {
                result.textContent = '❌ Network Error: ' + e.message;
                result.classList.remove('hidden');
                result.classList.add('text-red-400');
            }
        }
        
        testHealth();
    </script>
</body>
</html>"""

    # ==============================
    # HEALTH CHECK
    # ==============================
    @app.route("/health", methods=["GET"])
    def health_check():
        """Simple health check endpoint"""
        return jsonify({
            "status": "ok",
            "service": "Digital Footprint Scanner",
            "version": "2.0",
            "ml_models_ready": True,
            "timestamp": datetime.now().isoformat()
        }), 200

    # ==============================
    # WEB ROUTES
    # ==============================

    # ------------------------------
    # HOME (Professional ML+AI Version)
    # ------------------------------
    @app.route("/", methods=["GET"])
    def index():
        logger.info("Loading professional home page...")
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

        # Clear session to force fresh scan (prevent cached results)
        session.pop("scan_results", None)
        session.pop("risk_results", None)
        session.modified = True
        
        logger.info(f"[SCAN] Starting FRESH scan for: {user_input}")
        logger.info(f"[SCAN] Cleared cached session data")
        
        # Flush output immediately
        import sys
        sys.stdout.flush()
        sys.stderr.flush()
        
        try:
            # Step 1: Run full scan
            logger.info("[SCAN] Step 1: Running full scan...")
            import sys; sys.stdout.flush()
            scan_results = run_full_scan(
                user_input=user_input,
                max_platforms=config.MAX_PLATFORMS,
                timeout=config.SCAN_TIMEOUT
            )
            logger.info(f"[SCAN] Full scan completed. Found {len(scan_results.get('all_platforms_checked', []))} platforms")

            # Step 2: Calculate risk
            logger.info("[SCAN] Step 2: Calculating risk...")
            risk_results = calculate_risk(scan_results)
            logger.info(f"[SCAN] Risk calculated")
            
            # Step 3: ML analysis
            logger.info("[SCAN] Step 3: Running ML analysis...")
            try:
                groq_client = GroqClient()
                ml_analysis = get_ml_risk_analysis(scan_results, groq_client)
                logger.info(f"[SCAN] ML analysis completed")
            except Exception as ml_error:
                logger.warning(f"[SCAN] ML analysis failed: {ml_error}. Using defaults.")
                ml_analysis = {"ml_analysis": {}, "groq_analysis": ""}
            
            # Step 4: Anomaly detection
            logger.info("[SCAN] Step 4: Running anomaly detection...")
            try:
                anomalies = get_comprehensive_anomaly_analysis(scan_results)
                logger.info(f"[SCAN] Anomaly detection completed")
            except Exception as anom_error:
                logger.warning(f"[SCAN] Anomaly detection failed: {anom_error}. Using defaults.")
                anomalies = {}
            
            # Step 5: Threat intelligence
            logger.info("[SCAN] Step 5: Running threat intelligence...")
            try:
                threat_intel = get_complete_threat_intelligence(scan_results, ml_analysis.get("ml_analysis", {}), anomalies, groq_client)
                logger.info(f"[SCAN] Threat intelligence completed")
            except Exception as threat_error:
                logger.warning(f"[SCAN] Threat intelligence failed: {threat_error}. Using defaults.")
                threat_intel = {}
            
            # Step 6: Transform for JS
            logger.info("[SCAN] Step 6: Transforming results for dashboard...")
            dashboard_payload = transform_scan_for_js(
                scan_results=scan_results,
                risk_results=risk_results,
                user_input=user_input
            )
            
            # ✅ Include all advanced analyses in payload
            dashboard_payload["ml_analysis"] = ml_analysis.get("ml_analysis", {})
            dashboard_payload["groq_analysis"] = ml_analysis.get("groq_analysis", "")
            dashboard_payload["anomalies"] = anomalies
            dashboard_payload["threat_intel"] = threat_intel

            # ✅ Add unique timestamp to results (prevents caching)
            dashboard_payload["scan_timestamp"] = datetime.now().isoformat()
            dashboard_payload["scan_id"] = f"{user_input}_{int(datetime.now().timestamp()*1000)}"
            
            # ✅ Save to disk for persistence
            logger.info("[SCAN] Step 7: Saving results to disk...")
            save_results(dashboard_payload)

            # ✅ Save complete payload to session (for dashboard)
            session["user_input"] = user_input
            session["scan_results"] = dashboard_payload
            session["risk_results"] = risk_results
            session["last_scan_timestamp"] = datetime.now().isoformat()
            session.modified = True

            logger.info(f"[OK] Scan completed successfully for: {user_input}")
            logger.info(f"[SCAN ID] {dashboard_payload['scan_id']}")
            logger.info(f"[RESULTS] Platforms checked: {len(dashboard_payload.get('all_platforms_checked', []))}")
            logger.info(f"[RESULTS] Risk level: {dashboard_payload.get('risk_level', 'UNKNOWN')}")
            
            # Add no-cache headers to response
            response = jsonify(dashboard_payload)
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response, 200

        except Exception as e:
            import traceback
            logger.error(f"[ERROR] Scan error: {type(e).__name__}: {e}")
            logger.error(f"[ERROR] Traceback: {traceback.format_exc()}")
            return jsonify({
                "error": f"Scan failed: {type(e).__name__}: {str(e)[:100]}"
            }), 500

    # ==============================
    # REAL-TIME PROGRESS ENDPOINT
    # ==============================
    @app.route("/api/scan-progress", methods=["GET"])
    def get_scan_progress():
        """Get real-time scan progress"""
        try:
            progress = scan_progress.get_progress()
            return jsonify({
                "status": "success",
                "progress": progress
            }), 200
        except Exception as e:
            logger.error(f"Progress fetch error: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

    # ------------------------------
    # DASHBOARD (Professional ML+AI Version)
    # ------------------------------
    @app.route("/dashboard", methods=["GET"])
    def dashboard():
        """Professional company-grade dashboard with ML insights"""
        logger.info("Loading professional dashboard with ML insights...")
        return render_template("dashboard.html")

    # ------------------------------
    # DASHBOARD DATA
    # ------------------------------
    @app.route("/dashboard-data", methods=["GET"])
    def dashboard_data():
        # Always get fresh data from session (no caching)
        if session.get("scan_results"):
            payload = session.get("scan_results")
            user_input = session.get("user_input", "")
            risk_results = session.get("risk_results", {})
            
            logger.info(f"[DASHBOARD] Loading scan results for: {user_input}")
            logger.info(f"[DASHBOARD] Scan ID: {payload.get('scan_id', 'unknown')}")
            
            # Add unique timestamp to prevent browser caching
            payload["nocache"] = datetime.now().isoformat()
            
            response = jsonify(payload)
            # Disable all caching
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        
        # Return empty structure if no session (no cached data)
        logger.warning("[DASHBOARD] No scan data in session")
        return jsonify({
            "user_input": "",
            "platforms": [],
            "exposures": {"personal": [], "contact": [], "online": []},
            "risk_level": "UNKNOWN",
            "message": "No scan performed yet. Please run a scan first."
        })

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

    # ==============================
    # ALIAS ROUTES (For backward compatibility)
    # ==============================
    @app.route("/dashboard-pro")
    def dashboard_pro():
        """Professional company-grade dashboard - redirects to main dashboard"""
        return render_template("dashboard.html")

    @app.route("/index-pro")
    def index_pro():
        """Professional landing page - redirects to main index"""
        return render_template("index.html")

    @app.route("/api/dashboard-data", methods=["GET"])
    def get_dashboard_data():
        """
        Return all scan data for dashboard rendering
        Includes ML analysis, threat intelligence, and anomaly detection
        """
        try:
            # Require fresh scan data from session (no fallback cached data)
            if "scan_results" not in session:
                logger.warning("[API] No scan results in session - returning empty")
                return jsonify({
                    "user_input": "",
                    "timestamp": datetime.now().isoformat(),
                    "scan_id": "NO_SCAN",
                    "message": "No active scan. Please perform a scan first.",
                    "all_platforms_checked": [],
                    "platforms_found": [],
                    "risk_level": "UNKNOWN",
                    "ml_analysis": {},
                    "anomalies": {},
                    "threat_intel": {}
                }), 200
            
            scan_data = session["scan_results"]
            user_input = session.get("user_input", "UNKNOWN")
            
            logger.info(f"[API] Serving dashboard data for: {user_input}")
            logger.info(f"[API] Scan ID: {scan_data.get('scan_id', 'unknown')}")
            
            # Ensure all required fields exist
            if "ml_analysis" not in scan_data:
                scan_data["ml_analysis"] = {}
            if "anomalies" not in scan_data:
                scan_data["anomalies"] = {}
            if "threat_intel" not in scan_data:
                scan_data["threat_intel"] = {}
            
            # Add anti-cache timestamp
            scan_data["api_fetch_time"] = datetime.now().isoformat()
            
            response = jsonify(scan_data)
            # Disable all caching
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response, 200
            
        except Exception as e:
            logger.error(f"[API] Dashboard data error: {e}")
            return jsonify({"error": str(e)}), 500

    # ==============================
    # ML TRAINING & MODEL ENDPOINTS
    # ==============================
    @app.route("/api/ml/train-all", methods=["POST"])
    def train_all_models():
        """Trigger training of all ML models"""
        try:
            from analysis.ml_model_trainer import get_ml_trainer
            
            trainer = get_ml_trainer()
            results = trainer.train_all_models()
            
            logger.info(f"✅ All models trained successfully: {results}")
            
            return jsonify({
                "status": "success",
                "message": "All models trained successfully",
                "results": results
            }), 200
            
        except Exception as e:
            logger.error(f"Model training error: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

    @app.route("/api/ml/model-status", methods=["GET"])
    def get_model_status():
        """Get status of trained models"""
        try:
            from pathlib import Path
            
            models_dir = Path("data/models")
            training_dir = Path("data/training_data")
            
            model_count = len(list(models_dir.glob("*.pkl"))) if models_dir.exists() else 0
            training_files = len(list(training_dir.glob("*.json"))) if training_dir.exists() else 0
            
            return jsonify({
                "status": "healthy",
                "models_trained": model_count > 0,
                "model_count": model_count,
                "training_data_files": training_files,
                "models_directory": str(models_dir.absolute()),
                "training_data_directory": str(training_dir.absolute())
            }), 200
            
        except Exception as e:
            logger.error(f"Model status error: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

    # ==============================
    # ML-ENHANCED SCAN ENDPOINT
    # ==============================
    @app.route("/scan-ml", methods=["POST"])
    def scan_with_ml():
        """
        Enhanced scan with ML model predictions
        Returns scan results with ML risk scores and predictions
        """
        try:
            data = request.get_json() if request.is_json else request.form
            user_input = (data.get("user_input") or "").strip()

            if not user_input:
                return jsonify({"error": "User input is required"}), 400

            logger.info(f"[ML SCAN] Starting ML-enhanced scan for: {user_input}")

            # Run OSINT scan
            scan_results = run_full_scan(user_input)
            
            # Calculate risk
            risk_results = calculate_risk(scan_results)
            
            # ML risk analysis
            ml_analysis = get_ml_risk_analysis(scan_results)
            
            # Anomaly detection
            anomalies = get_comprehensive_anomaly_analysis(scan_results)
            
            # Threat intelligence
            groq_client = GroqClient()
            threat_analysis = get_complete_threat_intelligence(
                scan_results, ml_analysis, anomalies, groq_client
            )
            
            # Combine all results
            combined_results = {
                **scan_results,
                **risk_results,
                "ml_analysis": ml_analysis,
                "anomalies": anomalies,
                "threat_intelligence": threat_analysis,
                "ml_risk_score": ml_analysis.get("ml_risk_score", 50),
                "scan_timestamp": datetime.now().isoformat()
            }

            # Save to session
            session["scan_results"] = combined_results
            session.modified = True

            # Save to file
            os.makedirs(RESULTS_DIR, exist_ok=True)
            with open(RESULTS_FILE, "w") as f:
                json.dump(combined_results, f, indent=2)

            logger.info(f"✅ ML scan completed for: {user_input}")

            return jsonify({
                "status": "success",
                "data": combined_results,
                "message": "ML-enhanced scan completed"
            }), 200

        except Exception as e:
            logger.error(f"ML scan error: {e}")
            logger.error(traceback.format_exc())
            return jsonify({
                "error": str(e),
                "message": "ML-enhanced scan failed"
            }), 500

    # ==============================
    # AI CHATBOT ENDPOINT
    # ==============================
    @app.route("/api/chat-with-ai", methods=["POST"])
    def chat_with_ai():
        """
        Chat endpoint for users to ask AI questions about their scan results
        """
        try:
            data = request.get_json()
            message = data.get("message", "")
            scan_context = data.get("scan_context", {})

            if not message:
                return jsonify({"error": "Message is required"}), 400

            logger.info(f"[CHATBOT] User asking: {message[:100]}...")

            # Initialize Groq client properly
            from ai_engine.groq_client import get_groq_client
            groq_client = get_groq_client()

            # Build system prompt with context
            system_prompt = """You are a helpful AI security advisor for the Digital Footprint Scanner tool. 
You help users understand their digital footprint scan results and provide actionable security recommendations.

IMPORTANT: Keep responses concise (2-3 sentences max), friendly, and actionable.
Focus on privacy and security best practices based on the scan results provided."""

            # Send to Groq API using the correct method
            try:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
                
                ai_response = groq_client.chat(messages)
                
                if ai_response.startswith("Error:"):
                    logger.warning(f"[CHATBOT] API error: {ai_response}")
                    return jsonify({
                        "response": "I'm temporarily unable to connect to the AI service. Please try again.",
                        "status": "error"
                    }), 200
                
                logger.info(f"[CHATBOT] ✅ Response generated")

                return jsonify({
                    "response": ai_response,
                    "status": "success"
                }), 200

            except Exception as groq_error:
                logger.error(f"[CHATBOT] Groq API Error: {groq_error}")
                return jsonify({
                    "response": "I'm temporarily unable to connect to the AI service. Please try again.",
                    "status": "error"
                }), 200

        except Exception as e:
            logger.error(f"[CHATBOT] Error: {e}")
            return jsonify({
                "error": str(e),
                "response": "An error occurred processing your message."
            }), 500
    # ==============================
    # ENTERPRISE FEATURES
    # ==============================
    
    @app.route("/api/export", methods=["POST"])
    def export_results():
        """Export scan results in multiple formats"""
        try:
            from routes_enterprise import export_to_json, export_to_csv, export_to_pdf, audit_logger
            
            data = request.json or {}
            format_type = data.get("format", "json").lower()
            results = data.get("results", {})
            
            audit_logger.log("export", request.remote_addr, {"format": format_type})
            
            if format_type == "json":
                return jsonify(export_to_json(results)), 200
            elif format_type == "csv":
                return export_to_csv(results), 200, {"Content-Type": "text/csv"}
            elif format_type == "pdf":
                pdf_data = export_to_pdf(results)
                return pdf_data, 200, {
                    "Content-Type": "application/pdf",
                    "Content-Disposition": "attachment;filename=scan_report.pdf"
                }
            else:
                return jsonify({"error": "Unsupported format"}), 400
                
        except Exception as e:
            logger.error(f"Export error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/analytics", methods=["GET"])
    def get_analytics():
        """Get usage analytics and statistics"""
        try:
            from routes_enterprise import analytics
            
            return jsonify({
                "status": "success",
                "analytics": analytics.get_stats()
            }), 200
            
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/status", methods=["GET"])
    def system_status():
        """Get system status and health"""
        try:
            from routes_enterprise import get_system_status
            
            return jsonify(get_system_status()), 200
            
        except Exception as e:
            logger.error(f"Status error: {e}")
            return jsonify({"error": str(e), "status": "error"}), 500
    
    @app.route("/api/history", methods=["GET"])
    def scan_history():
        """Get scan result history"""
        try:
            from routes_enterprise import result_history
            
            limit = request.args.get("limit", 50, type=int)
            history = result_history.get_history(limit=limit)
            
            return jsonify({
                "status": "success",
                "total_scans": len(history),
                "history": history
            }), 200
            
        except Exception as e:
            logger.error(f"History error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/history/<scan_id>", methods=["GET"])
    def get_scan_result(scan_id):
        """Get specific scan result"""
        try:
            from routes_enterprise import result_history
            
            data = result_history.get_by_id(scan_id)
            
            if data:
                return jsonify({
                    "status": "success",
                    "scan_id": scan_id,
                    "data": data
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "Scan not found"
                }), 404
                
        except Exception as e:
            logger.error(f"History lookup error: {e}")
            return jsonify({"error": str(e)}), 500