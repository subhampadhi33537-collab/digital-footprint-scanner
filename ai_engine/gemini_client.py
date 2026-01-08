"""
Gemini Client for Digital Footprint Scanner
---------------------------------------------------
Responsibilities:
- Handle all interactions with Google Gemini API
- Send prompts, receive responses, and handle errors
- Provide unified interface for chatbot_handler.py or other AI modules
- Fully connected to analysis output, routes, and dashboard
"""

import os
import json
import logging
import requests # type: ignore
from config import config

# -------------------------------
# Logging Setup
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [GEMINI CLIENT] %(levelname)s: %(message)s"
)

# -------------------------------
# Gemini Client Class
# -------------------------------
class GeminiClient:
    def __init__(self, api_key: str = None):
        """
        Initialize Gemini Client
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or getattr(config, "GEMINI_API_KEY", None)
        if not self.api_key:
            logging.error("GEMINI API KEY not provided. GeminiClient will not work properly.")
        self.endpoint = getattr(config, "GEMINI_API_URL", "https://api.google.com/gemini/v1/generate")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logging.info("GeminiClient initialized successfully.")

    # -------------------------------
    # Generate AI Response
    # -------------------------------
    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Send a prompt to Gemini API and return the response
        Args:
            prompt (str): Prompt text
            max_tokens (int): Maximum tokens to generate
        Returns:
            str: AI response
        """
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9
        }

        try:
            logging.info("Sending request to Gemini API...")
            response = requests.post(self.endpoint, headers=self.headers, json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                # Adjust according to actual Gemini API response structure
                ai_text = data.get("text") or data.get("output") or "No response returned"
                logging.info("Received response from Gemini API.")
                return ai_text
            else:
                logging.error(f"Gemini API returned status {response.status_code}: {response.text}")
                return f"Error: Gemini API returned status {response.status_code}"

        except requests.exceptions.Timeout:
            logging.error("Gemini API request timed out.")
            return "Error: Gemini API request timed out."
        except requests.exceptions.RequestException as e:
            logging.error(f"Gemini API request exception: {e}")
            return f"Error: Gemini API request failed. {e}"

    # -------------------------------
    # Optional: Chat-style conversation
    # -------------------------------
    def chat(self, messages: list) -> str:
        """
        Send conversation messages to Gemini API and receive response
        Args:
            messages (list): List of dicts [{"role": "user", "content": "Hi"}, ...]
        Returns:
            str: AI response
        """
        payload = {
            "messages": messages,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 500
        }

        try:
            logging.info("Sending chat messages to Gemini API...")
            response = requests.post(self.endpoint, headers=self.headers, json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                ai_text = data.get("text") or data.get("output") or "No response returned"
                logging.info("Received chat response from Gemini API.")
                return ai_text
            else:
                logging.error(f"Gemini API chat returned status {response.status_code}: {response.text}")
                return f"Error: Gemini API returned status {response.status_code}"

        except requests.exceptions.Timeout:
            logging.error("Gemini API chat request timed out.")
            return "Error: Gemini API request timed out."
        except requests.exceptions.RequestException as e:
            logging.error(f"Gemini API chat request exception: {e}")
            return f"Error: Gemini API request failed. {e}"
