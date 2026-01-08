"""
AI Chatbot Handler for Digital Footprint Scanner
-------------------------------------------------
- Uses Google Gemini SDK (genai) for reliable AI responses
- Maintains chat sessions per user to preserve context
- Includes scan summary in chatbot responses
- Handles errors and missing API key gracefully
"""

import os
import logging
from google import genai

# -------------------------------
# Logging Setup
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CHATBOT HANDLER] %(levelname)s: %(message)s"
)

# -------------------------------
# Load Gemini API Key
# -------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logging.error("GEMINI_API_KEY not set! Chatbot will not work.")

# -------------------------------
# Initialize Gemini Client
# -------------------------------
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    logging.info("Gemini client initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize Gemini client: {e}")
    client = None

# -------------------------------
# Chat sessions per user
# -------------------------------
chat_sessions = {}  # key: session_id, value: genai.Chat object

# -------------------------------
# AI Chatbot Class
# -------------------------------
class AIChatbot:
    def __init__(self, session_id='default'):
        self.session_id = session_id
        if session_id not in chat_sessions:
            # Create new chat session with latest supported model
            try:
                chat_sessions[session_id] = client.chats.create(model='gemini-2.5-flash')
                logging.info(f"Created new chat session: {session_id}")
            except Exception as e:
                logging.error(f"Failed to create Gemini chat session: {e}")

        self.chat_session = chat_sessions.get(session_id)

    def generate_response(self, analysis_result: dict, user_query: str) -> str:
        if not self.chat_session:
            return "AI service unavailable. Chat session could not be created."

        # Build a concise scan summary
        risk_level = analysis_result.get("risk_results", {}).get("risk_level", "LOW")
        online_accounts = analysis_result.get("scan_results", {}).get("platforms_found", [])
        accounts_list = ', '.join([p.capitalize() for p in online_accounts]) if online_accounts else "None"
        summary = f"Risk Level: {risk_level}\nAccounts Found: {accounts_list}"

        # Construct the message for Gemini
        message = f"{summary}\nUser asked: {user_query}\nPlease provide a clear, actionable response with privacy advice."

        try:
            response = self.chat_session.send_message(message)
            reply = getattr(response, 'text', None) or str(response)
            if not reply:
                reply = "Gemini did not return a response."
            return reply
        except Exception as e:
            logging.error(f"Error sending message to Gemini: {e}")
            return "AI service unavailable. Please try again later."

# -------------------------------
# Helper function for routes.py
# -------------------------------
def get_ai_response(analysis_result: dict, user_query: str, session_id='default') -> str:
    chatbot = AIChatbot(session_id=session_id)
    return chatbot.generate_response(analysis_result, user_query)
