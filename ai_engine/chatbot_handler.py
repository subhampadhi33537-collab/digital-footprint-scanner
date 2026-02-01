"""
AI Chatbot Handler for Digital Footprint Scanner
------------------------------------------------
- Uses Groq API (OpenAI-compatible format)
- Maintains chat sessions
- Efficient and reliable
"""

import os
import logging
from ai_engine.groq_client import GroqClient, get_groq_client

# -------------------------------------------------
# Logging
# -------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CHATBOT] %(levelname)s: %(message)s"
)

# -------------------------------------------------
# API KEY CHECK
# -------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    logging.error("❌ GROQ_API_KEY not set")

# -------------------------------------------------
# Initialize Groq Client
# -------------------------------------------------
try:
    groq_client = get_groq_client()
    logging.info("✅ Groq client initialized successfully")
except Exception as e:
    logging.error(f"❌ Groq client init failed: {e}")
    groq_client = None

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
        self.chat_history = []

        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                "history": [],
                "client": groq_client
            }
            logging.info(f"🧠 Chat session created: {session_id}")

        self.chat_data = chat_sessions.get(session_id)

    def generate_response(self, analysis_result: dict, user_query: str) -> str:
        if not groq_client:
            return "AI service unavailable. Please try again later."

        risk = analysis_result.get("risk_results", {}).get("risk_level", "LOW")
        platforms = analysis_result.get("scan_results", {}).get("platforms_found", [])
        accounts = ", ".join(platforms) if platforms else "None"

        # Concise, fast-response prompt
        prompt = (
            f"Risk Level: {risk}\n"
            f"Accounts Found: {accounts}\n"
            f"User Question: {user_query}\n\n"
            "Provide a SHORT, ACTIONABLE response (3-5 sentences max):\n"
            "• Use bullet points for key items\n"
            "• Bold important terms: **term**\n"
            "• Add relevant emojis (🔒 🛡️ ✅ ⚠️)\n"
            "Focus on immediate privacy recommendations."
        )

        # Build messages with chat history
        messages = self.chat_data["history"].copy()
        messages.append({"role": "user", "content": prompt})

        try:
            response_text = groq_client.chat(messages)
            
            # Store in history for context
            self.chat_data["history"].append({"role": "user", "content": prompt})
            self.chat_data["history"].append({"role": "assistant", "content": response_text})
            
            # Keep history manageable (last 10 exchanges)
            if len(self.chat_data["history"]) > 20:
                self.chat_data["history"] = self.chat_data["history"][-20:]
            
            return response_text
        except Exception as e:
            logging.error(f"❌ Groq error: {e}")
            return "AI service unavailable."

# -------------------------------------------------
# Helper
# -------------------------------------------------
def get_ai_response(analysis_result: dict, user_query: str, session_id="default"):
    return AIChatbot(session_id).generate_response(analysis_result, user_query)
