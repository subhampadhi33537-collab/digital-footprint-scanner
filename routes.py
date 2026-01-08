"""
AI-Powered Digital Footprint Scanner
All Flask routes (Web & API)
"""

import json
import os
from datetime import datetime
import traceback

from flask import (  # type: ignore
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

from config import config

# ==============================
# IMPORT CORE MODULES
# ==============================
from scanner.osint_scanner import run_full_scan
from analysis.risk_engine import calculate_risk
from ai_engine.chatbot_handler import get_ai_response

# ==============================
# CONSTANTS
# ==============================
RESULTS_DIR = os.path.join("static", "data")
RESULTS_FILE = os.path.join(RESULTS_DIR, "results.json")


# ==============================
# HELPER FUNCTIONS
# ==============================
def transform_scan_for_js(scan_results: dict, risk_results: dict) -> dict:
    platforms = []
    for platform in scan_results.get("platforms_found", []):
        platforms.append({
            "name": platform.capitalize(),
            "platform": platform,
            "found": True,
            "summary": f"Account found on {platform}"
        })

    exposures = {
        "personal": scan_results.get("names_found", []),
        "contact": [e.get("email") for e in scan_results.get("emails_found", [])],
        "online": scan_results.get("platforms_found", [])
    }

    return {
        "platforms": platforms,
        "exposures": exposures,
        "risk_level": risk_results.get("risk_level", "LOW"),
        "correlations": scan_results.get("platform_links", [])
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
def register_routes(app):

    # ==============================
    # HOME
    # ==============================
    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    # ==============================
    # SCAN API
    # ==============================
    @app.route("/scan", methods=["POST"])
    def scan():
        data = request.get_json() if request.is_json else request.form
        user_input = (data.get("user_input") or "").strip()

        if not user_input:
            return jsonify({"error": "User input is required"}), 400

        scan_results = run_full_scan(
            user_input=user_input,
            max_platforms=config.MAX_PLATFORMS,
            timeout=config.SCAN_TIMEOUT
        )

        risk_results = calculate_risk(scan_results)

        dashboard_payload = transform_scan_for_js(
            scan_results=scan_results,
            risk_results=risk_results
        )

        save_results(dashboard_payload)

        # ✅ SAFE session storage (NO clear)
        session["user_input"] = user_input
        session["scan_results"] = scan_results
        session["risk_results"] = risk_results
        session.modified = True

        return jsonify(dashboard_payload)

    # ==============================
    # DASHBOARD
    # ==============================
    @app.route("/dashboard", methods=["GET"])
    def dashboard():
        latest = load_latest_result()
        if not latest:
            return redirect(url_for("index"))

        return render_template(
            "dashboard.html",
            scan_results=latest,
            risk_results={"risk_level": latest.get("risk_level", "LOW")},
            user_input=session.get("user_input", "")
        )

    # ==============================
    # DASHBOARD DATA
    # ==============================
    @app.route("/dashboard-data", methods=["GET"])
    def dashboard_data():
        return jsonify(load_latest_result() or {})

    # ==============================
    # CHATBOT PAGE
    # ==============================
    @app.route("/chatbot", methods=["GET"])
    def chatbot():
        return render_template(
            "chatbot.html",
            user_input=session.get("user_input", "")
        )

    # ==============================
    # AI CHATBOT API (FIXED)
    # ==============================
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
    # HEALTH CHECK
    # ==============================
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "OK",
            "timestamp": datetime.utcnow().isoformat()
        })
