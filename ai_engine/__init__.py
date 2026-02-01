"""
AI Engine Package Initialization
---------------------------------------------------
Responsibilities:
- Initialize AI engine for Digital Footprint Scanner
- Expose chatbot interface, AI explainer, and Groq client
- Connect scanner and analysis outputs to AI assistant
- Ready for routes.py, dashboard, and hackathon demo
"""

# ===============================
# IMPORT MODULES
# ===============================
from .chatbot_handler import AIChatbot, get_ai_response
from .groq_client import GroqClient
from .ai_explainer import explain_analysis, get_explanation_for_user

import logging

# ===============================
# LOGGING SETUP
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AI ENGINE INIT] %(levelname)s: %(message)s"
)

# ===============================
# PACKAGE LEVEL INTERFACE
# ===============================
__all__ = [
    "AIChatbot",
    "get_ai_response",
    "GroqClient",
    "explain_analysis",
    "get_explanation_for_user"
]

# ===============================
# UNIFIED AI FUNCTION
# ===============================
def analyze_and_explain(analysis_result: dict, user_query: str = None) -> dict:
    """
    Unified interface for AI engine:
    - Optionally takes a user query (for chatbot)
    - Provides AI explanation and response
    Args:
        analysis_result (dict): Output from analysis.analyze_user_data()
        user_query (str): Optional user query for AI assistant
    Returns:
        dict: {
            'ai_explanation': str,
            'ai_chat_response': str
        }
    """
    logging.info("Starting AI Engine unified analysis and explanation")

    # -------------------------------
    # Generate Explanation
    # -------------------------------
    explanation_text = get_explanation_for_user(analysis_result)

    # -------------------------------
    # Generate Chat Response (if query provided)
    # -------------------------------
    chat_response = None
    if user_query:
        chatbot = AIChatbot()
        chat_response = chatbot.generate_response(analysis_result, user_query)

    result = {
        "ai_explanation": explanation_text,
        "ai_chat_response": chat_response
    }

    logging.info("AI Engine analysis and explanation completed")
    return result

# ===============================
# PACKAGE READY MESSAGE
# ===============================
logging.info("✅ AI Engine package initialized. All modules loaded and ready.")
