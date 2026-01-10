"""
AI Chatbot Handler for Digital Footprint Scanner
------------------------------------------------
- Uses google.generativeai (Render-safe)
- Maintains chat sessions
- No ImportError on Render
"""

import os
import logging
import google.generativeai as genai

# -------------------------------------------------
# Logging
# -------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CHATBOT] %(levelname)s: %(message)s"
)

# -------------------------------------------------
# API KEY
# -------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    logging.error("❌ GEMINI_API_KEY not set")

# -------------------------------------------------
# Gemini Configuration (IMPORTANT)
# -------------------------------------------------
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
    logging.info("✅ Gemini configured successfully")
except Exception as e:
    logging.error(f"❌ Gemini init failed: {e}")
    model = None

# -------------------------------------------------
# Chat Sessions
# -------------------------------------------------
chat_sessions = {}

# -------------------------------------------------
# AI Chatbot
# -------------------------------------------------
class AIChatbot:
    def __init__(self, session_id="default"):
        self.session_id = session_id
        self.chat = None

        if not model:
            return

        if session_id not in chat_sessions:
            try:
                chat_sessions[session_id] = model.start_chat(history=[])
                logging.info(f"🧠 Chat session created: {session_id}")
            except Exception as e:
                logging.error(f"❌ Chat creation failed: {e}")
                return

        self.chat = chat_sessions.get(session_id)

    def generate_response(self, analysis_result: dict, user_query: str) -> str:
        if not self.chat:
            return "AI service unavailable. Please try again later."

        risk = analysis_result.get("risk_results", {}).get("risk_level", "LOW")
        platforms = analysis_result.get("scan_results", {}).get("platforms_found", [])
        accounts = ", ".join(platforms) if platforms else "None"

        prompt = (
            f"Risk Level: {risk}\n"
            f"Accounts Found: {accounts}\n\n"
            f"User Question: {user_query}\n"
            f"Give privacy and safety advice."
        )

        try:
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            logging.error(f"❌ Gemini error: {e}")
            return "AI service unavailable."

# -------------------------------------------------
# Helper
# -------------------------------------------------
def get_ai_response(analysis_result: dict, user_query: str, session_id="default"):
    return AIChatbot(session_id).generate_response(analysis_result, user_query)
