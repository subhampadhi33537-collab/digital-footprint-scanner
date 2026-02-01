"""
Groq Client for Digital Footprint Scanner
---------------------------------------------------
Responsibilities:
- Handle all interactions with Groq API
- Send prompts, receive responses, and handle errors
- Provide unified interface for chatbot_handler.py or other AI modules
- Compatible with OpenAI-style API format
"""

import os
import json
import logging
import requests
from config import config

# -------------------------------
# Logging Setup
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [GROQ CLIENT] %(levelname)s: %(message)s"
)

# -------------------------------
# Groq Client Class
# -------------------------------
class GroqClient:
    def __init__(self, api_key: str = None):
        """
        Initialize Groq Client
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or getattr(config, "GROQ_API_KEY", None)
        if not self.api_key:
            logging.error("GROQ API KEY not provided. GroqClient will not work properly.")
        
        self.api_url = getattr(config, "GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
        self.model = getattr(config, "GROQ_MODEL", "llama-3.1-8b-instant")
        self.max_tokens = getattr(config, "GROQ_MAX_TOKENS", 1024)
        self.temperature = getattr(config, "GROQ_TEMPERATURE", 0.6)
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logging.info("GroqClient initialized successfully.")

    # -------------------------------
    # Generate AI Response
    # -------------------------------
    def generate_text(self, prompt: str, max_tokens: int = None) -> str:
        """
        Send a prompt to Groq API and return the response
        Args:
            prompt (str): Prompt text
            max_tokens (int): Maximum tokens to generate
        Returns:
            str: AI response
        """
        max_tokens = max_tokens or min(self.max_tokens, 512)  # Cap at 512 for speed
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": self.temperature,
        }

        try:
            logging.info("Sending request to Groq API...")
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=12  # Optimized for faster timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                # Groq uses OpenAI-style response format
                ai_text = data.get("choices", [{}])[0].get("message", {}).get("content", "No response returned")
                logging.info("Received response from Groq API.")
                return ai_text
            else:
                logging.error(f"Groq API returned status {response.status_code}: {response.text}")
                return f"Error: Groq API returned status {response.status_code}"

        except requests.exceptions.Timeout:
            logging.error("Groq API request timed out.")
            return "Error: Groq API request timed out."
        except requests.exceptions.RequestException as e:
            logging.error(f"Groq API request exception: {e}")
            return f"Error: Groq API request failed. {e}"

    # -------------------------------
    # Chat-style conversation
    # -------------------------------
    def chat(self, messages: list) -> str:
        """
        Send conversation messages to Groq API and receive response
        Args:
            messages (list): List of dicts [{"role": "user", "content": "Hi"}, ...]
        Returns:
            str: AI response
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": min(self.max_tokens, 512),  # Cap at 512 for speed
        }

        try:
            logging.info("Sending chat request to Groq API...")
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=12  # Optimized timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_text = data.get("choices", [{}])[0].get("message", {}).get("content", "No response returned")
                logging.info("Received chat response from Groq API.")
                return ai_text
            else:
                logging.error(f"Groq API returned status {response.status_code}: {response.text}")
                return f"Error: Groq API returned status {response.status_code}"

        except requests.exceptions.Timeout:
            logging.error("Groq API request timed out.")
            return "Error: Groq API request timed out."
        except requests.exceptions.RequestException as e:
            logging.error(f"Groq API request exception: {e}")
            return f"Error: Groq API request failed. {e}"


# Create a singleton instance
_groq_client = None

def get_groq_client():
    """Get or create the Groq client instance"""
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqClient()
    return _groq_client
